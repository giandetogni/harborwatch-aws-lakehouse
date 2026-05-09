from datetime import datetime, timezone
from typing import Optional


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
