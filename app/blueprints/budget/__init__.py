from flask import Blueprint

budget_bp = Blueprint('budget', __name__, template_folder='../../templates/budget', url_prefix='/budget')

from app.blueprints.budget import routes  # noqa: E402, F401
