from datetime import UTC, datetime

from dbms.db import db


class Expense(db.Model):
    __tablename__="expenses"
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    amount=db.Column(db.Numeric(12,2),nullable=False)
    description=db.Column(db.String(100),nullable=True)
    date=db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(UTC))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'),nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user=db.relationship("User",back_populates="expenses")
