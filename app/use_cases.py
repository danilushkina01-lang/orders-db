from decimal import Decimal

from sqlalchemy.orm import Session

from .exceptions import (
    InjectedFailureError,
    InsufficientBalanceError,
    InvalidAmountError,
    UserNotFoundError,
)
from .models import Order, OrderStatus, User


def create_order(
    session: Session,
    user_id: int,
    amount: Decimal,
    fail_before_add: bool = False,
) -> Order:
    if amount <= 0:
        raise InvalidAmountError(amount)

    user = session.get(User, user_id)
    if user is None:
        raise UserNotFoundError(user_id)
    if user.balance < amount:
        raise InsufficientBalanceError(user_id, user.balance, amount)

    user.balance -= amount

    if fail_before_add:
        # Искусственный сбой строго между списанием и добавлением заказа.
        session.rollback()
        raise InjectedFailureError()

    order = Order(user_id=user_id, amount=amount, status=OrderStatus.pending)
    session.add(order)
    session.commit()
    return order


def create_user(session: Session, email: str, balance: Decimal = Decimal("0.00")) -> User:
    user = User(email=email, balance=balance)
    session.add(user)
    session.commit()
    return user
