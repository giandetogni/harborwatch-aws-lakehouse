import csv
import hashlib
from datetime import datetime, timezone
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path
from typing import Optional


INPUT_POSITIONS_PATH = Path(
    "data/processed/silver/silver_vessel_positions_clean_random_sample_500k.csv"
)
INPUT_PORTS_PATH = Path("data/raw/harborwatch_ports_mvp.csv")
OUTPUT_PATH = Path(
    "data/processed/gold/gold_vessel_anomalies_random_sample_500k.csv"
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
        return {
            "nearest_port_id": "",
            "nearest_port_name": "",
            "distance_to_port_km": "",
            "is_within_port_radius": False,
            "port_radius_km": "",
        }

    return {
        "nearest_port_id": nearest_port["port_id"],
        "nearest_port_name": nearest_port["port_name"],
        "distance_to_port_km": round(nearest_distance, 3),
        "is_within_port_radius": nearest_distance <= nearest_port["port_radius_km"],
        "port_radius_km": nearest_port["port_radius_km"],
    }


def generate_anomaly_id(source_message_id: str, anomaly_type: str) -> str:
    raw_key = f"{source_message_id}|{anomaly_type}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def classify_severity(anomaly_type: str) -> str:
    if anomaly_type in {"invalid_coordinate", "future_timestamp", "null_vessel_id"}:
        return "high"

    if anomaly_type in {"impossible_speed", "duplicate_message_id"}:
        return "medium"

    if anomaly_type == "speed_not_available":
        return "low"

    return "unknown"


def build_description(anomaly_type: str) -> str:
    descriptions = {
        "invalid_coordinate": "Position contains latitude or longitude outside valid geographic bounds.",
        "null_vessel_id": "AIS message does not contain a valid vessel identifier.",
        "speed_not_available": "AIS speed value uses the 102.3 sentinel for unavailable speed.",
        "impossible_speed": "AIS speed is outside the configured reasonable speed threshold.",
        "future_timestamp": "AIS event timestamp is later than processing time.",
        "duplicate_message_id": "AIS message has a duplicate deterministic message identifier.",
    }

    return descriptions.get(anomaly_type, "Unclassified data quality anomaly.")


def split_rejection_reasons(rejection_reason: str) -> list[str]:
    if not rejection_reason:
        return []

    return [reason for reason in rejection_reason.split("|") if reason]


def main() -> None:
    ports = load_ports(INPUT_PORTS_PATH)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    output_fieldnames = [
        "anomaly_id",
        "event_timestamp",
        "mmsi",
        "nearest_port_id",
        "nearest_port_name",
        "distance_to_port_km",
        "is_within_port_radius",
        "port_radius_km",
        "anomaly_type",
        "severity",
        "description",
        "source_message_id",
        "created_at",
    ]

    rows_read = 0
    anomalies_written = 0
    anomalies_with_coordinates = 0
    anomalies_within_port_radius = 0
    created_at = datetime.now(timezone.utc).isoformat()

    with INPUT_POSITIONS_PATH.open("r", encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)

        with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=output_fieldnames)
            writer.writeheader()

            for row in reader:
                rows_read += 1

                if row.get("quality_status") != "rejected":
                    continue

                latitude = to_float(row.get("latitude"))
                longitude = to_float(row.get("longitude"))

                if latitude is not None and longitude is not None:
                    nearest_port = find_nearest_port(latitude, longitude, ports)
                    anomalies_with_coordinates += 1

                    if nearest_port["is_within_port_radius"]:
                        anomalies_within_port_radius += 1
                else:
                    nearest_port = {
                        "nearest_port_id": "",
                        "nearest_port_name": "",
                        "distance_to_port_km": "",
                        "is_within_port_radius": False,
                        "port_radius_km": "",
                    }

                source_message_id = row["message_id"]
                rejection_reasons = split_rejection_reasons(
                    row.get("rejection_reason", "")
                )

                for anomaly_type in rejection_reasons:
                    writer.writerow(
                        {
                            "anomaly_id": generate_anomaly_id(
                                source_message_id,
                                anomaly_type,
                            ),
                            "event_timestamp": row.get("event_timestamp"),
                            "mmsi": row.get("mmsi"),
                            "nearest_port_id": nearest_port["nearest_port_id"],
                            "nearest_port_name": nearest_port["nearest_port_name"],
                            "distance_to_port_km": nearest_port["distance_to_port_km"],
                            "is_within_port_radius": nearest_port[
                                "is_within_port_radius"
                            ],
                            "port_radius_km": nearest_port["port_radius_km"],
                            "anomaly_type": anomaly_type,
                            "severity": classify_severity(anomaly_type),
                            "description": build_description(anomaly_type),
                            "source_message_id": source_message_id,
                            "created_at": created_at,
                        }
                    )

                    anomalies_written += 1

    print(f"Gold vessel anomalies file created: {OUTPUT_PATH}")
    print(f"Rows read: {rows_read}")
    print(f"Anomalies written: {anomalies_written}")
    print(f"Anomalies with coordinates: {anomalies_with_coordinates}")
    print(f"Anomalies within port radius: {anomalies_within_port_radius}")


if __name__ == "__main__":
    main()
