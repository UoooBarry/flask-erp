from flask import Flask
from config import config
from app.extensions import db, migrate, jwt
from app.routes.auth import auth_bp
from app.utils.error_handlers import register_error_handlers


def create_app(config_name="default"):
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app import models as _

    app.register_blueprint(auth_bp, url_prefix="/auth")
    register_error_handlers(app)

    return app
