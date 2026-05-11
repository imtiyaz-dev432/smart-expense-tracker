from dbms.db import db
from datetime import datetime

class Loan(db.Model):
    __tablename__='loans'
    id=db.Column(db.Integer,primary_key=True)
    loan_name=db.Column(db.String(100),nullable=False)
    total_amount=db.Column(db.Float,nullable=False)
    monthly_emi=db.Column(db.Float,nullable=False)
    remaining_amount=db.Column(db.Float,nullable=False)
    due_date=db.Column(db.DateTime,nullable=False)
    status=db.Column(db.String(100),nullable=False,default="active")
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
