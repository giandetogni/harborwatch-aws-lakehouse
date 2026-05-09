import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_INPUT_PATH = Path("data/raw/public_ais/AIS_2024_01_01_quality_sample_50k.csv")
DEFAULT_OUTPUT_PATH = Path("data/processed/bronze/bronze_ais_messages_quality_sample.csv")


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


def generate_raw_payload_hash(row: dict) -> str:
    raw_values = "|".join(str(value) for value in row.values())

    return hashlib.sha256(raw_values.encode("utf-8")).hexdigest()


def parse_date_parts(timestamp: str) -> tuple[str, str, str]:
    event_datetime = datetime.fromisoformat(timestamp)

    return (
        str(event_datetime.year),
        str(event_datetime.month).zfill(2),
        str(event_datetime.day).zfill(2),
    )


def transform_row(row: dict, source_file: str, ingestion_timestamp: str) -> dict:
    year, month, day = parse_date_parts(row["BaseDateTime"])

    return {
        "message_id": generate_message_id(row),
        "source_file": source_file,
        "ingestion_timestamp": ingestion_timestamp,
        "event_timestamp": row.get("BaseDateTime"),
        "mmsi": row.get("MMSI"),
        "latitude": row.get("LAT"),
        "longitude": row.get("LON"),
        "speed_knots": row.get("SOG"),
        "course": row.get("COG"),
        "heading": row.get("Heading"),
        "vessel_name": row.get("VesselName"),
        "imo": row.get("IMO"),
        "call_sign": row.get("CallSign"),
        "vessel_type": row.get("VesselType"),
        "navigation_status": row.get("Status"),
        "length": row.get("Length"),
        "width": row.get("Width"),
        "draft": row.get("Draft"),
        "cargo": row.get("Cargo"),
        "transceiver_class": row.get("TransceiverClass"),
        "raw_payload_hash": generate_raw_payload_hash(row),
        "year": year,
        "month": month,
        "day": day,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transform raw AIS CSV data into a standardized Bronze CSV table."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to the raw AIS CSV input file.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to the Bronze CSV output file.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = args.input
    output_path = args.output

    source_file = input_path.name
    ingestion_timestamp = datetime.now(timezone.utc).isoformat()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_fieldnames = [
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
        "year",
        "month",
        "day",
    ]

    rows_written = 0

    with input_path.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)

        with output_path.open("w", encoding="utf-8", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                bronze_row = transform_row(row, source_file, ingestion_timestamp)
                writer.writerow(bronze_row)
                rows_written += 1

    print(f"Bronze file created: {output_path}")
    print(f"Rows written: {rows_written}")


if __name__ == "__main__":
    main()
