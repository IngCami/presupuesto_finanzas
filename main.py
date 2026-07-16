from flask import Flask

from app.container import Container
from app.presentation.web.routes.auth_routes import auth_bp
from app.presentation.web.routes.expense_routes import expenses_bp
from app.presentation.web.routes.report_routes import reports_bp
from config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(
        __name__,
        template_folder="app/presentation/web/templates",
        static_folder="app/presentation/web/static",
    )
    app.config.from_object(config_class)

    container = Container(app.config["DB_PATH"])
    app.config["CONTAINER"] = container

    app.register_blueprint(auth_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(reports_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
