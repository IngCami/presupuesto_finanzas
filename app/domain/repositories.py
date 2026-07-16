from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.domain.entities import Expense, User


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def save(self, user: User) -> User:
        """Crea el usuario si no tiene id, o lo actualiza si ya existe."""
        ...


class ExpenseRepository(ABC):
    @abstractmethod
    def add(self, expense: Expense) -> Expense:
        ...

    @abstractmethod
    def delete(self, expense_id: int, user_id: int) -> bool:
        ...

    @abstractmethod
    def list_by_user(self, user_id: int) -> List[Expense]:
        ...

    @abstractmethod
    def list_by_user_between(
        self, user_id: int, start: date, end: date
    ) -> List[Expense]:
        ...
