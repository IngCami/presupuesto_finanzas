from dataclasses import dataclass
from typing import Dict, List

from app.domain.entities import CategoryType, Expense


@dataclass
class CategoryBudgetStatus:
    category: CategoryType
    recomendado: float
    gastado: float

    @property
    def diferencia(self) -> float:
        """Positivo = sobra presupuesto. Negativo = te excediste."""
        return self.recomendado - self.gastado

    @property
    def porcentaje_usado(self) -> float:
        if self.recomendado <= 0:
            return 0.0
        return round((self.gastado / self.recomendado) * 100, 1)

    @property
    def excedido(self) -> bool:
        return self.gastado > self.recomendado


@dataclass
class BudgetReport:
    ingreso: float
    estados: Dict[CategoryType, CategoryBudgetStatus]

    @property
    def total_gastado(self) -> float:
        return sum(e.gastado for e in self.estados.values())

    @property
    def total_recomendado(self) -> float:
        return sum(e.recomendado for e in self.estados.values())


def calcular_reporte(ingreso: float, gastos: List[Expense]) -> BudgetReport:
    """Calcula el estado del presupuesto 50/30/20 para un conjunto de gastos."""
    totales_por_categoria: Dict[CategoryType, float] = {
        cat: 0.0 for cat in CategoryType
    }
    for gasto in gastos:
        totales_por_categoria[gasto.category] += gasto.amount

    estados = {}
    for cat in CategoryType:
        recomendado = round(ingreso * cat.porcentaje_recomendado, 2)
        estados[cat] = CategoryBudgetStatus(
            category=cat,
            recomendado=recomendado,
            gastado=round(totales_por_categoria[cat], 2),
        )

    return BudgetReport(ingreso=ingreso, estados=estados)
