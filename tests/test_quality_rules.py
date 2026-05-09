from src.quality.rules import (
    is_impossible_speed,
    is_speed_unavailable,
    is_valid_latitude,
    is_valid_longitude,
    is_valid_speed,
)


def test_valid_latitude_accepts_valid_range():
    assert is_valid_latitude("0")
    assert is_valid_latitude("90")
    assert is_valid_latitude("-90")


def test_valid_latitude_rejects_invalid_range():
    assert not is_valid_latitude("91")
    assert not is_valid_latitude("-91")
    assert not is_valid_latitude("")


def test_valid_longitude_accepts_valid_range():
    assert is_valid_longitude("0")
    assert is_valid_longitude("180")
    assert is_valid_longitude("-180")


def test_valid_longitude_rejects_invalid_range():
    assert not is_valid_longitude("181")
    assert not is_valid_longitude("-181")
    assert not is_valid_longitude("")


def test_speed_102_3_is_unavailable_not_impossible():
    assert is_speed_unavailable("102.3")
    assert not is_valid_speed("102.3")
    assert not is_impossible_speed("102.3")


def test_negative_speed_is_impossible():
    assert is_impossible_speed("-1")
    assert not is_valid_speed("-1")


def test_reasonable_speed_is_valid():
    assert is_valid_speed("12.5")
    assert not is_impossible_speed("12.5")
