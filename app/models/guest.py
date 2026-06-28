import uuid
from datetime import datetime
from app.extensions import db


class Guest(db.Model):
    __tablename__ = 'guests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    rsvp_status = db.Column(db.String(20), default='Pending')  # Confirmed, Pending, Declined
    checked_in = db.Column(db.Boolean, default=False)
    check_in_time = db.Column(db.DateTime, nullable=True)
    qr_token = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))

    # Foreign key
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def __repr__(self):
        return f'<Guest {self.name}>'
