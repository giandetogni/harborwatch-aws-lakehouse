import csv
import hashlib
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


ZIP_PATH = Path("data/raw/public_ais/AIS_2024_01_01.zip")
ZIP_MEMBER = "AIS_2024_01_01.csv"

QUALITY_SAMPLE_PATH = Path("data/raw/public_ais/AIS_2024_01_01_quality_sample_50k.csv")
PROFILE_OUTPUT_PATH = Path("data/profiling/AIS_2024_01_01_quality_profile.csv")
ANOMALY_ROWS_PATH = Path("data/profiling/AIS_2024_01_01_anomaly_rows.csv")
SQLITE_PATH = Path("data/profiling/message_ids.sqlite")

MAX_SAMPLE_ROWS = 50_000
MAX_ANOMALY_ROWS_IN_SAMPLE = 10_000
MAX_REASONABLE_SPEED_KNOTS = 60.0


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


def is_valid_speed(value: Optional[str]) -> bool:
    speed = to_float(value)
    return speed is not None and 0 <= speed <= MAX_REASONABLE_SPEED_KNOTS


def is_future_timestamp(value: Optional[str]) -> bool:
    if is_blank(value):
        return True

    event_timestamp = datetime.fromisoformat(value)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    return event_timestamp > now


def generate_message_id(row: dict) -> str:
    key = "|".join(
        [
            row.get("MMSI", ""),
            row.get("BaseDateTime", ""),
            row.get("LAT", ""),
            row.get("LON", ""),
            row.get("SOG", ""),
            row.get("COG", ""),
        ]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def get_quality_reasons(row: dict, is_duplicate: bool) -> list[str]:
    reasons = []

    if not is_valid_latitude(row.get("LAT")) or not is_valid_longitude(row.get("LON")):
        reasons.append("invalid_coordinate")

    if is_blank(row.get("MMSI")):
        reasons.append("null_vessel_id")

    if not is_valid_speed(row.get("SOG")):
        reasons.append("invalid_speed")

    if is_future_timestamp(row.get("BaseDateTime")):
        reasons.append("future_timestamp")

    if is_duplicate:
        reasons.append("duplicate_message_id")

    return reasons


def setup_duplicate_store() -> sqlite3.Connection:
    if SQLITE_PATH.exists():
        SQLITE_PATH.unlink()

    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(SQLITE_PATH)
    connection.execute("CREATE TABLE message_ids (message_id TEXT PRIMARY KEY)")
    return connection


def check_and_store_duplicate(connection: sqlite3.Connection, message_id: str) -> bool:
    try:
        connection.execute(
            "INSERT INTO message_ids (message_id) VALUES (?)",
            (message_id,),
        )
        return False
    except sqlite3.IntegrityError:
        return True


def main() -> None:
    total_records = 0
    valid_records = 0
    rejected_records = 0

    invalid_coordinates_count = 0
    null_vessel_id_count = 0
    duplicate_records_count = 0
    impossible_speed_count = 0
    future_timestamp_count = 0

    anomaly_rows = []
    valid_sample_rows = []

    connection = setup_duplicate_store()

    with zipfile.ZipFile(ZIP_PATH) as zip_file:
        with zip_file.open(ZIP_MEMBER, "r") as compressed_file:
            text_file = (line.decode("utf-8") for line in compressed_file)
            reader = csv.DictReader(text_file)

            fieldnames = reader.fieldnames

            if fieldnames is None:
                raise ValueError("CSV header not found.")

            for row in reader:
                total_records += 1

                message_id = generate_message_id(row)
                is_duplicate = check_and_store_duplicate(connection, message_id)
                reasons = get_quality_reasons(row, is_duplicate)

                has_invalid_coordinate = "invalid_coordinate" in reasons
                has_null_vessel_id = "null_vessel_id" in reasons
                has_invalid_speed = "invalid_speed" in reasons
                has_future_timestamp = "future_timestamp" in reasons

                if has_invalid_coordinate:
                    invalid_coordinates_count += 1

                if has_null_vessel_id:
                    null_vessel_id_count += 1

                if has_invalid_speed:
                    impossible_speed_count += 1

                if has_future_timestamp:
                    future_timestamp_count += 1

                if is_duplicate:
                    duplicate_records_count += 1

                if reasons:
                    rejected_records += 1

                    if len(anomaly_rows) < MAX_ANOMALY_ROWS_IN_SAMPLE:
                        row_with_reason = dict(row)
                        row_with_reason["quality_reasons"] = "|".join(reasons)
                        anomaly_rows.append(row_with_reason)
                else:
                    valid_records += 1

                    if len(valid_sample_rows) < MAX_SAMPLE_ROWS:
                        valid_sample_rows.append(dict(row))

                if total_records % 500_000 == 0:
                    print(f"Rows scanned: {total_records}")

    connection.commit()
    connection.close()

    sample_rows = []

    raw_anomaly_rows = [
        {key: value for key, value in row.items() if key != "quality_reasons"}
        for row in anomaly_rows
    ]

    sample_rows.extend(raw_anomaly_rows)

    remaining_slots = MAX_SAMPLE_ROWS - len(sample_rows)
    sample_rows.extend(valid_sample_rows[:remaining_slots])

    QUALITY_SAMPLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    original_fieldnames = [
        "MMSI",
        "BaseDateTime",
        "LAT",
        "LON",
        "SOG",
        "COG",
        "Heading",
        "VesselName",
        "IMO",
        "CallSign",
        "VesselType",
        "Status",
        "Length",
        "Width",
        "Draft",
        "Cargo",
        "TransceiverClass",
    ]

    with QUALITY_SAMPLE_PATH.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=original_fieldnames)
        writer.writeheader()
        writer.writerows(sample_rows)

    anomaly_fieldnames = original_fieldnames + ["quality_reasons"]

    with ANOMALY_ROWS_PATH.open("w", encoding="utf-8", newline="") as anomaly_file:
        writer = csv.DictWriter(anomaly_file, fieldnames=anomaly_fieldnames)
        writer.writeheader()
        writer.writerows(anomaly_rows)

    rejection_rate = rejected_records / total_records if total_records else 0

    with PROFILE_OUTPUT_PATH.open("w", encoding="utf-8", newline="") as profile_file:
        fieldnames = [
            "source_file",
            "total_records",
            "valid_records",
            "rejected_records",
            "invalid_coordinates_count",
            "null_vessel_id_count",
            "duplicate_records_count",
            "impossible_speed_count",
            "future_timestamp_count",
            "rejection_rate",
            "quality_sample_rows",
            "anomaly_rows_captured",
            "created_at",
        ]

        writer = csv.DictWriter(profile_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "source_file": ZIP_PATH.name,
                "total_records": total_records,
                "valid_records": valid_records,
                "rejected_records": rejected_records,
                "invalid_coordinates_count": invalid_coordinates_count,
                "null_vessel_id_count": null_vessel_id_count,
                "duplicate_records_count": duplicate_records_count,
                "impossible_speed_count": impossible_speed_count,
                "future_timestamp_count": future_timestamp_count,
                "rejection_rate": round(rejection_rate, 6),
                "quality_sample_rows": len(sample_rows),
                "anomaly_rows_captured": len(anomaly_rows),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    print(f"Full file scanned: {ZIP_PATH}")
    print(f"Total records: {total_records}")
    print(f"Rejected records: {rejected_records}")
    print(f"Rejection rate: {rejection_rate:.4%}")
    print(f"Quality-focused sample created: {QUALITY_SAMPLE_PATH}")
    print(f"Anomaly rows report created: {ANOMALY_ROWS_PATH}")
    print(f"Quality profile created: {PROFILE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
