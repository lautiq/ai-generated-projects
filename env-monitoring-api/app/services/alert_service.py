from typing import Literal

AlertStatus = Literal["green", "yellow", "red", "unknown"]


def compute_status(measurement, threshold) -> AlertStatus:
    if measurement is None or threshold is None:
        return "unknown"

    temp = measurement.temperature
    humidity = measurement.humidity

    # Red: out of bounds
    if temp < threshold.temp_min or temp > threshold.temp_max:
        return "red"
    if humidity < threshold.humidity_min or humidity > threshold.humidity_max:
        return "red"

    # Yellow: within 10% of range from any limit
    temp_margin = (threshold.temp_max - threshold.temp_min) * 0.10
    humidity_margin = (threshold.humidity_max - threshold.humidity_min) * 0.10

    temp_yellow = (
        temp <= threshold.temp_min + temp_margin or
        temp >= threshold.temp_max - temp_margin
    )
    humidity_yellow = (
        humidity <= threshold.humidity_min + humidity_margin or
        humidity >= threshold.humidity_max - humidity_margin
    )

    if temp_yellow or humidity_yellow:
        return "yellow"

    return "green"
