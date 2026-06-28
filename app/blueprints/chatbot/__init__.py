from flask import Blueprint

chatbot_bp = Blueprint('chatbot', __name__)

from app.blueprints.chatbot import routes  # noqa: E402, F401
