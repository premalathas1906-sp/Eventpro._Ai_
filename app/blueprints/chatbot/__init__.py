from flask import Blueprint

chatbot_bp = Blueprint('chatbot', __name__, template_folder='../../templates/chatbot')

from app.blueprints.chatbot import routes  # noqa: E402, F401
