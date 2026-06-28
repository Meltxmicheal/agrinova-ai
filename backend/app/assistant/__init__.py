from flask import Blueprint

assistant_bp = Blueprint("assistant", __name__)

from . import routes
