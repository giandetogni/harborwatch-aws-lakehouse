import csv
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from typing import Optional


INPUT_POSITIONS_PATH = Path(
    "data/processed/silver/silver_vessel_positions_clean_random_sample_500k.csv"
)
INPUT_PORTS_PATH = Path("data/raw/harborwatch_ports_mvp.csv")
OUTPUT_PATH = Path(
    "data/processed/silver/silver_vessel_port_proximity_random_sample_500k.csv"
)

EARTH_RADIUS_KM = 6371.0


def is_blank(value: Optional[str]) -> bool:
    return value is None or value.strip() == ""


def to_float(value: Optional[str]) -> Optional[float]:
    if is_blank(value):
        return None

    try:
        return float(value)
    except ValueError:
        return None


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def load_ports(path: Path) -> list[dict]:
    ports = []

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            ports.append(
                {
                    "port_id": row["port_id"],
                    "port_name": row["port_name"],
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "port_radius_km": float(row["port_radius_km"]),
                }
            )

    return ports


def find_nearest_port(
    vessel_latitude: float,
    vessel_longitude: float,
    ports: list[dict],
) -> dict:
    nearest_port = None
    nearest_distance = None

    for port in ports:
        distance = haversine_distance_km(
            vessel_latitude,
            vessel_longitude,
            port["latitude"],
            port["longitude"],
        )

        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_port = port

    if nearest_port is None or nearest_distance is None:
        raise ValueError("No ports available to calculate nearest port.")

    return {
        "nearest_port_id": nearest_port["port_id"],
        "nearest_port_name": nearest_port["port_name"],
        "distance_to_port_km": nearest_distance,
        "port_radius_km": nearest_port["port_radius_km"],
        "is_within_port_radius": nearest_distance <= nearest_port["port_radius_km"],
    }


def main() -> None:
    ports = load_ports(INPUT_PORTS_PATH)

    total_rows_read = 0
    valid_rows_processed = 0
    rows_written = 0
    rows_skipped = 0
    rows_within_port_radius = 0

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
        "nearest_port_id",
        "nearest_port_name",
        "distance_to_port_km",
        "is_within_port_radius",
        "port_radius_km",
        "source_file",
        "ingestion_timestamp",
        "year",
        "month",
        "day",
    ]

    with INPUT_POSITIONS_PATH.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)

        with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                total_rows_read += 1

                if row.get("quality_status") != "valid":
                    continue

                valid_rows_processed += 1

                latitude = to_float(row.get("latitude"))
                longitude = to_float(row.get("longitude"))

                if latitude is None or longitude is None:
                    rows_skipped += 1
                    continue

                nearest_port = find_nearest_port(latitude, longitude, ports)

                if nearest_port["is_within_port_radius"]:
                    rows_within_port_radius += 1

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
                        "nearest_port_id": nearest_port["nearest_port_id"],
                        "nearest_port_name": nearest_port["nearest_port_name"],
                        "distance_to_port_km": round(
                            nearest_port["distance_to_port_km"], 3
                        ),
                        "is_within_port_radius": nearest_port[
                            "is_within_port_radius"
                        ],
                        "port_radius_km": nearest_port["port_radius_km"],
                        "source_file": row.get("source_file"),
                        "ingestion_timestamp": row.get("ingestion_timestamp"),
                        "year": row.get("year"),
                        "month": row.get("month"),
                        "day": row.get("day"),
                    }
                )

                rows_written += 1

    print(f"Port proximity file created: {OUTPUT_PATH}")
    print(f"Total rows read: {total_rows_read}")
    print(f"Valid rows processed: {valid_rows_processed}")
    print(f"Rows written: {rows_written}")
    print(f"Rows skipped: {rows_skipped}")
    print(f"Rows within port radius: {rows_within_port_radius}")


if __name__ == "__main__":
    main()
