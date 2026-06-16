from sqlalchemy.orm import Session
from sqlalchemy import or_, select

from .. import models, schemas
from ..utils.security import verify_password, get_password_hash


def get_user_by_username(db: Session, username: str):
    stmt = select(models.User).where(models.User.username == username)
    return db.scalars(stmt).first()


def get_user_by_email(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    return db.scalars(stmt).first()


def get_user_by_username_or_email(db: Session, username_or_email: str):
    normalized = username_or_email.strip().lower()
    stmt = select(models.User).where(
        or_(models.User.username == normalized, models.User.email == normalized)
    )
    return db.scalars(stmt).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=models.Role(user.role),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username_or_email: str, password: str):
    user = get_user_by_username_or_email(db, username_or_email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
