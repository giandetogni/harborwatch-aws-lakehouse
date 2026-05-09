import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


INPUT_PATH = Path(
    "data/processed/silver/silver_vessel_port_proximity_random_sample_500k.csv"
)
OUTPUT_PATH = Path("data/processed/silver/silver_vessel_stops_random_sample_500k.csv")

STOP_SPEED_THRESHOLD_KNOTS = 1.0
MIN_STOP_DURATION_MINUTES = 30.0
MAX_GAP_BETWEEN_STOP_MESSAGES_MINUTES = 60.0


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)


def to_float(value: str) -> float:
    return float(value)


def build_stop_id(
    mmsi: str,
    port_id: str,
    stop_start_timestamp: datetime,
    sequence_number: int,
) -> str:
    safe_timestamp = stop_start_timestamp.isoformat().replace(":", "").replace("-", "")
    return f"{mmsi}_{port_id}_{safe_timestamp}_{sequence_number}"


def write_stop_if_valid(
    writer: csv.DictWriter,
    rows: list[dict],
    sequence_number: int,
) -> bool:
    if not rows:
        return False

    stop_start = parse_timestamp(rows[0]["event_timestamp"])
    stop_end = parse_timestamp(rows[-1]["event_timestamp"])
    dwell_time_minutes = (stop_end - stop_start).total_seconds() / 60

    if dwell_time_minutes < MIN_STOP_DURATION_MINUTES:
        return False

    speeds = [to_float(row["speed_knots"]) for row in rows]
    avg_speed_knots = sum(speeds) / len(speeds)

    mmsi = rows[0]["mmsi"]
    port_id = rows[0]["nearest_port_id"]

    writer.writerow(
        {
            "stop_id": build_stop_id(mmsi, port_id, stop_start, sequence_number),
            "mmsi": mmsi,
            "port_id": port_id,
            "port_name": rows[0]["nearest_port_name"],
            "stop_start_timestamp": stop_start.isoformat(),
            "stop_end_timestamp": stop_end.isoformat(),
            "dwell_time_minutes": round(dwell_time_minutes, 2),
            "avg_speed_knots": round(avg_speed_knots, 3),
            "message_count": len(rows),
            "is_valid_stop": True,
        }
    )

    return True


def main() -> None:
    candidates_by_vessel_port = defaultdict(list)

    total_rows_read = 0
    candidate_rows = 0

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            total_rows_read += 1

            is_within_port_radius = row.get("is_within_port_radius") == "True"
            speed_knots = to_float(row["speed_knots"])

            if not is_within_port_radius:
                continue

            if speed_knots >= STOP_SPEED_THRESHOLD_KNOTS:
                continue

            candidate_rows += 1

            key = (row["mmsi"], row["nearest_port_id"])
            candidates_by_vessel_port[key].append(row)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output_fieldnames = [
        "stop_id",
        "mmsi",
        "port_id",
        "port_name",
        "stop_start_timestamp",
        "stop_end_timestamp",
        "dwell_time_minutes",
        "avg_speed_knots",
        "message_count",
        "is_valid_stop",
    ]

    stops_written = 0

    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
        writer.writeheader()

        for (_mmsi, _port_id), rows in candidates_by_vessel_port.items():
            rows_sorted = sorted(rows, key=lambda item: item["event_timestamp"])

            current_episode = []
            sequence_number = 1

            for row in rows_sorted:
                if not current_episode:
                    current_episode.append(row)
                    continue

                previous_timestamp = parse_timestamp(
                    current_episode[-1]["event_timestamp"]
                )
                current_timestamp = parse_timestamp(row["event_timestamp"])

                gap_minutes = (
                    current_timestamp - previous_timestamp
                ).total_seconds() / 60

                if gap_minutes > MAX_GAP_BETWEEN_STOP_MESSAGES_MINUTES:
                    was_written = write_stop_if_valid(
                        writer,
                        current_episode,
                        sequence_number,
                    )

                    if was_written:
                        stops_written += 1
                        sequence_number += 1

                    current_episode = [row]
                else:
                    current_episode.append(row)

            was_written = write_stop_if_valid(
                writer,
                current_episode,
                sequence_number,
            )

            if was_written:
                stops_written += 1

    print(f"Vessel stops file created: {OUTPUT_PATH}")
    print(f"Total rows read: {total_rows_read}")
    print(f"Candidate stopped position rows: {candidate_rows}")
    print(f"Valid stops written: {stops_written}")
    print(
        "Max gap between messages in same stop episode: "
        f"{MAX_GAP_BETWEEN_STOP_MESSAGES_MINUTES} minutes"
    )


if __name__ == "__main__":
    main()