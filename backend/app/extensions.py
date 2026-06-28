from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()

# Translation filter setup
import json
import os

_translations_path = os.path.join(os.path.dirname(__file__), 'translations.json')
with open(_translations_path, 'r', encoding='utf-8') as f:
    _translations = json.load(f)

def t_filter(text):
    """Translate text based on the 'lang' cookie. Defaults to English."""
    from flask import request
    lang = request.cookies.get('lang', 'en')
    return _translations.get(lang, {}).get(text, text)

def init_app(app):
    app.jinja_env.filters['t'] = t_filter