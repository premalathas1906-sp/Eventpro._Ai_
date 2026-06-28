from datetime import datetime
from app.extensions import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # Conference, Wedding, Birthday, etc.
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    venue = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Float, default=0.0)
    guest_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Draft')  # Active, Upcoming, Completed, Draft
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    guests = db.relationship('Guest', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    vendors = db.relationship('Vendor', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    feedback_items = db.relationship('Feedback', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    budget_items = db.relationship('BudgetItem', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    reminders = db.relationship('Reminder', backref='event', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Event {self.name}>'
