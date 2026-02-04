from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas
from ..utils.security import verify_password, get_password_hash


def get_user_by_username(db: Session, username: str):
    stmt = select(models.User).where(models.User.username == username)
    return db.scalars(stmt).first()


def get_user_by_email(db: Session, email: str):
    stmt = select(models.User).where(models.User.email == email)
    return db.scalars(stmt).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
