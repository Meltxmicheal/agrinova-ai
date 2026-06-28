from flask import Flask
from config.config import Config
from app.extensions import db, bcrypt, jwt, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app.models.user import User
    from app.auth.routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app