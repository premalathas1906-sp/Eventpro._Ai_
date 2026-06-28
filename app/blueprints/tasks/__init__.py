from flask import Blueprint

tasks_bp = Blueprint('tasks', __name__, template_folder='../../templates/tasks', url_prefix='/tasks')

from app.blueprints.tasks import routes  # noqa: E402, F401
