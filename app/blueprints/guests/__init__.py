from flask import Blueprint

guests_bp = Blueprint('guests', __name__, template_folder='../../templates/guests', url_prefix='/guests')

from app.blueprints.guests import routes  # noqa: E402, F401
