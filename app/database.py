from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .config import settings

engine_kwargs = {"pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

from sqlalchemy.orm import declarative_base

Base = declarative_base()
Base.query = db_session.query_property()


def get_db():
    return db_session
