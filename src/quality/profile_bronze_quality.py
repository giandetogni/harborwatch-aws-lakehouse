import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


DEFAULT_INPUT_PATH = Path("data/processed/bronze/bronze_ais_messages_quality_sample.csv")
DEFAULT_OUTPUT_PATH = Path("data/processed/silver/silver_data_quality_report_quality_sample.csv")

MAX_REASONABLE_SPEED_KNOTS = 60.0
AIS_SPEED_NOT_AVAILABLE_SENTINEL = 102.3


def is_blank(value: Optional[str]) -> bool:
    return value is None or value.strip() == ""


def to_float(value: Optional[str]) -> Optional[float]:
    if is_blank(value):
        return None

    try:
        return float(value)
    except ValueError:
        return None


def is_valid_latitude(value: Optional[str]) -> bool:
    latitude = to_float(value)

    return latitude is not None and -90 <= latitude <= 90


def is_valid_longitude(value: Optional[str]) -> bool:
    longitude = to_float(value)

    return longitude is not None and -180 <= longitude <= 180


def is_speed_not_available(value: Optional[str]) -> bool:
    speed = to_float(value)

    return speed == AIS_SPEED_NOT_AVAILABLE_SENTINEL


def is_impossible_speed(value: Optional[str]) -> bool:
    speed = to_float(value)

    if speed is None:
        return True

    if is_speed_not_available(value):
        return False

    return speed < 0 or speed > MAX_REASONABLE_SPEED_KNOTS


def is_future_timestamp(value: Optional[str]) -> bool:
    if is_blank(value):
        return True

    event_timestamp = datetime.fromisoformat(value)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    return event_timestamp > now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a data quality report from a Bronze AIS CSV table."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to the Bronze AIS CSV input file.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to the Silver data quality report CSV output file.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = args.input
    output_path = args.output

    total_records = 0
    valid_records = 0
    rejected_records = 0

    invalid_coordinates_count = 0
    null_vessel_id_count = 0
    duplicate_records_count = 0
    impossible_speed_count = 0
    unavailable_speed_count = 0
    future_timestamp_count = 0
    null_source_file_count = 0
    null_ingestion_timestamp_count = 0

    seen_message_ids = set()

    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            total_records += 1

            message_id = row.get("message_id")
            latitude = row.get("latitude")
            longitude = row.get("longitude")
            mmsi = row.get("mmsi")
            speed_knots = row.get("speed_knots")
            event_timestamp = row.get("event_timestamp")
            source_file = row.get("source_file")
            ingestion_timestamp = row.get("ingestion_timestamp")

            has_invalid_coordinate = (
                not is_valid_latitude(latitude)
                or not is_valid_longitude(longitude)
            )
            has_null_vessel_id = is_blank(mmsi)
            has_unavailable_speed = is_speed_not_available(speed_knots)
            has_impossible_speed = is_impossible_speed(speed_knots)
            has_future_timestamp = is_future_timestamp(event_timestamp)
            has_null_source_file = is_blank(source_file)
            has_null_ingestion_timestamp = is_blank(ingestion_timestamp)
            is_duplicate = message_id in seen_message_ids

            if has_invalid_coordinate:
                invalid_coordinates_count += 1

            if has_null_vessel_id:
                null_vessel_id_count += 1

            if has_unavailable_speed:
                unavailable_speed_count += 1

            if has_impossible_speed:
                impossible_speed_count += 1

            if has_future_timestamp:
                future_timestamp_count += 1

            if has_null_source_file:
                null_source_file_count += 1

            if has_null_ingestion_timestamp:
                null_ingestion_timestamp_count += 1

            if is_duplicate:
                duplicate_records_count += 1

            row_has_any_problem = (
                has_invalid_coordinate
                or has_null_vessel_id
                or has_unavailable_speed
                or has_impossible_speed
                or has_future_timestamp
                or has_null_source_file
                or has_null_ingestion_timestamp
                or is_duplicate
            )

            if row_has_any_problem:
                rejected_records += 1
            else:
                valid_records += 1

            seen_message_ids.add(message_id)

    rejection_rate = rejected_records / total_records if total_records else 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        fieldnames = [
            "processing_date",
            "source_file",
            "total_records",
            "valid_records",
            "rejected_records",
            "invalid_coordinates_count",
            "null_vessel_id_count",
            "duplicate_records_count",
            "impossible_speed_count",
            "unavailable_speed_count",
            "future_timestamp_count",
            "null_source_file_count",
            "null_ingestion_timestamp_count",
            "rejection_rate",
            "created_at",
        ]

        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        writer.writerow(
            {
                "processing_date": datetime.now(timezone.utc).date().isoformat(),
                "source_file": input_path.name,
                "total_records": total_records,
                "valid_records": valid_records,
                "rejected_records": rejected_records,
                "invalid_coordinates_count": invalid_coordinates_count,
                "null_vessel_id_count": null_vessel_id_count,
                "duplicate_records_count": duplicate_records_count,
                "impossible_speed_count": impossible_speed_count,
                "unavailable_speed_count": unavailable_speed_count,
                "future_timestamp_count": future_timestamp_count,
                "null_source_file_count": null_source_file_count,
                "null_ingestion_timestamp_count": null_ingestion_timestamp_count,
                "rejection_rate": round(rejection_rate, 6),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    print(f"Quality report created: {output_path}")
    print(f"Total records: {total_records}")
    print(f"Valid records: {valid_records}")
    print(f"Rejected records: {rejected_records}")
    print(f"Invalid coordinates: {invalid_coordinates_count}")
    print(f"Null vessel IDs: {null_vessel_id_count}")
    print(f"Duplicates: {duplicate_records_count}")
    print(f"Impossible speeds: {impossible_speed_count}")
    print(f"Unavailable speeds: {unavailable_speed_count}")
    print(f"Future timestamps: {future_timestamp_count}")
    print(f"Rejection rate: {rejection_rate:.4%}")


if __name__ == "__main__":
    main()