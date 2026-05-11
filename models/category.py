from dbms.db import db
from datetime import datetime

class Category(db.Model):
    __tablename__='category'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(120),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

