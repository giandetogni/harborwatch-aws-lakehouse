import sys

from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import Window
from pyspark.sql.functions import (
    col,
    concat_ws,
    count,
    current_timestamp,
    lit,
    trim,
    when,
)


args = getResolvedOptions(sys.argv, ["JOB_NAME", "INPUT_PATH", "OUTPUT_PATH"])

input_path = args["INPUT_PATH"]
output_path = args["OUTPUT_PATH"]

MAX_REASONABLE_SPEED_KNOTS = 60.0
AIS_SPEED_NOT_AVAILABLE_SENTINEL = 102.3

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

bronze_df = spark.read.parquet(input_path)

window_by_message_id = Window.partitionBy("message_id")

silver_df = (
    bronze_df
    .withColumn(
        "is_valid_coordinate",
        col("latitude").between(-90, 90) & col("longitude").between(-180, 180),
    )
    .withColumn(
        "is_null_vessel_id",
        col("mmsi").isNull() | (trim(col("mmsi")) == ""),
    )
    .withColumn(
        "is_speed_unavailable",
        col("speed_knots") == lit(AIS_SPEED_NOT_AVAILABLE_SENTINEL),
    )
    .withColumn(
        "is_impossible_speed",
        col("speed_knots").isNull()
        | (col("speed_knots") < 0)
        | (
            (col("speed_knots") > lit(MAX_REASONABLE_SPEED_KNOTS))
            & (col("speed_knots") != lit(AIS_SPEED_NOT_AVAILABLE_SENTINEL))
        ),
    )
    .withColumn(
        "is_valid_speed",
        col("speed_knots").isNotNull()
        & (col("speed_knots") >= 0)
        & (col("speed_knots") <= lit(MAX_REASONABLE_SPEED_KNOTS))
        & (col("speed_knots") != lit(AIS_SPEED_NOT_AVAILABLE_SENTINEL)),
    )
    .withColumn(
        "is_future_timestamp",
        col("event_timestamp") > current_timestamp(),
    )
    .withColumn(
        "duplicate_message_count",
        count("*").over(window_by_message_id),
    )
    .withColumn(
        "is_duplicate",
        col("duplicate_message_count") > 1,
    )
    .withColumn(
        "rejection_reason",
        concat_ws(
            "|",
            when(~col("is_valid_coordinate"), lit("invalid_coordinate")),
            when(col("is_null_vessel_id"), lit("null_vessel_id")),
            when(col("is_speed_unavailable"), lit("speed_not_available")),
            when(col("is_impossible_speed"), lit("impossible_speed")),
            when(col("is_future_timestamp"), lit("future_timestamp")),
            when(col("is_duplicate"), lit("duplicate_message_id")),
        ),
    )
    .withColumn(
        "quality_status",
        when(col("rejection_reason") == "", lit("valid")).otherwise(lit("rejected")),
    )
    .drop("duplicate_message_count")
)

(
    silver_df
    .write
    .mode("overwrite")
    .partitionBy("year", "month")
    .parquet(output_path)
)

total_rows = silver_df.count()
valid_rows = silver_df.filter(col("quality_status") == "valid").count()
rejected_rows = silver_df.filter(col("quality_status") == "rejected").count()

print(f"Bronze input path: {input_path}")
print(f"Silver output path: {output_path}")
print(f"Total rows: {total_rows}")
print(f"Valid rows: {valid_rows}")
print(f"Rejected rows: {rejected_rows}")
