import math
import sys

from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import broadcast, col, row_number, udf
from pyspark.sql.types import DoubleType
from pyspark.sql.window import Window


args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME", "INPUT_POSITIONS_PATH", "INPUT_PORTS_PATH", "OUTPUT_PATH"],
)

input_positions_path = args["INPUT_POSITIONS_PATH"]
input_ports_path = args["INPUT_PORTS_PATH"]
output_path = args["OUTPUT_PATH"]

EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None

    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


haversine_distance_udf = udf(haversine_distance_km, DoubleType())

sc = SparkContext()
glue_context = GlueContext(sc)
spark = glue_context.spark_session

positions_df = spark.read.parquet(input_positions_path)

ports_df = (
    spark.read.option("header", "true")
    .option("inferSchema", "true")
    .csv(input_ports_path)
    .select(
        col("port_id"),
        col("port_name"),
        col("latitude").alias("port_latitude"),
        col("longitude").alias("port_longitude"),
        col("port_radius_km"),
    )
)

valid_positions_df = positions_df.filter(col("quality_status") == "valid")

distance_df = (
    valid_positions_df.crossJoin(broadcast(ports_df))
    .withColumn(
        "distance_to_port_km",
        haversine_distance_udf(
            col("latitude"),
            col("longitude"),
            col("port_latitude"),
            col("port_longitude"),
        ),
    )
)

nearest_port_window = Window.partitionBy("message_id").orderBy(
    col("distance_to_port_km").asc()
)

proximity_df = (
    distance_df.withColumn("port_rank", row_number().over(nearest_port_window))
    .filter(col("port_rank") == 1)
    .drop("port_rank")
    .withColumnRenamed("port_id", "nearest_port_id")
    .withColumnRenamed("port_name", "nearest_port_name")
    .withColumn(
        "is_within_port_radius",
        col("distance_to_port_km") <= col("port_radius_km"),
    )
    .withColumn(
        "distance_to_port_km",
        col("distance_to_port_km").cast("double"),
    )
)

(
    proximity_df.write.mode("overwrite")
    .partitionBy("year", "month")
    .parquet(output_path)
)

total_rows = proximity_df.count()
within_radius_rows = proximity_df.filter(col("is_within_port_radius")).count()

print(f"Input positions path: {input_positions_path}")
print(f"Input ports path: {input_ports_path}")
print(f"Output path: {output_path}")
print(f"Rows written: {total_rows}")
print(f"Rows within port radius: {within_radius_rows}")