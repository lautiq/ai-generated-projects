import bcrypt
from sqlalchemy.orm import Session
from app.models.user import User, UserRole


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_user(db: Session, username: str, password: str, role: UserRole = UserRole.user) -> User:
    user = User(username=username, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def list_users(db: Session):
    return db.query(User).all()


def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
