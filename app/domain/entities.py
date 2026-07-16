from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class CategoryType(str, Enum):
    NECESIDAD = "necesidad"      # 50% - servicios básicos necesarios
    LUJO = "lujo"                # 30% - lujos personales
    AHORRO = "ahorro"            # 20% - ahorro

    @property
    def etiqueta(self) -> str:
        return {
            CategoryType.NECESIDAD: "Servicios básicos necesarios",
            CategoryType.LUJO: "Lujos personales",
            CategoryType.AHORRO: "Ahorro",
        }[self]

    @property
    def porcentaje_recomendado(self) -> float:
        return {
            CategoryType.NECESIDAD: 0.50,
            CategoryType.LUJO: 0.30,
            CategoryType.AHORRO: 0.20,
        }[self]


@dataclass
class User:
    """Usuario del sistema."""

    id: Optional[int]
    name: str
    email: str
    password_hash: str
    monthly_income: float = 0.0

    def has_income_configured(self) -> bool:
        return self.monthly_income > 0


@dataclass
class Expense:

    id: Optional[int]
    user_id: int
    description: str
    amount: float
    category: CategoryType
    expense_date: date

    def quincena(self) -> int:
        return 1 if self.expense_date.day <= 15 else 2

    def month_key(self) -> str:
        return f"{self.expense_date.year:04d}-{self.expense_date.month:02d}"

    def quincena_key(self) -> str:
        return f"{self.month_key()}-Q{self.quincena()}"

@dataclass
class IncomeRecord:
    id: Optional[int]
    user_id: int
    month_year: str  
    amount: float