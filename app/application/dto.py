"""
DTOs (Data Transfer Objects) usados entre la capa de presentación y los casos de uso.
Mantienen la capa de aplicación desacoplada de formularios/HTTP.
"""
from dataclasses import dataclass
from datetime import date

from app.domain.entities import CategoryType


@dataclass
class RegisterUserInput:
    name: str
    email: str
    password: str


@dataclass
class LoginInput:
    email: str
    password: str


@dataclass
class AddExpenseInput:
    user_id: int
    description: str
    amount: float
    category: CategoryType
    expense_date: date
