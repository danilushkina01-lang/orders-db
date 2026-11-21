from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Order, User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User:
        self._session.add(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self._session.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalars(
            select(User).where(User.email == email)
        ).first()


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, order: Order) -> Order:
        self._session.add(order)
        return order

    def get_by_id(self, order_id: int) -> Order | None:
        return self._session.get(Order, order_id)

    def get_for_user(self, user_id: int) -> list[Order]:
        return list(self._session.scalars(
            select(Order).where(Order.user_id == user_id)
        ).all())
