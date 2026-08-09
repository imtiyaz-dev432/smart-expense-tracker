from dbms.db import db
from datetime import datetime

class Subscription(db.Model):
    __tablename__="subscriptiions"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    amount=db.Column(db.String(50),nullable=False)
    billing_cycle=db.Column(db.String(50),nullable=False)
    next_billing_date=db.Column(db.DateTime,nullable=False)
    status=db.Column(db.String(50),default='active')
    note=db.Column(db.String(150),nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)