from app.extensions import db


class Vendor(db.Model):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Catering, Decoration, Photography, Music, Venue
    contact = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Contacted')  # Contacted, Confirmed, Paid
    rating = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Foreign key
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    def __repr__(self):
        return f'<Vendor {self.name} ({self.category})>'
