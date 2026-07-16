import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
    DB_PATH = os.environ.get("DB_PATH", os.path.join("data", "expense_manager.db"))
