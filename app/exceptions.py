class DomainError(Exception):
    pass


class InvalidAmountError(DomainError):
    def __init__(self, amount):
        super().__init__(f"Сумма заказа должна быть положительной, получено: {amount}")


class UserNotFoundError(DomainError):
    def __init__(self, user_id):
        super().__init__(f"Пользователь с id={user_id} не найден")


class InsufficientBalanceError(DomainError):
    def __init__(self, user_id, balance, amount):
        super().__init__(
            f"Недостаточно средств: баланс {balance} меньше суммы {amount} (user_id={user_id})"
        )


class InjectedFailureError(DomainError):
    """Искусственная ошибка для теста атомарности."""
    def __init__(self):
        super().__init__("Тестовый сбой между списанием и добавлением заказа")
