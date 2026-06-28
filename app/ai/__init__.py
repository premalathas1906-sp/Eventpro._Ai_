# app/ai/__init__.py
"""
AI Engine modules for EventPro AI.

This package contains the intelligent engines that power
the smart features of the application:

- ChatbotEngine:      NLP-based conversational assistant
- BudgetEngine:       Budget allocation & recommendation engine
- InvitationEngine:   Smart invitation template generator
- SentimentEngine:    Feedback sentiment analysis
"""

from app.ai.chatbot_engine import ChatbotEngine
from app.ai.budget_engine import BudgetEngine
from app.ai.invitation_engine import InvitationEngine
from app.ai.sentiment_engine import SentimentEngine

__all__ = [
    'ChatbotEngine',
    'BudgetEngine',
    'InvitationEngine',
    'SentimentEngine',
]
