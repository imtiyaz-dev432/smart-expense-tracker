from dbms.db import db
from datetime import datetime

class Borrow(db.Model):
    __tablename__="borrows"
    id=db.Column(db.Integer,primary_key=True)
    person_name=db.Column(db.String(100),nullable=False)
    amount=db.Column(db.Float,nullable=False)
    type=db.Column(db.String(20),nullable=False)
    due_date=db.Column(db.DateTime,nullable=True)
    status=db.Column(db.String(30),default='pending')
    note=db.Column(db.String(100),nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
