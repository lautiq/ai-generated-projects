from unittest.mock import MagicMock
from app.services.alert_service import compute_status


def _mock_measurement(temp, humidity):
    m = MagicMock()
    m.temperature = temp
    m.humidity = humidity
    return m


def _mock_threshold(temp_min, temp_max, hum_min, hum_max):
    t = MagicMock()
    t.temp_min = temp_min
    t.temp_max = temp_max
    t.humidity_min = hum_min
    t.humidity_max = hum_max
    return t


# Threshold: temp 20-30°C, humidity 40-70% (ranges: 10°C, 30%)
# Yellow zone: temp 20-21 or 29-30; humidity 40-43 or 67-70

def test_unknown_no_measurement():
    assert compute_status(None, _mock_threshold(20, 30, 40, 70)) == "unknown"


def test_unknown_no_threshold():
    assert compute_status(_mock_measurement(25, 55), None) == "unknown"


def test_green():
    assert compute_status(_mock_measurement(25, 55), _mock_threshold(20, 30, 40, 70)) == "green"


def test_red_temp_above():
    assert compute_status(_mock_measurement(31, 55), _mock_threshold(20, 30, 40, 70)) == "red"


def test_red_temp_below():
    assert compute_status(_mock_measurement(19, 55), _mock_threshold(20, 30, 40, 70)) == "red"


def test_red_humidity_above():
    assert compute_status(_mock_measurement(25, 71), _mock_threshold(20, 30, 40, 70)) == "red"


def test_red_humidity_below():
    assert compute_status(_mock_measurement(25, 39), _mock_threshold(20, 30, 40, 70)) == "red"


def test_yellow_temp_near_max():
    # 29.5°C is within 10% of range (1°C) from max
    assert compute_status(_mock_measurement(29.5, 55), _mock_threshold(20, 30, 40, 70)) == "yellow"


def test_yellow_humidity_near_min():
    # 41.5% is within 10% of range (3%) from min
    assert compute_status(_mock_measurement(25, 41.5), _mock_threshold(20, 30, 40, 70)) == "yellow"
