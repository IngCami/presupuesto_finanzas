from typing import Optional
from app.domain.entities import User, IncomeRecord
from app.domain.repositories import UserRepository
from app.infrastructure.db.database import Database


class SqliteUserRepository(UserRepository):
    def __init__(self, database: Database):
        self._db = database

    def get_by_id(self, user_id: int) -> Optional[User]:
        conn = self._db.get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return self._row_to_user(row) if row else None
        finally:
            conn.close()

    def get_by_email(self, email: str) -> Optional[User]:
        conn = self._db.get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
            return self._row_to_user(row) if row else None
        finally:
            conn.close()

    def save(self, user: User) -> User:
        conn = self._db.get_connection()
        try:
            if user.id is None:
                cur = conn.execute(
                    """INSERT INTO users (name, email, password_hash, monthly_income)
                       VALUES (?, ?, ?, ?)""",
                    (user.name, user.email, user.password_hash, user.monthly_income),
                )
                user.id = cur.lastrowid
            else:
                conn.execute(
                    """UPDATE users SET name = ?, email = ?, password_hash = ?,
                       monthly_income = ? WHERE id = ?""",
                    (
                        user.name,
                        user.email,
                        user.password_hash,
                        user.monthly_income,
                        user.id,
                    ),
                )
            conn.commit()
            return user
        finally:
            conn.close()

    def save_income_history(self, record: IncomeRecord) -> IncomeRecord:
        conn = self._db.get_connection()
        try:
            cur = conn.execute(
                """INSERT INTO income_history (user_id, month_year, amount)
                   VALUES (?, ?, ?)
                   ON CONFLICT(user_id, month_year) DO UPDATE SET amount = excluded.amount""",
                (record.user_id, record.month_year, record.amount),
            )
            if record.id is None:
                record.id = cur.lastrowid
            conn.commit()
            return record
        finally:
            conn.close()

    def get_income_history(self, user_id: int) -> list[IncomeRecord]:
        conn = self._db.get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM income_history WHERE user_id = ? ORDER BY month_year DESC",
                (user_id,)
            ).fetchall()
            return [
                IncomeRecord(
                    id=r["id"], 
                    user_id=r["user_id"], 
                    month_year=r["month_year"], 
                    amount=r["amount"]
                ) for r in rows
            ]
        finally:
            conn.close()
    def get_income_by_month(self, user_id: int, month_year: str) -> Optional[IncomeRecord]:
        conn = self._db.get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM income_history WHERE user_id = ? AND month_year = ?",
                (user_id, month_year)
            ).fetchone()
            if row:
                return IncomeRecord(
                    id=row["id"], user_id=row["user_id"], 
                    month_year=row["month_year"], amount=row["amount"]
                )
            return None
        finally:
            conn.close()
            
    @staticmethod
    def _row_to_user(row) -> User:
        return User(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            monthly_income=row["monthly_income"],
        )