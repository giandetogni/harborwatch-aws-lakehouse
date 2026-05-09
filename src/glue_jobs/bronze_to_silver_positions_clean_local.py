import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


INPUT_PATH = Path("data/processed/bronze/bronze_ais_messages_random_sample_500k.csv")
OUTPUT_PATH = Path("data/processed/silver/silver_vessel_positions_clean_random_sample_500k.csv")

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


def is_speed_unavailable(value: Optional[str]) -> bool:
    speed = to_float(value)
    return speed == AIS_SPEED_NOT_AVAILABLE_SENTINEL


def is_impossible_speed(value: Optional[str]) -> bool:
    speed = to_float(value)

    if speed is None:
        return True

    if is_speed_unavailable(value):
        return False

    return speed < 0 or speed > MAX_REASONABLE_SPEED_KNOTS


def is_valid_speed(value: Optional[str]) -> bool:
    speed = to_float(value)

    if speed is None:
        return False

    if is_speed_unavailable(value):
        return False

    return 0 <= speed <= MAX_REASONABLE_SPEED_KNOTS


def is_future_timestamp(value: Optional[str]) -> bool:
    if is_blank(value):
        return True

    event_timestamp = datetime.fromisoformat(value)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    return event_timestamp > now


def build_rejection_reason(
    has_invalid_coordinate: bool,
    has_null_vessel_id: bool,
    has_unavailable_speed: bool,
    has_impossible_speed: bool,
    has_future_timestamp: bool,
    has_null_source_file: bool,
    has_null_ingestion_timestamp: bool,
    is_duplicate: bool,
) -> str:
    reasons = []

    if has_invalid_coordinate:
        reasons.append("invalid_coordinate")

    if has_null_vessel_id:
        reasons.append("null_vessel_id")

    if has_unavailable_speed:
        reasons.append("speed_not_available")

    if has_impossible_speed:
        reasons.append("impossible_speed")

    if has_future_timestamp:
        reasons.append("future_timestamp")

    if has_null_source_file:
        reasons.append("null_source_file")

    if has_null_ingestion_timestamp:
        reasons.append("null_ingestion_timestamp")

    if is_duplicate:
        reasons.append("duplicate_message_id")

    return "|".join(reasons)


def main() -> None:
    seen_message_ids = set()

    total_rows = 0
    valid_rows = 0
    rejected_rows = 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output_fieldnames = [
        "message_id",
        "event_timestamp",
        "mmsi",
        "latitude",
        "longitude",
        "speed_knots",
        "course",
        "heading",
        "vessel_name",
        "vessel_type",
        "navigation_status",
        "source_file",
        "ingestion_timestamp",
        "is_valid_coordinate",
        "is_valid_speed",
        "is_duplicate",
        "is_future_timestamp",
        "is_speed_unavailable",
        "is_impossible_speed",
        "quality_status",
        "rejection_reason",
        "year",
        "month",
        "day",
    ]

    with INPUT_PATH.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)

        with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                total_rows += 1

                message_id = row.get("message_id")

                has_invalid_coordinate = (
                    not is_valid_latitude(row.get("latitude"))
                    or not is_valid_longitude(row.get("longitude"))
                )
                has_null_vessel_id = is_blank(row.get("mmsi"))
                has_unavailable_speed = is_speed_unavailable(row.get("speed_knots"))
                has_impossible_speed = is_impossible_speed(row.get("speed_knots"))
                has_future_timestamp = is_future_timestamp(row.get("event_timestamp"))
                has_null_source_file = is_blank(row.get("source_file"))
                has_null_ingestion_timestamp = is_blank(row.get("ingestion_timestamp"))
                is_duplicate = message_id in seen_message_ids

                rejection_reason = build_rejection_reason(
                    has_invalid_coordinate=has_invalid_coordinate,
                    has_null_vessel_id=has_null_vessel_id,
                    has_unavailable_speed=has_unavailable_speed,
                    has_impossible_speed=has_impossible_speed,
                    has_future_timestamp=has_future_timestamp,
                    has_null_source_file=has_null_source_file,
                    has_null_ingestion_timestamp=has_null_ingestion_timestamp,
                    is_duplicate=is_duplicate,
                )

                quality_status = "rejected" if rejection_reason else "valid"

                if quality_status == "valid":
                    valid_rows += 1
                else:
                    rejected_rows += 1

                writer.writerow(
                    {
                        "message_id": row.get("message_id"),
                        "event_timestamp": row.get("event_timestamp"),
                        "mmsi": row.get("mmsi"),
                        "latitude": row.get("latitude"),
                        "longitude": row.get("longitude"),
                        "speed_knots": row.get("speed_knots"),
                        "course": row.get("course"),
                        "heading": row.get("heading"),
                        "vessel_name": row.get("vessel_name"),
                        "vessel_type": row.get("vessel_type"),
                        "navigation_status": row.get("navigation_status"),
                        "source_file": row.get("source_file"),
                        "ingestion_timestamp": row.get("ingestion_timestamp"),
                        "is_valid_coordinate": not has_invalid_coordinate,
                        "is_valid_speed": is_valid_speed(row.get("speed_knots")),
                        "is_duplicate": is_duplicate,
                        "is_future_timestamp": has_future_timestamp,
                        "is_speed_unavailable": has_unavailable_speed,
                        "is_impossible_speed": has_impossible_speed,
                        "quality_status": quality_status,
                        "rejection_reason": rejection_reason,
                        "year": row.get("year"),
                        "month": row.get("month"),
                        "day": row.get("day"),
                    }
                )

                seen_message_ids.add(message_id)

    print(f"Silver clean file created: {OUTPUT_PATH}")
    print(f"Total rows: {total_rows}")
    print(f"Valid rows: {valid_rows}")
    print(f"Rejected rows: {rejected_rows}")


if __name__ == "__main__":
    main()
