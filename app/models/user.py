from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.sql import func
from ..database import Base
import enum


class Role(enum.Enum):
    buyer = "buyer"
    seller = "seller"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Role), default=Role.buyer, nullable=False)
    created_at = Column(String, server_default=func.now())
