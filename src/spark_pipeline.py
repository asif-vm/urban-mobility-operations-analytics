from __future__ import annotations

import argparse
from pathlib import Path

from pyspark.sql import SparkSession, functions as F, types as T


SCHEMA = T.StructType(
    [
        T.StructField("trip_id", T.StringType(), False),
        T.StructField("event_ts", T.TimestampType(), False),
        T.StructField("service_date", T.DateType(), False),
        T.StructField("route_name", T.StringType(), False),
        T.StructField("vehicle_id", T.StringType(), False),
        T.StructField("scheduled_minutes", T.IntegerType(), False),
        T.StructField("actual_minutes", T.DoubleType(), False),
        T.StructField("delay_minutes", T.DoubleType(), False),
        T.StructField("passengers", T.IntegerType(), False),
        T.StructField("capacity", T.IntegerType(), False),
        T.StructField("weather", T.StringType(), False),
        T.StructField("cancelled", T.BooleanType(), False),
    ]
)


def run(input_path: Path, output_root: Path) -> None:
    spark = SparkSession.builder.appName("urban-mobility-operations").getOrCreate()
    raw = spark.read.option("header", True).schema(SCHEMA).csv(str(input_path))
    duplicate_ids = raw.groupBy("trip_id").count().filter("count > 1").count()
    invalid = raw.filter((F.col("passengers") > F.col("capacity")) | F.col("trip_id").isNull()).count()
    if duplicate_ids or invalid:
        raise ValueError(f"Data contract failed: duplicates={duplicate_ids}, invalid={invalid}")

    silver = (
        raw.withColumn("occupancy_rate", F.col("passengers") / F.col("capacity"))
        .withColumn("on_time_flag", ((F.col("delay_minutes") <= 5) & ~F.col("cancelled")).cast("int"))
        .repartition("service_date")
    )
    gold = (
        silver.groupBy("service_date", "route_name")
        .agg(
            F.count("*").alias("scheduled_trips"),
            F.sum(F.col("cancelled").cast("int")).alias("cancelled_trips"),
            F.round(F.avg("delay_minutes"), 2).alias("average_delay_minutes"),
            F.round(100 * F.avg("on_time_flag"), 2).alias("on_time_pct"),
            F.sum("passengers").alias("passengers"),
            F.round(100 * F.avg("occupancy_rate"), 2).alias("average_occupancy_pct"),
        )
        .orderBy("service_date", "route_name")
    )
    silver.write.mode("overwrite").partitionBy("service_date").parquet(str(output_root / "silver_trips"))
    gold.write.mode("overwrite").parquet(str(output_root / "gold_route_daily"))
    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/raw/trips.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed"))
    args = parser.parse_args()
    run(args.input, args.output)

