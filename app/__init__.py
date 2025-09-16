from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import get_config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .models import User  # noqa: F401 ensure model registration

    from .auth.routes import auth_bp
    from .main.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

