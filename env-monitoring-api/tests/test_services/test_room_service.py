from app.services.room_service import create_room, list_rooms, get_room


def test_create_room(db):
    room = create_room(db, name="Lab A", location="Building 1, Floor 2")
    assert room.id is not None
    assert room.name == "Lab A"
    assert room.location == "Building 1, Floor 2"


def test_list_rooms(db):
    create_room(db, name="R1", location="L1")
    create_room(db, name="R2", location="L2")
    rooms = list_rooms(db)
    assert len(rooms) == 2


def test_get_room(db):
    room = create_room(db, name="Target", location="Loc")
    found = get_room(db, room.id)
    assert found is not None
    assert found.name == "Target"


def test_get_room_not_found(db):
    assert get_room(db, 9999) is None
