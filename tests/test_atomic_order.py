from decimal import Decimal

import pytest

from app.exceptions import InjectedFailureError, InsufficientBalanceError, InvalidAmountError
from app.models import Order, User
from app.use_cases import create_order, create_user
from tests.conftest import TestSessionLocal


def test_create_order_success(session):
    user = create_user(session, "ira@example.com", Decimal("100.00"))
    session.close()

    fresh = TestSessionLocal()
    order = create_order(fresh, user.id, Decimal("40.00"))
    assert order.status == "pending"
    fresh.close()


def test_injected_failure_does_not_persist(session):
    user = create_user(session, "ira@example.com", Decimal("100.00"))
    session.close()

    s1 = TestSessionLocal()
    with pytest.raises(InjectedFailureError):
        create_order(s1, user.id, Decimal("30.00"), fail_before_add=True)
    s1.close()

    # Проверка строго новой сессией — не той, где случился сбой.
    s2 = TestSessionLocal()
    user_after = s2.get(User, user.id)
    orders = s2.query(Order).all()
    assert user_after.balance == Decimal("100.00")  # баланс не уменьшился
    assert orders == []                              # заказ не сохранился
    s2.close()


def test_invalid_amount(session):
    with pytest.raises(InvalidAmountError):
        create_order(session, 1, Decimal("0"))


def test_insufficient_balance(session):
    user = create_user(session, "ira@example.com", Decimal("10.00"))
    session.close()
    fresh = TestSessionLocal()
    with pytest.raises(InsufficientBalanceError):
        create_order(fresh, user.id, Decimal("50.00"))
    fresh.close()
