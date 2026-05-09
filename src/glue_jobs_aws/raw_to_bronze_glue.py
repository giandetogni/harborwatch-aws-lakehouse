import sys

from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import (
    coalesce,
    col,
    concat_ws,
    current_timestamp,
    input_file_name,
    lit,
    month,
    sha2,
    to_date,
    to_timestamp,
    year,
)
from pyspark.sql.types import DoubleType, IntegerType, StringType


args = getResolvedOptions(sys.argv, ["JOB_NAME", "INPUT_PATH", "OUTPUT_PATH"])

input_path = args["INPUT_PATH"]
output_path = args["OUTPUT_PATH"]

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

raw_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "false")
    .csv(input_path)
)

bronze_df = (
    raw_df
    .withColumn(
        "message_id",
        sha2(
            concat_ws(
                "|",
                coalesce(col("MMSI").cast(StringType()), lit("")),
                coalesce(col("BaseDateTime").cast(StringType()), lit("")),
                coalesce(col("LAT").cast(StringType()), lit("")),
                coalesce(col("LON").cast(StringType()), lit("")),
                coalesce(col("SOG").cast(StringType()), lit("")),
                coalesce(col("COG").cast(StringType()), lit("")),
            ),
            256,
        ),
    )
    .withColumn("source_file", input_file_name())
    .withColumn("ingestion_timestamp", current_timestamp())
    .withColumn("event_timestamp", to_timestamp(col("BaseDateTime")))
    .withColumn("mmsi", col("MMSI").cast(StringType()))
    .withColumn("latitude", col("LAT").cast(DoubleType()))
    .withColumn("longitude", col("LON").cast(DoubleType()))
    .withColumn("speed_knots", col("SOG").cast(DoubleType()))
    .withColumn("course", col("COG").cast(DoubleType()))
    .withColumn("heading", col("Heading").cast(DoubleType()))
    .withColumn("vessel_name", col("VesselName").cast(StringType()))
    .withColumn("imo", col("IMO").cast(StringType()))
    .withColumn("call_sign", col("CallSign").cast(StringType()))
    .withColumn("vessel_type", col("VesselType").cast(StringType()))
    .withColumn("navigation_status", col("Status").cast(StringType()))
    .withColumn("length", col("Length").cast(DoubleType()))
    .withColumn("width", col("Width").cast(DoubleType()))
    .withColumn("draft", col("Draft").cast(DoubleType()))
    .withColumn("cargo", col("Cargo").cast(StringType()))
    .withColumn("transceiver_class", col("TransceiverClass").cast(StringType()))
    .withColumn(
        "raw_payload_hash",
        sha2(
            concat_ws(
                "|",
                *[
                    coalesce(col(column_name).cast(StringType()), lit(""))
                    for column_name in raw_df.columns
                ],
            ),
            256,
        ),
    )
    .withColumn("event_date", to_date(col("event_timestamp")))
    .withColumn("year", year(col("event_timestamp")))
    .withColumn("month", month(col("event_timestamp")))
    .select(
        "message_id",
        "source_file",
        "ingestion_timestamp",
        "event_timestamp",
        "mmsi",
        "latitude",
        "longitude",
        "speed_knots",
        "course",
        "heading",
        "vessel_name",
        "imo",
        "call_sign",
        "vessel_type",
        "navigation_status",
        "length",
        "width",
        "draft",
        "cargo",
        "transceiver_class",
        "raw_payload_hash",
        "event_date",
        "year",
        "month",
    )
)

(
    bronze_df
    .write
    .mode("overwrite")
    .partitionBy("year", "month")
    .parquet(output_path)
)

print(f"Raw input path: {input_path}")
print(f"Bronze output path: {output_path}")
print(f"Rows written: {bronze_df.count()}")
