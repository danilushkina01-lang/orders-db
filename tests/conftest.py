import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import TEST_DATABASE_URL

# Alembic env.py читает DATABASE_URL — переключаем его на тестовую базу,
# иначе миграции уйдут в orders_db, а тесты смотрят в orders_test.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

test_engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSession = sessionmaker(bind=test_engine, expire_on_commit=False)
TestSessionLocal = TestSession


@pytest.fixture(autouse=True)
def prepared_database():
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


@pytest.fixture
def session():
    s = TestSession()
    yield s
    s.rollback()
    s.close()
