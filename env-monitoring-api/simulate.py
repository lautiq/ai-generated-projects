"""
Live simulator: inserts new measurements every 30 seconds for all devices.
Run alongside the server: py simulate.py
Ctrl+C to stop.
"""
import time
import random
from datetime import datetime, timezone
from app.db import SessionLocal
from app.models import room, user, threshold  # noqa: F401 — register all models
from app.models.device import Device
from app.models.measurement import Measurement
from app.services.measurement_service import create_measurement

# Drift state per device so values move gradually instead of jumping randomly
_state: dict[int, dict] = {}

INTERVAL = 30  # seconds


def _get_devices(db):
    return db.query(Device).all()


def _last_measurement(db, device_id):
    return (
        db.query(Measurement)
        .filter(Measurement.device_id == device_id)
        .order_by(Measurement.timestamp.desc())
        .first()
    )


def _init_state(device_id, temp, hum):
    _state[device_id] = {"temp": temp, "hum": hum}


def _next_value(current, step=0.3, noise=0.5, min_val=None, max_val=None):
    """Random walk: small drift + noise."""
    drift = random.uniform(-step, step)
    noise_val = random.gauss(0, noise)
    new = round(current + drift + noise_val, 2)
    if min_val is not None:
        new = max(min_val, new)
    if max_val is not None:
        new = min(max_val, new)
    return new


def tick():
    db = SessionLocal()
    try:
        devices = _get_devices(db)
        if not devices:
            print("No devices found. Run seed_demo.py first.")
            return

        for device in devices:
            # Initialize state from last measurement on first run
            if device.id not in _state:
                last = _last_measurement(db, device.id)
                if last:
                    _init_state(device.id, last.temperature, last.humidity)
                else:
                    _init_state(device.id, 22.0, 55.0)

            state = _state[device.id]
            temp = _next_value(state["temp"], step=0.2, noise=0.3)
            hum = _next_value(state["hum"], step=0.3, noise=0.5, min_val=0.0, max_val=100.0)

            state["temp"] = temp
            state["hum"] = hum

            create_measurement(db, device_id=device.id, temperature=temp,
                               humidity=hum, timestamp=datetime.now(timezone.utc))

            print(f"  [{device.name}] temp={temp}°C  hum={hum}%")

    finally:
        db.close()


def main():
    print(f"Simulator running — new readings every {INTERVAL}s. Ctrl+C to stop.\n")
    while True:
        now = datetime.now(timezone.utc).strftime("%H:%M:%S")
        print(f"[{now}]")
        tick()
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
