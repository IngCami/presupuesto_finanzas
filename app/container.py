"""
Contenedor de dependencias.
"""
from app.application.use_cases.auth_use_cases import AuthUseCases
from app.application.use_cases.expense_use_cases import ExpenseUseCases
from app.application.use_cases.report_use_cases import ReportUseCases
from app.infrastructure.db.database import Database
from app.infrastructure.repositories.sqlite_expense_repository import (
    SqliteExpenseRepository,
)
from app.infrastructure.repositories.sqlite_user_repository import (
    SqliteUserRepository,
)
from app.infrastructure.security.password_hasher import PasswordHasher


class Container:
    def __init__(self, db_path: str):
        self.database = Database(db_path)

        self.user_repository = SqliteUserRepository(self.database)
        self.expense_repository = SqliteExpenseRepository(self.database)
        self.password_hasher = PasswordHasher()

        self.auth_use_cases = AuthUseCases(self.user_repository, self.password_hasher)
        self.expense_use_cases = ExpenseUseCases(self.expense_repository)
        self.report_use_cases = ReportUseCases(
            self.user_repository, self.expense_repository
        )
