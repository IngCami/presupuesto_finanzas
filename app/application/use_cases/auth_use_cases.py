from app.application.dto import LoginInput, RegisterUserInput
from app.domain.entities import User, IncomeRecord
from app.domain.repositories import UserRepository
from app.infrastructure.security.password_hasher import PasswordHasher


class EmailYaRegistradoError(Exception):
    pass


class CredencialesInvalidasError(Exception):
    pass


class AuthUseCases:
    def __init__(self, user_repository: UserRepository, hasher: PasswordHasher):
        self._users = user_repository
        self._hasher = hasher

    def register(self, data: RegisterUserInput) -> User:
        if self._users.get_by_email(data.email):
            raise EmailYaRegistradoError(
                f"El correo {data.email} ya está registrado."
            )

        user = User(
            id=None,
            name=data.name.strip(),
            email=data.email.strip().lower(),
            password_hash=self._hasher.hash(data.password),
            monthly_income=0.0,
        )
        return self._users.save(user)

    def login(self, data: LoginInput) -> User:
        user = self._users.get_by_email(data.email.strip().lower())
        if user is None or not self._hasher.verify(data.password, user.password_hash):
            raise CredencialesInvalidasError("Correo o contraseña incorrectos.")
        return user

    def update_income(self, user_id: int, monthly_income: float, month_year: str) -> User:
        user = self._users.get_by_id(user_id)
        if user is None:
            raise ValueError("Usuario no encontrado.")
        user.monthly_income = monthly_income
        saved_user = self._users.save(user)
        historial = IncomeRecord(
            id=None,
            user_id=user_id,
            month_year=month_year,
            amount=monthly_income
        )
        self._users.save_income_history(historial)

        return saved_user
