from datetime import UTC, datetime

from dbms.db import db


class Subscription(db.Model):
    __tablename__="subscriptions"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    amount=db.Column(db.Numeric(12,2),nullable=False)
    billing_cycle=db.Column(db.String(30),nullable=False)
    next_billing_date=db.Column(db.DateTime(timezone=True),nullable=False)
    status=db.Column(db.String(30),default='active',nullable=False)
    note=db.Column(db.String(100),nullable=True)
    created_at=db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(UTC))
    user_id=db.Column(db.Integer,db.ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    user=db.relationship("User",back_populates="subscriptions")