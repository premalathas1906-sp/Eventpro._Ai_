from flask import Blueprint

vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')

from app.blueprints.vendors import routes  # noqa: E402, F401
