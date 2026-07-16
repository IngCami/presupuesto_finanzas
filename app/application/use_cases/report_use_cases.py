"""
Casos de uso de reportes: agrupan gastos por mes y por quincena,
y calculan el estado del presupuesto 50/30/20.
"""
import calendar
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

from app.domain.budget_rules import BudgetReport, calcular_reporte
from app.domain.entities import CategoryType, Expense, User
from app.domain.repositories import ExpenseRepository, UserRepository

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


@dataclass
class PeriodSummary:
    """Resumen de un periodo (mes o quincena) para el historial."""

    key: str
    label: str
    total: float
    por_categoria: Dict[CategoryType, float] = field(default_factory=dict)


class ReportUseCases:
    def __init__(
        self, user_repository: UserRepository, expense_repository: ExpenseRepository
    ):
        self._users = user_repository
        self._expenses = expense_repository

    # ---------- Reporte 50/30/20 del mes actual ----------
    def current_month_budget_report(self, user: User, today: date) -> BudgetReport:
        gastos = self._expenses.list_by_user(user.id)
        gastos_mes = [
            g
            for g in gastos
            if g.expense_date.year == today.year and g.expense_date.month == today.month
        ]
        return calcular_reporte(user.monthly_income, gastos_mes)

    # ---------- Historial mensual ----------
    def monthly_history(self, user_id: int) -> List[PeriodSummary]:
        gastos = self._expenses.list_by_user(user_id)
        agrupado: Dict[str, List[Expense]] = defaultdict(list)
        for g in gastos:
            agrupado[g.month_key()].append(g)

        resumenes = []
        for key in sorted(agrupado.keys(), reverse=True):
            items = agrupado[key]
            year, month = map(int, key.split("-"))
            label = f"{MESES_ES[month]} {year}"
            resumenes.append(self._build_summary(key, label, items))
        return resumenes

    # ---------- Historial quincenal ----------
    def biweekly_history(self, user_id: int) -> List[PeriodSummary]:
        gastos = self._expenses.list_by_user(user_id)
        agrupado: Dict[str, List[Expense]] = defaultdict(list)
        for g in gastos:
            agrupado[g.quincena_key()].append(g)

        resumenes = []
        for key in sorted(agrupado.keys(), reverse=True):
            items = agrupado[key]
            year, month, q = key.split("-")[0], key.split("-")[1], key.split("-")[2]
            month_i = int(month)
            rango = "1 al 15" if q == "Q1" else f"16 al {calendar.monthrange(int(year), month_i)[1]}"
            label = f"{MESES_ES[month_i]} {year} (días {rango})"
            resumenes.append(self._build_summary(key, label, items))
        return resumenes

    @staticmethod
    def _build_summary(key: str, label: str, items: List[Expense]) -> PeriodSummary:
        por_categoria: Dict[CategoryType, float] = {cat: 0.0 for cat in CategoryType}
        for g in items:
            por_categoria[g.category] += g.amount
        total = sum(por_categoria.values())
        return PeriodSummary(
            key=key,
            label=label,
            total=round(total, 2),
            por_categoria={k: round(v, 2) for k, v in por_categoria.items()},
        )
