from decimal import Decimal

from sqlalchemy import event, select
from sqlalchemy.orm import selectinload

from app.db import Base
from app.models import Order, User
from tests.conftest import TestSessionLocal


class QueryCounter:
    def __init__(self, engine):
        self.count = 0
        self.statements = []
        event.listen(engine, "before_cursor_execute", self._on_query)

    def _on_query(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1
        self.statements.append(statement)

    def reset(self):
        self.count = 0
        self.statements = []


def seed(session):
    """Создаём 5 пользователей, у каждого по 3 заказа."""
    for i in range(1, 6):
        user = User(email=f"user{i}@example.com", balance=Decimal("100.00"))
        session.add(user)
        session.flush()
        for j in range(3):
            session.add(Order(user_id=user.id, amount=Decimal("10.00")))
    session.commit()


def test_naive_vs_selectinload(prepared_database):
    s = TestSessionLocal()
    seed(s)
    s.close()

    counter = QueryCounter(TestSessionLocal.kw["bind"])

    # --- Вариант 1: наивный ---
    s1 = TestSessionLocal()          # свежая сессия
    counter.reset()                  # сброс счётчика перед вариантом
    users = s1.scalars(select(User)).all()
    result_naive = [(u.email, [o.amount for o in u.orders]) for u in users]
    naive_queries = counter.count
    s1.close()

    # --- Вариант 2: selectinload ---
    s2 = TestSessionLocal()          # снова свежая сессия
    counter.reset()                  # сброс перед вторым вариантом
    users = s2.scalars(
        select(User).options(selectinload(User.orders))
    ).all()
    result_batch = [(u.email, [o.amount for o in u.orders]) for u in users]
    batch_queries = counter.count
    in_queries = [q for q in counter.statements if " IN " in q.upper()]
    s2.close()

    assert result_naive == result_batch
    assert naive_queries == 1 + 5            # 1 основной + по запросу на пользователя
    assert batch_queries == 2                # основной + один пакетный с IN
    assert len(in_queries) == 1 and "IN" in in_queries[0].upper()
