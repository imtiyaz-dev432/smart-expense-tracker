from dbms.db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'   # optional but good practice

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False,unique=True)

    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile_no=db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(200), nullable=False)

    otp = db.Column(db.String(255))
    otp_created_at=db.Column(db.DateTime)

    is_verified = db.Column(db.Boolean, default=False)
   