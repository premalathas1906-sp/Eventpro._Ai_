from datetime import datetime
from app.extensions import db


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(20), default='Neutral')  # Positive, Neutral, Negative
    emoji = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def __repr__(self):
        return f'<Feedback from {self.guest_name} - {self.rating}/5>'
