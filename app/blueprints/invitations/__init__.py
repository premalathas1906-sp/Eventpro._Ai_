from flask import Blueprint

invitations_bp = Blueprint('invitations', __name__, url_prefix='/invitations')

from app.blueprints.invitations import routes  # noqa: E402, F401
