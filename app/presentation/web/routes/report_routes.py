from flask import Blueprint, current_app, jsonify, render_template

from app.infrastructure.security.session_auth import current_user_id, login_required

reports_bp = Blueprint("reports", __name__)


def _container():
    return current_app.config["CONTAINER"]


@reports_bp.route("/historial/mensual")
@login_required
def monthly_history():
    resumenes = _container().report_use_cases.monthly_history(current_user_id())
    return render_template(
        "history.html",
        resumenes=resumenes,
        titulo="Historial mensual",
        endpoint_json="reports.monthly_history_json",
    )


@reports_bp.route("/historial/quincenal")
@login_required
def biweekly_history():
    resumenes = _container().report_use_cases.biweekly_history(current_user_id())
    return render_template(
        "history.html",
        resumenes=resumenes,
        titulo="Historial quincenal",
        endpoint_json="reports.biweekly_history_json",
    )


@reports_bp.route("/api/historial/mensual.json")
@login_required
def monthly_history_json():
    resumenes = _container().report_use_cases.monthly_history(current_user_id())
    return jsonify(_serialize(resumenes))


@reports_bp.route("/api/historial/quincenal.json")
@login_required
def biweekly_history_json():
    resumenes = _container().report_use_cases.biweekly_history(current_user_id())
    return jsonify(_serialize(resumenes))


def _monto(por_categoria, category_value: str) -> float:
    for categoria, monto in por_categoria.items():
        if categoria.value == category_value:
            return monto
    return 0.0


def _serialize(resumenes):
    # Se invierte para mostrar cronológicamente en el gráfico (más antiguo -> más reciente)
    ordenado = list(reversed(resumenes))
    return {
        "labels": [r.label for r in ordenado],
        "necesidad": [_monto(r.por_categoria, "necesidad") for r in ordenado],
        "lujo": [_monto(r.por_categoria, "lujo") for r in ordenado],
        "ahorro": [_monto(r.por_categoria, "ahorro") for r in ordenado],
        "totales": [r.total for r in ordenado],
    }
