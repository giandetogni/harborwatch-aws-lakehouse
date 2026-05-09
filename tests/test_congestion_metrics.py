from src.metrics.congestion import (
    calculate_port_congestion_index,
    min_max_normalize,
)


def test_min_max_normalize_returns_expected_value():
    value = min_max_normalize(50, [0, 50, 100])

    assert value == 0.5


def test_min_max_normalize_returns_zero_when_all_values_equal():
    value = min_max_normalize(10, [10, 10, 10])

    assert value == 0.0


def test_calculate_port_congestion_index_uses_expected_weights():
    score = calculate_port_congestion_index(
        normalized_stopped_vessels=1.0,
        normalized_avg_dwell_time=0.5,
        normalized_stopped_position_count=0.0,
    )

    assert score == 0.575
