from datetime import datetime
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.application.dto import LoginInput, RegisterUserInput
from app.application.use_cases.auth_use_cases import (
    CredencialesInvalidasError,
    EmailYaRegistradoError,
)
from app.infrastructure.security.session_auth import (
    current_user_id,
    login_required,
    login_user_session,
    logout_user_session,
)

auth_bp = Blueprint("auth", __name__)


def _container():
    return current_app.config["CONTAINER"]


@auth_bp.route("/registro", methods=["GET", "POST"])
def register():
    if current_user_id() is not None:
        return redirect(url_for("expenses.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if password != password_confirm:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "error")
            return render_template("register.html")

        try:
            user = _container().auth_use_cases.register(
                RegisterUserInput(name=name, email=email, password=password)
            )
            login_user_session(user.id)
            flash("¡Cuenta creada! Ahora configura tu ingreso mensual.", "success")
            return redirect(url_for("auth.settings"))
        except EmailYaRegistradoError as e:
            flash(str(e), "error")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user_id() is not None:
        return redirect(url_for("expenses.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        try:
            user = _container().auth_use_cases.login(
                LoginInput(email=email, password=password)
            )
            login_user_session(user.id)
            return redirect(url_for("expenses.dashboard"))
        except CredencialesInvalidasError as e:
            flash(str(e), "error")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    logout_user_session()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/configuracion", methods=["GET", "POST"])
@login_required
def settings():
    user = _container().user_repository.get_by_id(current_user_id())

    if request.method == "POST":
        try:
            monthly_income = float(request.form.get("monthly_income", 0))
            month_year = request.form.get("month_year") 

            if monthly_income < 0:
                raise ValueError
            if not month_year:
                flash("Debes seleccionar un mes.", "error")
                return redirect(url_for("auth.settings"))
            
            user = _container().auth_use_cases.update_income(
                user.id, monthly_income, month_year
            )
            flash(f"Ingreso mensual para {month_year} actualizado correctamente.", "success")
        except ValueError:
            flash("Ingresa un número válido para el ingreso mensual.", "error")
            
    current_month = datetime.now().strftime("%Y-%m")

    historial_ingresos = _container().user_repository.get_income_history(user.id)
    
    return render_template(
        "settings.html", 
        user=user, 
        current_month=current_month,
        historial_ingresos=historial_ingresos
    )