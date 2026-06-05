from sqlalchemy.orm import Session
from app.models.room import Room


def create_room(db: Session, name: str, location: str) -> Room:
    room = Room(name=name, location=location)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def list_rooms(db: Session):
    return db.query(Room).all()


def get_room(db: Session, room_id: int):
    return db.query(Room).filter(Room.id == room_id).first()
