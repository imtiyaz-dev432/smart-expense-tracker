from dbms.db  import db
from datetime import datetime

class Expense(db.Model):
    __tablename__="expenses"
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    amount=db.Column(db.Float(50),nullable=False)
    category=db.Column(db.String(50),nullable=False)
    description=db.Column(db.String(100),nullable=False)
    date=db.Column(db.DateTime,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id',),nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)