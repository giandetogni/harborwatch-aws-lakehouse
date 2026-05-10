import sys

from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql import Window
from pyspark.sql.functions import (
    avg,
    col,
    concat_ws,
    count,
    date_format,
    lag,
    max,
    min,
    sha2,
    sum as spark_sum,
    unix_timestamp,
    when,
    year,
    month,
)


args = getResolvedOptions(sys.argv, ["JOB_NAME", "INPUT_PATH", "OUTPUT_PATH"])

input_path = args["INPUT_PATH"]
output_path = args["OUTPUT_PATH"]

MAX_GAP_MINUTES = 60.0
MIN_DWELL_MINUTES = 30.0
STOPPED_SPEED_THRESHOLD_KNOTS = 1.0

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

proximity_df = spark.read.parquet(input_path)

candidate_stops_df = (
    proximity_df
    .filter(col("is_within_port_radius") == True)
    .filter(col("speed_knots") < STOPPED_SPEED_THRESHOLD_KNOTS)
    .filter(col("event_timestamp").isNotNull())
    .filter(col("mmsi").isNotNull())
    .filter(col("nearest_port_id").isNotNull())
)

position_window = Window.partitionBy("mmsi", "nearest_port_id").orderBy(
    col("event_timestamp").asc()
)

candidate_with_gaps_df = (
    candidate_stops_df
    .withColumn("previous_event_timestamp", lag("event_timestamp").over(position_window))
    .withColumn(
        "gap_minutes",
        (
            unix_timestamp(col("event_timestamp"))
            - unix_timestamp(col("previous_event_timestamp"))
        )
        / 60.0,
    )
    .withColumn(
        "is_new_stop_episode",
        when(col("previous_event_timestamp").isNull(), 1)
        .when(col("gap_minutes") > MAX_GAP_MINUTES, 1)
        .otherwise(0),
    )
)

episode_window = (
    Window.partitionBy("mmsi", "nearest_port_id")
    .orderBy(col("event_timestamp").asc())
    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
)

candidate_with_episode_df = candidate_with_gaps_df.withColumn(
    "stop_episode_number",
    spark_sum("is_new_stop_episode").over(episode_window),
)

stops_df = (
    candidate_with_episode_df
    .groupBy(
        "mmsi",
        "nearest_port_id",
        "nearest_port_name",
        "stop_episode_number",
    )
    .agg(
        min("event_timestamp").alias("stop_start_timestamp"),
        max("event_timestamp").alias("stop_end_timestamp"),
        avg("speed_knots").alias("avg_speed_knots"),
        count("*").alias("message_count"),
    )
    .withColumn(
        "dwell_time_minutes",
        (
            unix_timestamp(col("stop_end_timestamp"))
            - unix_timestamp(col("stop_start_timestamp"))
        )
        / 60.0,
    )
    .filter(col("dwell_time_minutes") >= MIN_DWELL_MINUTES)
    .withColumn(
        "stop_id",
        sha2(
            concat_ws(
                "|",
                col("mmsi"),
                col("nearest_port_id"),
                date_format(col("stop_start_timestamp"), "yyyyMMddHHmmss"),
            ),
            256,
        ),
    )
    .withColumn("stop_date", col("stop_start_timestamp").cast("date"))
    .withColumn("year", year(col("stop_start_timestamp")))
    .withColumn("month", month(col("stop_start_timestamp")))
    .select(
        "stop_id",
        "mmsi",
        "nearest_port_id",
        "nearest_port_name",
        "stop_start_timestamp",
        "stop_end_timestamp",
        "dwell_time_minutes",
        "avg_speed_knots",
        "message_count",
        "stop_date",
        "year",
        "month",
    )
)

(
    stops_df
    .write
    .mode("overwrite")
    .partitionBy("year", "month")
    .parquet(output_path)
)

candidate_rows = candidate_stops_df.count()
valid_stops = stops_df.count()

print(f"Input path: {input_path}")
print(f"Output path: {output_path}")
print(f"Candidate stopped position rows: {candidate_rows}")
print(f"Valid stops written: {valid_stops}")
print(f"Minimum dwell time minutes: {MIN_DWELL_MINUTES}")
print(f"Max gap minutes: {MAX_GAP_MINUTES}")