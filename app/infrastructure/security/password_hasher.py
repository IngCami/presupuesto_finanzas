from werkzeug.security import check_password_hash, generate_password_hash


class PasswordHasher:
    def hash(self, plain_password: str) -> str:
        return generate_password_hash(plain_password)

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return check_password_hash(password_hash, plain_password)
