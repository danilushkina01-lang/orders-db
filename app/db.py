from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_database_url


class Base(DeclarativeBase):
    pass


engine = create_engine(get_database_url(), echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
