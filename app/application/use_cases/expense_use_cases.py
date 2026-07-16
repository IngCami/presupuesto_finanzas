"""
Casos de uso para gestionar gastos.
"""
from typing import List

from app.application.dto import AddExpenseInput
from app.domain.entities import Expense
from app.domain.repositories import ExpenseRepository


class MontoInvalidoError(Exception):
    pass


class ExpenseUseCases:
    def __init__(self, expense_repository: ExpenseRepository):
        self._expenses = expense_repository

    def add_expense(self, data: AddExpenseInput) -> Expense:
        if data.amount <= 0:
            raise MontoInvalidoError("El monto del gasto debe ser mayor a 0.")
        if not data.description.strip():
            raise MontoInvalidoError("La descripción no puede estar vacía.")

        expense = Expense(
            id=None,
            user_id=data.user_id,
            description=data.description.strip(),
            amount=round(data.amount, 2),
            category=data.category,
            expense_date=data.expense_date,
        )
        return self._expenses.add(expense)

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        return self._expenses.delete(expense_id, user_id)

    def list_all(self, user_id: int) -> List[Expense]:
        gastos = self._expenses.list_by_user(user_id)
        return sorted(gastos, key=lambda g: g.expense_date, reverse=True)
