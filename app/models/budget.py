from app.extensions import db


class BudgetItem(db.Model):
    __tablename__ = 'budget_items'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    allocated_amount = db.Column(db.Float, default=0.0)
    spent_amount = db.Column(db.Float, default=0.0)

    # Foreign key
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)

    @property
    def remaining(self):
        return self.allocated_amount - self.spent_amount

    @property
    def usage_percent(self):
        if self.allocated_amount == 0:
            return 0
        return round((self.spent_amount / self.allocated_amount) * 100, 1)

    def __repr__(self):
        return f'<BudgetItem {self.category}: ${self.spent_amount}/${self.allocated_amount}>'
