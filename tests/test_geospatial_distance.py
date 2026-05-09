from src.geospatial.distance import haversine_distance_km


def test_haversine_distance_same_point_returns_zero():
    distance = haversine_distance_km(0, 0, 0, 0)

    assert distance == 0


def test_haversine_distance_between_los_angeles_and_new_york_is_reasonable():
    distance = haversine_distance_km(34.0522, -118.2437, 40.7128, -74.0060)

    assert 3900 <= distance <= 4000
