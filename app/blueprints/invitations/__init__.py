from flask import Blueprint

invitations_bp = Blueprint('invitations', __name__, template_folder='../../templates/invitations', url_prefix='/invitations')

from app.blueprints.invitations import routes  # noqa: E402, F401
