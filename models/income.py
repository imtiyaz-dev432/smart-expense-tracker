from datetime import UTC, datetime

from dbms.db import db


class Income(db.Model):
    __tablename__='incomes'
    id=db.Column(db.Integer,primary_key=True)
    source=db.Column(db.String(100),nullable=False)
    amount=db.Column(db.Numeric(12,2),nullable=False)
    description=db.Column(db.String(200))
    date=db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(UTC))
    user_id=db.Column(db.Integer,db.ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    user=db.relationship("User",back_populates="incomes")
