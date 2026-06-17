"""
Demo seed: run once after `alembic upgrade head`.
Creates admin, 4 rooms+devices, thresholds and 48h of sample measurements.
"""
import random
from datetime import datetime, timedelta, timezone
from app.db import SessionLocal
from app.services.user_service import create_user, get_by_username
from app.services.room_service import create_room
from app.services.device_service import create_device
from app.services.threshold_service import upsert as upsert_threshold
from app.services.measurement_service import create_measurement
from app.models.user import UserRole

ROOMS = [
    ("Laboratorio A",    "Edificio 1, Piso 2",  18.0, 26.0, 40.0, 70.0),
    ("Cámara Fría",      "Edificio 1, Sótano",   2.0,  8.0, 50.0, 80.0),
    ("Sala de Servidores","Edificio 2, Piso 1",  16.0, 24.0, 35.0, 60.0),
    ("Cuarto de Control","Edificio 2, Piso 3",   20.0, 28.0, 40.0, 65.0),
]

def _simulate_measurements(db, device_id, temp_center, hum_center, hours=48):
    now = datetime.now(timezone.utc)
    for i in range(hours * 4):  # one per 15 min
        ts = now - timedelta(minutes=15 * (hours * 4 - i))
        temp = round(temp_center + random.uniform(-2.5, 2.5), 2)
        hum = round(hum_center + random.uniform(-5.0, 5.0), 2)
        hum = max(0.0, min(100.0, hum))
        create_measurement(db, device_id=device_id, temperature=temp, humidity=hum, timestamp=ts)

def main():
    db = SessionLocal()
    try:
        if not get_by_username(db, "admin"):
            create_user(db, username="admin", password="admin123", role=UserRole.admin)
            print("Created admin user (admin / admin123)")

        for room_name, location, t_min, t_max, h_min, h_max in ROOMS:
            room = create_room(db, name=room_name, location=location)
            device = create_device(db, room_id=room.id, name=f"Nodo {room_name}")
            upsert_threshold(db, device_id=device.id,
                             temp_min=t_min, temp_max=t_max,
                             humidity_min=h_min, humidity_max=h_max)
            temp_center = (t_min + t_max) / 2
            hum_center = (h_min + h_max) / 2
            _simulate_measurements(db, device.id, temp_center, hum_center)
            print(f"Seeded: {room_name}")

        print("Done. Run: uvicorn app.main:app --reload")
    finally:
        db.close()

if __name__ == "__main__":
    main()
