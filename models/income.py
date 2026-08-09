from dbms.db import db
from datetime import datetime

class Income(db.Model):
    __tablename__='incomes'
    id=db.Column(db.Integer,primary_key=True)
    source=db.Column(db.String(100),nullable=False)
    amount=db.Column(db.Float,nullable=False)
    description=db.Column(db.String(200))
    date=db.Column(db.DateTime,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)