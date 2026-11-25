from datetime import UTC, datetime

from dbms.db import db


class Borrow(db.Model):
    __tablename__="borrows"
    id=db.Column(db.Integer,primary_key=True)
    person_name=db.Column(db.String(100),nullable=False)
    amount=db.Column(db.Numeric(12,2),nullable=False)
    borrow_type=db.Column(db.String(20),nullable=False)
    due_date=db.Column(db.DateTime(timezone=True),nullable=True)
    status=db.Column(db.String(30),default='pending',nullable=False)
    note=db.Column(db.String(100),nullable=True)
    created_at=db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(UTC))
    user_id=db.Column(db.Integer,db.ForeignKey("users.id",ondelete='CASCADE'),nullable=False)
    user=db.relationship("User",back_populates="borrows")
