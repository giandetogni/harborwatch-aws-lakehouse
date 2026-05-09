import csv
from collections import defaultdict
from pathlib import Path


INPUT_PROXIMITY_PATH = Path(
    "data/processed/silver/silver_vessel_port_proximity_random_sample_500k.csv"
)
INPUT_STOPS_PATH = Path("data/processed/silver/silver_vessel_stops_random_sample_500k.csv")
INPUT_QUALITY_REPORT_PATH = Path(
    "data/processed/silver/silver_data_quality_report_random_sample_500k.csv"
)
INPUT_ANOMALIES_PATH = Path(
    "data/processed/gold/gold_vessel_anomalies_random_sample_500k.csv"
)
OUTPUT_PATH = Path("data/processed/gold/gold_port_congestion_daily_random_sample_500k.csv")


def percentile(values: list[float], percentile_rank: float) -> float:
    if not values:
        return 0.0

    values_sorted = sorted(values)
    index = (len(values_sorted) - 1) * percentile_rank
    lower_index = int(index)
    upper_index = min(lower_index + 1, len(values_sorted) - 1)

    if lower_index == upper_index:
        return values_sorted[lower_index]

    weight = index - lower_index

    return (
        values_sorted[lower_index] * (1 - weight)
        + values_sorted[upper_index] * weight
    )


def min_max_normalize(value: float, values: list[float]) -> float:
    if not values:
        return 0.0

    min_value = min(values)
    max_value = max(values)

    if max_value == min_value:
        return 0.0

    return (value - min_value) / (max_value - min_value)


def load_quality_rejection_rate(path: Path) -> float:
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        row = next(reader)

    return float(row["rejection_rate"])


def main() -> None:
    proximity_metrics = defaultdict(
        lambda: {
            "vessels_near_port": set(),
            "stopped_position_count": 0,
        }
    )

    port_names = {}

    with INPUT_PROXIMITY_PATH.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["is_within_port_radius"] != "True":
                continue

            date = row["event_timestamp"][:10]
            port_id = row["nearest_port_id"]
            port_name = row["nearest_port_name"]
            key = (date, port_id)

            port_names[port_id] = port_name
            proximity_metrics[key]["vessels_near_port"].add(row["mmsi"])

            if float(row["speed_knots"]) < 1.0:
                proximity_metrics[key]["stopped_position_count"] += 1

    stop_metrics = defaultdict(
        lambda: {
            "stopped_vessels": set(),
            "dwell_times": [],
        }
    )

    with INPUT_STOPS_PATH.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            date = row["stop_start_timestamp"][:10]
            port_id = row["port_id"]
            port_name = row["port_name"]
            key = (date, port_id)

            port_names[port_id] = port_name
            stop_metrics[key]["stopped_vessels"].add(row["mmsi"])
            stop_metrics[key]["dwell_times"].append(float(row["dwell_time_minutes"]))

    anomaly_metrics = defaultdict(int)

    with INPUT_ANOMALIES_PATH.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["is_within_port_radius"] != "True":
                continue

            date = row["event_timestamp"][:10]
            port_id = row["nearest_port_id"]
            port_name = row["nearest_port_name"]
            key = (date, port_id)

            port_names[port_id] = port_name
            anomaly_metrics[key] += 1

    data_quality_rejection_rate = load_quality_rejection_rate(INPUT_QUALITY_REPORT_PATH)

    all_keys = sorted(
        set(proximity_metrics.keys())
        | set(stop_metrics.keys())
        | set(anomaly_metrics.keys())
    )

    intermediate_rows = []

    for date, port_id in all_keys:
        vessels_near_port = len(proximity_metrics[(date, port_id)]["vessels_near_port"])
        stopped_position_count = proximity_metrics[(date, port_id)][
            "stopped_position_count"
        ]

        stopped_vessels = len(stop_metrics[(date, port_id)]["stopped_vessels"])
        dwell_times = stop_metrics[(date, port_id)]["dwell_times"]

        avg_dwell_time_minutes = (
            sum(dwell_times) / len(dwell_times) if dwell_times else 0.0
        )
        p90_dwell_time_minutes = percentile(dwell_times, 0.90)
        anomaly_count = anomaly_metrics[(date, port_id)]

        intermediate_rows.append(
            {
                "date": date,
                "port_id": port_id,
                "port_name": port_names.get(port_id, port_id),
                "vessels_near_port": vessels_near_port,
                "stopped_vessels": stopped_vessels,
                "avg_dwell_time_minutes": avg_dwell_time_minutes,
                "p90_dwell_time_minutes": p90_dwell_time_minutes,
                "stopped_position_count": stopped_position_count,
                "anomaly_count": anomaly_count,
                "data_quality_rejection_rate": data_quality_rejection_rate,
            }
        )

    stopped_vessels_values = [row["stopped_vessels"] for row in intermediate_rows]
    avg_dwell_values = [row["avg_dwell_time_minutes"] for row in intermediate_rows]
    stopped_position_values = [
        row["stopped_position_count"] for row in intermediate_rows
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output_fieldnames = [
        "date",
        "port_id",
        "port_name",
        "vessels_near_port",
        "stopped_vessels",
        "avg_dwell_time_minutes",
        "p90_dwell_time_minutes",
        "stopped_position_count",
        "anomaly_count",
        "data_quality_rejection_rate",
        "port_congestion_index",
    ]

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
        writer.writeheader()

        for row in intermediate_rows:
            normalized_waiting_vessels = min_max_normalize(
                row["stopped_vessels"], stopped_vessels_values
            )
            normalized_avg_dwell_time = min_max_normalize(
                row["avg_dwell_time_minutes"], avg_dwell_values
            )
            normalized_stopped_position_count = min_max_normalize(
                row["stopped_position_count"], stopped_position_values
            )

            port_congestion_index = (
                0.40 * normalized_waiting_vessels
                + 0.35 * normalized_avg_dwell_time
                + 0.25 * normalized_stopped_position_count
            )

            writer.writerow(
                {
                    "date": row["date"],
                    "port_id": row["port_id"],
                    "port_name": row["port_name"],
                    "vessels_near_port": row["vessels_near_port"],
                    "stopped_vessels": row["stopped_vessels"],
                    "avg_dwell_time_minutes": round(
                        row["avg_dwell_time_minutes"], 2
                    ),
                    "p90_dwell_time_minutes": round(
                        row["p90_dwell_time_minutes"], 2
                    ),
                    "stopped_position_count": row["stopped_position_count"],
                    "anomaly_count": row["anomaly_count"],
                    "data_quality_rejection_rate": row[
                        "data_quality_rejection_rate"
                    ],
                    "port_congestion_index": round(port_congestion_index, 4),
                }
            )

    print(f"Gold congestion file created: {OUTPUT_PATH}")
    print(f"Rows written: {len(intermediate_rows)}")


if __name__ == "__main__":
    main()