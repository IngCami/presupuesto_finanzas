from datetime import date, datetime
import re

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.application.dto import AddExpenseInput
from app.application.use_cases.expense_use_cases import MontoInvalidoError
from app.domain.entities import CategoryType
from app.infrastructure.security.session_auth import current_user_id, login_required

expenses_bp = Blueprint("expenses", __name__)


def _container():
    return current_app.config["CONTAINER"]


@expenses_bp.route("/")
@login_required
def dashboard():
    container = _container()
    user = container.user_repository.get_by_id(current_user_id())
    today = date.today()

    reporte = container.report_use_cases.current_month_budget_report(user, today)
    gastos_recientes = container.expense_use_cases.list_all(user.id)[:8]
    categorias = list(CategoryType)
    chart_labels = [cat.etiqueta for cat in categorias]
    chart_data = [float(reporte.estados[cat].gastado) for cat in categorias]

    return render_template(
        "dashboard.html",
        user=user,
        reporte=reporte,
        categorias=categorias,
        gastos_recientes=gastos_recientes,
        chart_labels=chart_labels,
        chart_data=chart_data,
    )


@expenses_bp.route("/gastos", methods=["GET", "POST"])
@login_required
def list_expenses():
    container = _container()
    user_id = current_user_id()

    if request.method == "POST":
        try:
            expense_date_str = request.form.get("expense_date") or date.today().isoformat()
            data = AddExpenseInput(
                user_id=user_id,
                description=request.form.get("description", ""),
                amount=float(request.form.get("amount", 0)),
                category=CategoryType(request.form.get("category")),
                expense_date=datetime.strptime(expense_date_str, "%Y-%m-%d").date(),
            )
            container.expense_use_cases.add_expense(data)
            flash("Gasto agregado correctamente.", "success")
        except (MontoInvalidoError, ValueError) as e:
            flash(f"No se pudo agregar el gasto: {e}", "error")

        return redirect(url_for("expenses.list_expenses"))

    gastos = container.expense_use_cases.list_all(user_id)
    return render_template(
        "expenses.html", gastos=gastos, categorias=list(CategoryType), today=date.today().isoformat()
    )


@expenses_bp.route("/gastos/<int:expense_id>/eliminar", methods=["POST"])
@login_required
def delete_expense(expense_id):
    container = _container()
    eliminado = container.expense_use_cases.delete_expense(
        expense_id, current_user_id()
    )
    if eliminado:
        flash("Gasto eliminado.", "success")
    else:
        flash("No se encontró el gasto.", "error")
    return redirect(url_for("expenses.list_expenses"))

@expenses_bp.route("/reporte/<month_year>/pdf")
@login_required
def reporte_pdf(month_year):
    user_id = current_user_id()
    user = _container().user_repository.get_by_id(user_id)
    meses_espanol = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }
    formato_db = month_year
    partes = month_year.split() 
    if len(partes) == 2 and partes[0].lower() in meses_espanol:
        mes_num = meses_espanol[partes[0].lower()]
        año = partes[1]
        formato_db = f"{año}-{mes_num}" 
    record = _container().user_repository.get_income_by_month(user_id, formato_db)
    ingreso_mes = record.amount if record else user.monthly_income
    todos_los_gastos = _container().expense_repository.list_by_user(user_id)
    gastos_mes = [g for g in todos_los_gastos if g.month_key() == formato_db]
    gastos_categoria = {"necesidad": [], "lujo": [], "ahorro": []}
    total_gastado = 0

    for g in gastos_mes:
        gastos_categoria[g.category.value].append(g)
        total_gastado += g.amount

    sobrante = ingreso_mes - total_gastado

    return render_template(
        "reporte_pdf.html",
        mes=month_year.capitalize(),
        ingreso=ingreso_mes,
        gastos_categoria=gastos_categoria,
        total_gastado=total_gastado,
        sobrante=sobrante
    )


@expenses_bp.route("/reporte_quincena/<texto_quincena>/pdf")
@login_required
def reporte_quincena_pdf(texto_quincena):
    user_id = current_user_id()
    user = _container().user_repository.get_by_id(user_id)
    texto_lower = texto_quincena.lower()
    meses_espanol = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }
    mes_num = "01"
    for mes_nombre, numero in meses_espanol.items():
        if mes_nombre in texto_lower:
            mes_num = numero
            break
    año_match = re.search(r'\d{4}', texto_lower)
    año = año_match.group() if año_match else "2026"
    texto_sin_año = texto_lower.replace(año, "")
    quincena_num = 2 if "2" in texto_sin_año else 1
    formato_db = f"{año}-{mes_num}"
    quincena_key_db = f"{formato_db}-Q{quincena_num}"
    record = _container().user_repository.get_income_by_month(user_id, formato_db)
    ingreso_quincena = (record.amount if record else user.monthly_income) / 2
    todos_los_gastos = _container().expense_repository.list_by_user(user_id)
    gastos_quincena = [g for g in todos_los_gastos if g.quincena_key() == quincena_key_db]
    gastos_categoria = {"necesidad": [], "lujo": [], "ahorro": []}
    total_gastado = 0
    for g in gastos_quincena:
        gastos_categoria[g.category.value].append(g)
        total_gastado += g.amount
    sobrante = ingreso_quincena - total_gastado
    return render_template(
        "reporte_pdf.html",
        mes=texto_quincena.title(), 
        ingreso=ingreso_quincena,
        gastos_categoria=gastos_categoria,
        total_gastado=total_gastado,
        sobrante=sobrante
    )