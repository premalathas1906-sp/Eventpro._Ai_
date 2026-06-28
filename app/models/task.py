from datetime import datetime
from app.extensions import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='To Do')  # To Do, In Progress, Completed
    priority = db.Column(db.String(10), default='Medium')  # High, Medium, Low
    assigned_to = db.Column(db.String(100), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def __repr__(self):
        return f'<Task {self.title}>'
