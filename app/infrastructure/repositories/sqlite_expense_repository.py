from datetime import date, datetime
from typing import List

from app.domain.entities import CategoryType, Expense
from app.domain.repositories import ExpenseRepository
from app.infrastructure.db.database import Database


class SqliteExpenseRepository(ExpenseRepository):
    def __init__(self, database: Database):
        self._db = database

    def add(self, expense: Expense) -> Expense:
        conn = self._db.get_connection()
        try:
            cur = conn.execute(
                """INSERT INTO expenses (user_id, description, amount, category, expense_date)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    expense.user_id,
                    expense.description,
                    expense.amount,
                    expense.category.value,
                    expense.expense_date.isoformat(),
                ),
            )
            expense.id = cur.lastrowid
            conn.commit()
            return expense
        finally:
            conn.close()

    def delete(self, expense_id: int, user_id: int) -> bool:
        conn = self._db.get_connection()
        try:
            cur = conn.execute(
                "DELETE FROM expenses WHERE id = ? AND user_id = ?",
                (expense_id, user_id),
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()

    def list_by_user(self, user_id: int) -> List[Expense]:
        conn = self._db.get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM expenses WHERE user_id = ? ORDER BY expense_date DESC",
                (user_id,),
            ).fetchall()
            return [self._row_to_expense(r) for r in rows]
        finally:
            conn.close()

    def list_by_user_between(
        self, user_id: int, start: date, end: date
    ) -> List[Expense]:
        conn = self._db.get_connection()
        try:
            rows = conn.execute(
                """SELECT * FROM expenses WHERE user_id = ?
                   AND expense_date BETWEEN ? AND ?
                   ORDER BY expense_date DESC""",
                (user_id, start.isoformat(), end.isoformat()),
            ).fetchall()
            return [self._row_to_expense(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def _row_to_expense(row) -> Expense:
        return Expense(
            id=row["id"],
            user_id=row["user_id"],
            description=row["description"],
            amount=row["amount"],
            category=CategoryType(row["category"]),
            expense_date=datetime.strptime(row["expense_date"], "%Y-%m-%d").date(),
        )
