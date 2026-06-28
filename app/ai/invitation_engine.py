# app/ai/invitation_engine.py
"""
Smart Invitation Generator for EventPro AI.

Provides 16 rich, personalised invitation templates across
4 event types × 4 tones (Formal, Casual, Elegant, Fun).
"""

from __future__ import annotations

from datetime import datetime


class InvitationEngine:
    """
    Generates personalised invitation content from curated templates.

    Usage::

        engine = InvitationEngine()
        invite = engine.generate(
            event_type='Wedding',
            tone='Elegant',
            guest_name='Priya Sharma',
            event_name="Raj & Meera's Wedding",
            date='2026-08-15',
            venue='The Grand Palace, Jaipur',
            host_name='The Sharma Family',
        )
    """

    # ════════════════════════════════════════════════════════════════════
    #  TEMPLATES – 4 event types × 4 tones = 16 templates
    # ════════════════════════════════════════════════════════════════════
    TEMPLATES: dict[str, dict[str, dict]] = {
        # ────────────── WEDDING ─────────────────────────────────────────
        "Wedding": {
            "Formal": {
                "heading": "You Are Cordially Invited",
                "greeting": "Dear {guest_name},",
                "body": (
                    "It is with great joy and immense pleasure that we request "
                    "the honour of your presence at the marriage celebration of "
                    "{event_name}.\n\n"
                    "As two souls unite in the sacred bond of matrimony, your "
                    "gracious presence would add immeasurable joy to this "
                    "momentous occasion. We would be deeply honoured to have "
                    "you share in our happiness."
                ),
                "details_prefix": "The ceremony will take place on:",
                "closing": (
                    "Kindly honour us with a response at your earliest convenience.\n\n"
                    "With warm regards and sincere affection,\n"
                    "{host_name}"
                ),
            },
            "Casual": {
                "heading": "We're Getting Married! 🎉",
                "greeting": "Hey {guest_name}!",
                "body": (
                    "Guess what? We're tying the knot and we can't imagine "
                    "celebrating without YOU! {event_name} is happening, "
                    "and it's going to be one heck of a party.\n\n"
                    "Come for the love, stay for the food and the dance floor. "
                    "We promise it'll be a day to remember!"
                ),
                "details_prefix": "Here's when and where:",
                "closing": (
                    "Drop us a message and let us know you're coming!\n\n"
                    "Can't wait to see you there,\n"
                    "{host_name}"
                ),
            },
            "Elegant": {
                "heading": "Together With Their Families",
                "greeting": "Dearest {guest_name},",
                "body": (
                    "With hearts brimming with love and gratitude, we invite "
                    "you to witness and celebrate the union of two hearts at "
                    "{event_name}.\n\n"
                    "In the golden glow of this auspicious day, your presence "
                    "would be the most cherished gift of all. Join us as we "
                    "embark on this beautiful journey of togetherness, surrounded "
                    "by the warmth of family and friends."
                ),
                "details_prefix": "Celebration details:",
                "closing": (
                    "We await the pleasure of your company.\n\n"
                    "With love and warm wishes,\n"
                    "{host_name}"
                ),
            },
            "Fun": {
                "heading": "Love Is in the Air! 💕✨",
                "greeting": "Yo {guest_name}! 🥳",
                "body": (
                    "POP THE CONFETTI! 🎊 {event_name} is officially happening, "
                    "and you're on the VIP guest list!\n\n"
                    "We're talking amazing food, killer dance moves, and probably "
                    "a few happy tears. This is THE event of the year and it "
                    "simply won't be the same without you. So clear your calendar, "
                    "put on your dancing shoes, and get ready to party!"
                ),
                "details_prefix": "Save this date or we'll be sad 👇",
                "closing": (
                    "RSVP ASAP so we can save you a seat (and extra dessert 🍰)!\n\n"
                    "All the love,\n"
                    "{host_name}"
                ),
            },
        },

        # ────────────── BIRTHDAY ────────────────────────────────────────
        "Birthday": {
            "Formal": {
                "heading": "Birthday Celebration Invitation",
                "greeting": "Dear {guest_name},",
                "body": (
                    "We cordially invite you to celebrate a milestone occasion — "
                    "{event_name}.\n\n"
                    "It would be a privilege and a delight to have you join us "
                    "as we honour this special day with an evening of fine dining, "
                    "heartfelt toasts, and cherished memories."
                ),
                "details_prefix": "Event details:",
                "closing": (
                    "We kindly request your response by the date indicated.\n\n"
                    "Warm regards,\n"
                    "{host_name}"
                ),
            },
            "Casual": {
                "heading": "You're Invited to a Birthday Bash! 🎂",
                "greeting": "Hey {guest_name}!",
                "body": (
                    "It's party time! 🥳 We're throwing a birthday celebration "
                    "for {event_name} and it just wouldn't be the same without you.\n\n"
                    "Expect great food, awesome music, and a whole lot of fun. "
                    "No fancy dress code — just bring your best self and your "
                    "appetite!"
                ),
                "details_prefix": "Here's the scoop:",
                "closing": (
                    "Let us know if you can make it!\n\n"
                    "Cheers,\n"
                    "{host_name}"
                ),
            },
            "Elegant": {
                "heading": "A Celebration of Another Beautiful Year",
                "greeting": "Dearest {guest_name},",
                "body": (
                    "As the calendar turns another page, we gather to celebrate "
                    "the wonderful person at the heart of {event_name}.\n\n"
                    "Your presence would add a touch of magic to an already "
                    "enchanting evening filled with laughter, fine cuisine, "
                    "and the joy of good company. Please join us for this "
                    "exquisite celebration."
                ),
                "details_prefix": "Celebration details:",
                "closing": (
                    "Kindly grace us with your response.\n\n"
                    "With affection,\n"
                    "{host_name}"
                ),
            },
            "Fun": {
                "heading": "🎈 PARTY ALERT! 🎈",
                "greeting": "What's up, {guest_name}! 🎉",
                "body": (
                    "CAKE! MUSIC! DANCING! 🕺💃 That's right — {event_name} is "
                    "going DOWN and you're officially invited!\n\n"
                    "We're talking a legendary birthday bash with all the works. "
                    "Bring your party energy and maybe a goofy gift (bonus points "
                    "for creativity). Let's make this one for the books!"
                ),
                "details_prefix": "Mark your calendar 📅",
                "closing": (
                    "Text back a 🎉 if you're in!\n\n"
                    "Party on,\n"
                    "{host_name}"
                ),
            },
        },

        # ────────────── COLLEGE EVENT ───────────────────────────────────
        "College Event": {
            "Formal": {
                "heading": "Official Invitation",
                "greeting": "Dear {guest_name},",
                "body": (
                    "The organising committee is pleased to extend this invitation "
                    "to {event_name}.\n\n"
                    "This event promises insightful sessions, networking opportunities, "
                    "and a platform for intellectual exchange. Your participation "
                    "would contribute greatly to the success of this endeavour."
                ),
                "details_prefix": "Programme details:",
                "closing": (
                    "Please confirm your attendance at your earliest convenience.\n\n"
                    "Respectfully,\n"
                    "{host_name}"
                ),
            },
            "Casual": {
                "heading": "You're Invited! 🎓",
                "greeting": "Hey {guest_name}!",
                "body": (
                    "Big things are happening on campus! 🚀 We're putting together "
                    "{event_name} and we'd love for you to be part of it.\n\n"
                    "Whether you want to learn something new, meet cool people, "
                    "or just have a good time — this is the place to be!"
                ),
                "details_prefix": "Details:",
                "closing": (
                    "Shoot us a reply if you're coming!\n\n"
                    "See you there,\n"
                    "{host_name}"
                ),
            },
            "Elegant": {
                "heading": "An Invitation to Excellence",
                "greeting": "Esteemed {guest_name},",
                "body": (
                    "We take great pleasure in inviting you to an evening of "
                    "knowledge, inspiration, and camaraderie at {event_name}.\n\n"
                    "This curated gathering brings together bright minds and "
                    "passionate individuals. Your presence would enrich the "
                    "experience and add to the vibrancy of discourse."
                ),
                "details_prefix": "Event particulars:",
                "closing": (
                    "We look forward to welcoming you.\n\n"
                    "With respect and anticipation,\n"
                    "{host_name}"
                ),
            },
            "Fun": {
                "heading": "🚀 Don't Miss This! 🚀",
                "greeting": "Yo {guest_name}! 👋",
                "body": (
                    "Campus is about to get LIT 🔥 because {event_name} is here!\n\n"
                    "Think workshops, competitions, free food (yes, FREE FOOD 🍕), "
                    "and an energy that's off the charts. Whether you're a nerd, "
                    "a socialite, or just hungry — there's something for everyone!"
                ),
                "details_prefix": "Here's the deets 👇",
                "closing": (
                    "Register now before spots fill up! 🏃‍♂️💨\n\n"
                    "Your fave organising committee,\n"
                    "{host_name}"
                ),
            },
        },

        # ────────────── CORPORATE ───────────────────────────────────────
        "Corporate": {
            "Formal": {
                "heading": "Invitation to {event_name}",
                "greeting": "Dear {guest_name},",
                "body": (
                    "On behalf of {host_name}, we are delighted to invite you to "
                    "{event_name}.\n\n"
                    "This event will feature keynote presentations, panel discussions, "
                    "and invaluable networking opportunities with industry leaders. "
                    "Your attendance would be a valued addition to this distinguished "
                    "gathering."
                ),
                "details_prefix": "Event details:",
                "closing": (
                    "Kindly confirm your attendance by responding to this invitation.\n\n"
                    "We look forward to your participation.\n\n"
                    "Best regards,\n"
                    "{host_name}"
                ),
            },
            "Casual": {
                "heading": "Join Us! 🤝",
                "greeting": "Hi {guest_name},",
                "body": (
                    "We're putting together {event_name} and think you'd be a "
                    "great fit for the crowd!\n\n"
                    "It's a chance to connect with peers, pick up new ideas, "
                    "and maybe even find your next big collaboration. Plus, "
                    "the refreshments are on us 😉"
                ),
                "details_prefix": "Here's the plan:",
                "closing": (
                    "Let us know if you can make it — we'd love to have you!\n\n"
                    "Best,\n"
                    "{host_name}"
                ),
            },
            "Elegant": {
                "heading": "A Distinguished Gathering Awaits",
                "greeting": "Dear {guest_name},",
                "body": (
                    "It is our privilege to extend a personal invitation to "
                    "{event_name}, an exclusive gathering designed to foster "
                    "meaningful connections and forward-thinking dialogue.\n\n"
                    "Curated with care, this event promises an atmosphere of "
                    "sophistication and substance. We believe your insights "
                    "and expertise would make for a remarkable contribution "
                    "to the proceedings."
                ),
                "details_prefix": "Engagement details:",
                "closing": (
                    "We sincerely hope to welcome you.\n\n"
                    "With high esteem,\n"
                    "{host_name}"
                ),
            },
            "Fun": {
                "heading": "Work Hard, Network Harder! 🎯🥂",
                "greeting": "Hey {guest_name}! 👋",
                "body": (
                    "Who says corporate events have to be boring? 😏 "
                    "{event_name} is flipping the script!\n\n"
                    "Think TED-talk vibes meets after-party energy. Great talks, "
                    "awesome people, and yes — an open bar. Come for the insights, "
                    "stay for the connections (and the cocktails 🍸)."
                ),
                "details_prefix": "Block your calendar 📅",
                "closing": (
                    "RSVP now and bring your business cards (and your A-game)!\n\n"
                    "The Events Team,\n"
                    "{host_name}"
                ),
            },
        },
    }

    # ════════════════════════════════════════════════════════════════════
    #  Public API
    # ════════════════════════════════════════════════════════════════════
    def generate(
        self,
        event_type: str,
        tone: str,
        guest_name: str,
        event_name: str,
        date: str,
        venue: str,
        host_name: str | None = None,
        custom_message: str | None = None,
        time: str | None = None,
    ) -> dict:
        """
        Generate a personalised invitation.

        Parameters
        ----------
        event_type : str
            One of 'Wedding', 'Birthday', 'College Event', 'Corporate'.
        tone : str
            One of 'Formal', 'Casual', 'Elegant', 'Fun'.
        guest_name : str
            Name of the invited guest.
        event_name : str
            Name / title of the event.
        date : str
            Event date (any string format; will be prettified if ISO).
        venue : str
            Venue name / address.
        host_name : str | None
            Host or organiser name (defaults to 'The Hosts').
        custom_message : str | None
            Optional extra paragraph to append before the closing.
        time : str | None
            Event time string (e.g. '6:00 PM').

        Returns
        -------
        dict
            Keys: heading, greeting, body, details, closing, full_text.
        """
        host_name = host_name or "The Hosts"
        pretty_date = self._prettify_date(date)
        time_str = time or "To be announced"

        # Resolve template (with graceful fallback)
        type_templates = self.TEMPLATES.get(event_type, self.TEMPLATES["Corporate"])
        template = dict(type_templates.get(tone, type_templates["Formal"]))

        # Substitution context
        ctx = {
            "guest_name": guest_name,
            "event_name": event_name,
            "host_name": host_name,
        }

        heading = template["heading"].format(**ctx)
        greeting = template["greeting"].format(**ctx)
        body = template["body"].format(**ctx)

        # Build details block
        details_prefix = template.get("details_prefix", "Event details:")
        details = (
            f"{details_prefix}\n"
            f"📅  Date: {pretty_date}\n"
            f"🕐  Time: {time_str}\n"
            f"📍  Venue: {venue}"
        )

        # Append custom message if provided
        if custom_message:
            body += f"\n\n✉️ {custom_message}"

        closing = template["closing"].format(**ctx)

        # Full text concatenation
        full_text = (
            f"{heading}\n\n"
            f"{greeting}\n\n"
            f"{body}\n\n"
            f"{details}\n\n"
            f"{closing}"
        )

        return {
            "heading": heading,
            "greeting": greeting,
            "body": body,
            "details": details,
            "closing": closing,
            "full_text": full_text,
        }

    def get_available_tones(self, event_type: str) -> list[str]:
        """Return available tone options for the given event type."""
        type_templates = self.TEMPLATES.get(event_type, {})
        return list(type_templates.keys())

    def get_available_event_types(self) -> list[str]:
        """Return all supported event types."""
        return list(self.TEMPLATES.keys())

    # ── Helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _prettify_date(date_str: str) -> str:
        """Attempt to convert an ISO-ish date string to a human-friendly one."""
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%A, %B %d, %Y")
            except (ValueError, AttributeError):
                continue
        # If parsing fails, return the original string
        return date_str
