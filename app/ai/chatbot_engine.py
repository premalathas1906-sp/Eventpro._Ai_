# app/ai/chatbot_engine.py
"""
NLP Chatbot Engine for EventPro AI.

Uses TF-IDF vectorization and cosine similarity to classify user intents,
then queries the database for contextual, data-driven responses.
"""

import re
import string
from datetime import datetime, timedelta

import math
from collections import Counter


class ChatbotEngine:
    """
    Intent-based chatbot engine.

    Flow:
        1. Preprocess incoming message (lowercase, strip punctuation).
        2. Classify intent via TF-IDF cosine similarity against trained patterns.
        3. Extract entities (event names, dates) from the message.
        4. Optionally query the database for live data.
        5. Return a structured response dict with 'text' and optional 'data'.
    """

    # Confidence threshold – below this the fallback intent is used.
    CONFIDENCE_THRESHOLD = 0.20

    def __init__(self):
        """Initialise intents, vectorizer, and train the model."""

        self.intents = {
            "greeting": {
                "patterns": [
                    "hello", "hi", "hey", "good morning", "good afternoon",
                    "good evening", "howdy", "what's up", "hola",
                    "hi there", "hey there", "greetings",
                ],
                "responses": [
                    "Hello! 👋 I'm your EventPro AI assistant. How can I help you today?",
                    "Hi there! 🎉 Ready to help you plan something amazing. What do you need?",
                    "Hey! Great to see you. I can help with events, guests, budgets, and more!",
                ],
            },
            "farewell": {
                "patterns": [
                    "bye", "goodbye", "see you", "see ya", "take care",
                    "later", "farewell", "good night", "gotta go",
                ],
                "responses": [
                    "Goodbye! 👋 Happy planning!",
                    "See you later! Don't hesitate to come back if you need anything. 🎊",
                    "Take care! Your events are in good hands. ✨",
                ],
            },
            "event_count": {
                "patterns": [
                    "how many events", "total events", "my events",
                    "event count", "number of events", "events do i have",
                    "count my events", "list events",
                ],
                "responses": [],
            },
            "event_details": {
                "patterns": [
                    "tell me about", "event details", "when is",
                    "details of", "info about", "show event",
                    "what is the event", "describe event",
                    "event information", "about the event",
                ],
                "responses": [],
            },
            "guest_count": {
                "patterns": [
                    "how many guests", "guest count", "total guests",
                    "number of guests", "guests invited",
                    "how many people", "attendee count",
                    "how many attendees", "total invitees",
                ],
                "responses": [],
            },
            "attendance_status": {
                "patterns": [
                    "attendance", "who checked in", "attendance rate",
                    "check in status", "who attended", "attendance report",
                    "checked in guests", "who showed up",
                    "attendance stats", "attendance summary",
                ],
                "responses": [],
            },
            "budget_info": {
                "patterns": [
                    "budget", "how much spent", "budget remaining",
                    "total budget", "budget status", "spending",
                    "how much is left", "expenses", "budget overview",
                    "money spent", "budget summary",
                ],
                "responses": [],
            },
            "task_status": {
                "patterns": [
                    "tasks", "pending tasks", "what's left to do",
                    "task status", "incomplete tasks", "to do list",
                    "remaining tasks", "task progress", "completed tasks",
                    "overdue tasks", "task summary",
                ],
                "responses": [],
            },
            "vendor_info": {
                "patterns": [
                    "vendors", "who is catering", "photographer",
                    "vendor list", "vendor details", "service providers",
                    "caterer", "decorator", "dj", "entertainment vendor",
                    "vendor status", "booked vendors",
                ],
                "responses": [],
            },
            "help": {
                "patterns": [
                    "help", "what can you do", "features",
                    "capabilities", "commands", "options",
                    "how to use", "what do you do", "menu",
                    "show commands", "instructions",
                ],
                "responses": [
                    (
                        "I can help you with:\n"
                        "📊 **Event Stats** – \"How many events do I have?\"\n"
                        "👥 **Guest Info** – \"How many guests for my wedding?\"\n"
                        "✅ **Attendance** – \"What's the attendance rate?\"\n"
                        "💰 **Budget** – \"Budget status\" or \"How much spent?\"\n"
                        "📋 **Tasks** – \"Pending tasks\" or \"Task progress\"\n"
                        "🏢 **Vendors** – \"Vendor list\" or \"Who is catering?\"\n"
                        "📅 **Upcoming** – \"Next event\" or \"What's coming up?\"\n"
                        "🆕 **Create** – \"Create event\" or \"Plan an event\"\n\n"
                        "Just type naturally – I'll understand! 😊"
                    ),
                ],
            },
            "create_event": {
                "patterns": [
                    "create event", "new event", "plan an event",
                    "start planning", "make an event", "add event",
                    "organise an event", "organize event", "set up event",
                ],
                "responses": [
                    (
                        "Great idea! 🎉 To create a new event, head over to the "
                        "**My Events** page and click the **\"+ New Event\"** button.\n\n"
                        "You'll need:\n"
                        "• Event name & type\n"
                        "• Date, time & venue\n"
                        "• Expected guest count\n"
                        "• Budget (optional)\n\n"
                        "I'll help you with smart budget allocation and invitations once "
                        "the event is created!"
                    ),
                ],
            },
            "upcoming": {
                "patterns": [
                    "upcoming events", "next event", "what's coming up",
                    "future events", "events this week",
                    "events this month", "soon events",
                    "what's next", "scheduled events",
                ],
                "responses": [],
            },
        }

        self._train()

    # ── Training ────────────────────────────────────────────────────────
    def _train(self):
        """Fit TF-IDF vectorizer on all intent patterns."""
        self._labels: list[str] = []
        self._patterns: list[str] = []

        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data["patterns"]:
                self._patterns.append(self._preprocess(pattern))
                self._labels.append(intent_name)

        # Preprocess and tokenize all corpus documents
        self.doc_tokens = [self._tokenize(doc) for doc in self._patterns]
        # Build vocabulary
        self.vocab = list(set(word for doc in self.doc_tokens for word in doc))
        # Compute document frequencies
        df = Counter()
        for doc in self.doc_tokens:
            for word in set(doc):
                df[word] += 1
        # Compute IDFs
        N = len(self._patterns)
        self.idf = {word: math.log((1 + N) / (1 + df[word])) + 1 for word in self.vocab}
        # Compute TF-IDF vectors for all corpus documents
        self._tfidf_matrix = [self._get_tfidf(doc) for doc in self.doc_tokens]

    def _tokenize(self, text: str) -> list[str]:
        return text.lower().translate(str.maketrans("", "", string.punctuation)).split()

    def _get_tf(self, tokens: list[str]) -> dict:
        counts = Counter(tokens)
        length = len(tokens) or 1
        return {word: count / length for word, count in counts.items()}

    def _get_tfidf(self, tokens: list[str]) -> list[float]:
        tf = self._get_tf(tokens)
        vector = []
        for word in self.vocab:
            val = tf.get(word, 0) * self.idf.get(word, 0)
            vector.append(val)
        return vector

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    # ── Preprocessing ───────────────────────────────────────────────────
    @staticmethod
    def _preprocess(text: str) -> str:
        """Lowercase, strip punctuation, collapse whitespace."""
        text = text.lower().strip()
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = re.sub(r"\s+", " ", text)
        return text

    # ── Intent Classification ───────────────────────────────────────────
    def _classify(self, text: str) -> tuple[str, float]:
        """Return (intent_name, confidence) for the preprocessed *text*."""
        tokens = self._tokenize(text)
        if not tokens:
            return "fallback", 0.0
        vec = self._get_tfidf(tokens)
        
        best_score = 0.0
        best_label = "fallback"
        
        for score_idx, doc_vec in enumerate(self._tfidf_matrix):
            sim = self._cosine_similarity(vec, doc_vec)
            if sim > best_score:
                best_score = sim
                best_label = self._labels[score_idx]
                
        if best_score < self.CONFIDENCE_THRESHOLD:
            return "fallback", best_score
            
        return best_label, best_score

    # ── Entity Extraction ───────────────────────────────────────────────
    @staticmethod
    def _extract_entities(text: str) -> dict:
        """
        Lightweight entity extraction.

        Returns a dict that may contain:
            - 'event_name': a quoted string found in the message
            - 'date':       a date-like string (YYYY-MM-DD, DD/MM/YYYY, …)
        """
        entities: dict = {}

        # Quoted event names
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        if quoted:
            entities["event_name"] = quoted[0]

        # Date patterns
        date_match = re.search(
            r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}",
            text,
        )
        if date_match:
            entities["date"] = date_match.group()

        return entities

    # ── Database Helpers (imported lazily) ──────────────────────────────
    @staticmethod
    def _query_event_count(user_id: int) -> str:
        """Return a natural-language string with event counts for the user."""
        try:
            from app.models import Event

            total = Event.query.filter_by(user_id=user_id).count()
            upcoming = (
                Event.query
                .filter(Event.user_id == user_id, Event.date >= datetime.utcnow())
                .count()
            )
            past = total - upcoming
            return (
                f"📊 You have **{total}** event{'s' if total != 1 else ''} in total.\n"
                f"• 📅 Upcoming: **{upcoming}**\n"
                f"• ✅ Past: **{past}**"
            )
        except Exception:
            return "I couldn't fetch your event data right now. Please try again later."

    @staticmethod
    def _query_event_details(user_id: int, entities: dict) -> str:
        """Return details of a specific event (or the nearest upcoming one)."""
        try:
            from app.models import Event

            if "event_name" in entities:
                event = (
                    Event.query
                    .filter(
                        Event.user_id == user_id,
                        Event.name.ilike(f"%{entities['event_name']}%"),
                    )
                    .first()
                )
            else:
                event = (
                    Event.query
                    .filter(Event.user_id == user_id, Event.date >= datetime.utcnow())
                    .order_by(Event.date.asc())
                    .first()
                )

            if not event:
                return "I couldn't find a matching event. Try putting the event name in quotes, e.g. *\"My Wedding\"*."

            date_str = event.date.strftime("%B %d, %Y") if event.date else "TBD"
            return (
                f"🎯 **{event.name}**\n"
                f"• Type: {event.event_type}\n"
                f"• Date: {date_str}\n"
                f"• Venue: {event.venue or 'Not set'}\n"
                f"• Guests expected: {event.guest_count or 'N/A'}\n"
                f"• Budget: ₹{event.budget:,.0f}" if event.budget else ""
            )
        except Exception:
            return "I couldn't fetch event details right now. Please try again later."

    @staticmethod
    def _query_guest_count(user_id: int) -> str:
        """Return guest summary across all events."""
        try:
            from app.models import Event, Guest

            events = Event.query.filter_by(user_id=user_id).all()
            if not events:
                return "You don't have any events yet. Create one first! 🎉"

            lines = ["👥 **Guest Summary**\n"]
            total_guests = 0
            for ev in events:
                count = Guest.query.filter_by(event_id=ev.id).count()
                total_guests += count
                lines.append(f"• {ev.name}: **{count}** guest{'s' if count != 1 else ''}")

            lines.insert(1, f"Total across all events: **{total_guests}**\n")
            return "\n".join(lines)
        except Exception:
            return "I couldn't fetch guest data right now. Please try again later."

    @staticmethod
    def _query_attendance(user_id: int) -> str:
        """Return attendance / check-in statistics."""
        try:
            from app.models import Event, Guest

            events = Event.query.filter_by(user_id=user_id).all()
            if not events:
                return "No events found to report attendance for."

            lines = ["✅ **Attendance Report**\n"]
            for ev in events:
                guests = Guest.query.filter_by(event_id=ev.id).all()
                total = len(guests)
                checked = sum(1 for g in guests if g.checked_in)
                rate = (checked / total * 100) if total else 0
                lines.append(
                    f"• {ev.name}: **{checked}/{total}** checked in "
                    f"({rate:.0f}%)"
                )
            return "\n".join(lines)
        except Exception:
            return "I couldn't fetch attendance data right now. Please try again later."

    @staticmethod
    def _query_budget(user_id: int) -> str:
        """Return budget overview."""
        try:
            from app.models import Event, BudgetItem

            events = Event.query.filter_by(user_id=user_id).all()
            if not events:
                return "No events found to show budget for."

            lines = ["💰 **Budget Overview**\n"]
            for ev in events:
                items = BudgetItem.query.filter_by(event_id=ev.id).all()
                spent = sum(i.actual_cost or 0 for i in items)
                allocated = ev.budget or 0
                remaining = allocated - spent
                pct = (spent / allocated * 100) if allocated else 0
                lines.append(
                    f"• {ev.name}: ₹{spent:,.0f} / ₹{allocated:,.0f} "
                    f"({pct:.0f}% used) – ₹{remaining:,.0f} remaining"
                )
            return "\n".join(lines)
        except Exception:
            return "I couldn't fetch budget data right now. Please try again later."

    @staticmethod
    def _query_tasks(user_id: int) -> str:
        """Return task progress summary."""
        try:
            from app.models import Event, Task

            events = Event.query.filter_by(user_id=user_id).all()
            if not events:
                return "No events found to show tasks for."

            lines = ["📋 **Task Summary**\n"]
            for ev in events:
                tasks = Task.query.filter_by(event_id=ev.id).all()
                total = len(tasks)
                done = sum(1 for t in tasks if t.status == "Completed")
                pending = sum(1 for t in tasks if t.status == "Pending")
                progress = sum(1 for t in tasks if t.status == "In Progress")
                lines.append(
                    f"• {ev.name}: **{done}**✅ / **{progress}**🔄 / "
                    f"**{pending}**⏳  ({total} total)"
                )
            return "\n".join(lines)
        except Exception:
            return "I couldn't fetch task data right now. Please try again later."

    @staticmethod
    def _query_vendors(user_id: int) -> str:
        """Return vendor listing."""
        try:
            from app.models import Event, Vendor

            events = Event.query.filter_by(user_id=user_id).all()
            if not events:
                return "No events found to show vendors for."

            lines = ["🏢 **Vendor Summary**\n"]
            for ev in events:
                vendors = Vendor.query.filter_by(event_id=ev.id).all()
                if vendors:
                    lines.append(f"**{ev.name}**:")
                    for v in vendors:
                        status = "✅ Booked" if v.is_booked else "⏳ Pending"
                        lines.append(f"  • {v.name} ({v.service_type}) – {status}")
            return "\n".join(lines)
        except Exception:
            return "I couldn't fetch vendor data right now. Please try again later."

    @staticmethod
    def _query_upcoming(user_id: int) -> str:
        """Return upcoming events list."""
        try:
            from app.models import Event

            events = (
                Event.query
                .filter(Event.user_id == user_id, Event.date >= datetime.utcnow())
                .order_by(Event.date.asc())
                .limit(5)
                .all()
            )
            if not events:
                return "You have no upcoming events. Time to plan something! 🎉"

            lines = ["📅 **Upcoming Events**\n"]
            for ev in events:
                delta = (ev.date - datetime.utcnow()).days
                date_str = ev.date.strftime("%b %d, %Y")
                lines.append(
                    f"• **{ev.name}** – {date_str} "
                    f"({'today' if delta == 0 else f'in {delta} day' + ('s' if delta != 1 else '')})"
                )
            return "\n".join(lines)
        except Exception:
            return "I couldn't fetch upcoming events right now. Please try again later."

    # ── Main Response Handler ───────────────────────────────────────────
    def get_response(self, message: str, user_id: int | None = None) -> dict:
        """
        Process *message* and return a structured response.

        Parameters
        ----------
        message : str
            Raw user message.
        user_id : int | None
            Current user's database ID (for data queries).

        Returns
        -------
        dict
            ``{'text': str, 'intent': str, 'confidence': float, 'data': ... }``
        """
        import random

        intent, confidence = self._classify(message)
        entities = self._extract_entities(message)
        response_text = ""
        data = None

        # ── Static intents (no DB needed) ──────────────────────────────
        if intent in ("greeting", "farewell", "help", "create_event"):
            responses = self.intents[intent]["responses"]
            response_text = random.choice(responses) if responses else ""

        # ── Data-driven intents ────────────────────────────────────────
        elif intent == "event_count" and user_id:
            response_text = self._query_event_count(user_id)

        elif intent == "event_details" and user_id:
            response_text = self._query_event_details(user_id, entities)

        elif intent == "guest_count" and user_id:
            response_text = self._query_guest_count(user_id)

        elif intent == "attendance_status" and user_id:
            response_text = self._query_attendance(user_id)

        elif intent == "budget_info" and user_id:
            response_text = self._query_budget(user_id)

        elif intent == "task_status" and user_id:
            response_text = self._query_tasks(user_id)

        elif intent == "vendor_info" and user_id:
            response_text = self._query_vendors(user_id)

        elif intent == "upcoming" and user_id:
            response_text = self._query_upcoming(user_id)

        # ── Fallback ───────────────────────────────────────────────────
        else:
            response_text = (
                "🤔 I'm not sure I understood that. Here are some things you can ask me:\n\n"
                "• \"How many events do I have?\"\n"
                "• \"Budget status\"\n"
                "• \"Pending tasks\"\n"
                "• \"Guest count\"\n"
                "• \"Upcoming events\"\n\n"
                "Type **help** to see all my capabilities!"
            )
            intent = "fallback"

        return {
            "text": response_text,
            "intent": intent,
            "confidence": round(confidence, 3),
            "data": data,
        }
