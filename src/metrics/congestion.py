def min_max_normalize(value: float, values: list[float]) -> float:
    if not values:
        return 0.0

    min_value = min(values)
    max_value = max(values)

    if max_value == min_value:
        return 0.0

    return (value - min_value) / (max_value - min_value)


def calculate_port_congestion_index(
    normalized_stopped_vessels: float,
    normalized_avg_dwell_time: float,
    normalized_stopped_position_count: float,
) -> float:
    return (
        0.40 * normalized_stopped_vessels
        + 0.35 * normalized_avg_dwell_time
        + 0.25 * normalized_stopped_position_count
    )
