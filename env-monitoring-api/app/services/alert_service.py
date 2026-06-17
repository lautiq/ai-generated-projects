from typing import Literal

AlertStatus = Literal["ok", "warning", "danger", "unknown"]


def compute_status(measurement, threshold) -> AlertStatus:
    if measurement is None or threshold is None:
        return "unknown"

    temp = measurement.temperature
    humidity = measurement.humidity

    if temp < threshold.temp_min or temp > threshold.temp_max:
        return "danger"
    if humidity < threshold.humidity_min or humidity > threshold.humidity_max:
        return "danger"

    temp_margin = (threshold.temp_max - threshold.temp_min) * 0.10
    humidity_margin = (threshold.humidity_max - threshold.humidity_min) * 0.10

    temp_near = (
        temp <= threshold.temp_min + temp_margin or
        temp >= threshold.temp_max - temp_margin
    )
    humidity_near = (
        humidity <= threshold.humidity_min + humidity_margin or
        humidity >= threshold.humidity_max - humidity_margin
    )

    if temp_near or humidity_near:
        return "warning"

    return "ok"
