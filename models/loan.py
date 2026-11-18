from datetime import UTC, datetime

from dbms.db import db


class Loan(db.Model):
    __tablename__='loans'
    id=db.Column(db.Integer,primary_key=True)
    loan_name=db.Column(db.String(100),nullable=False)
    total_amount=db.Column(db.Numeric(12,2),nullable=False)
    monthly_emi=db.Column(db.Numeric(12,2),nullable=False)
    remaining_amount=db.Column(db.Numeric(12,2),nullable=False)
    due_date=db.Column(db.DateTime(timezone=True),nullable=False)
    status=db.Column(db.String(20),nullable=False,default="active")
    created_at=db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(UTC))
    user_id=db.Column(db.Integer,db.ForeignKey('users.id',ondelete="CASCADE"),nullable=False)
    user=db.relationship("User",back_populates="loans")
