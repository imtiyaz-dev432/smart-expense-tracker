
from dbms.db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False,unique=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile_no=db.Column(db.String(20),nullable=False,unique=True)
    password = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    categories=db.relationship("Category",back_populates="user",cascade="all, delete-orphan")
    expenses=db.relationship("Expense",back_populates="user",cascade="all, delete-orphan")
    incomes=db.relationship("Income",back_populates="user",cascade="all, delete-orphan")
    loans=db.relationship("Loan",back_populates="user",cascade="all, delete-orphan")
    borrows=db.relationship("Borrow",back_populates="user",cascade="all, delete-orphan")
    subscriptions = db.relationship("Subscription",back_populates="user",cascade="all, delete-orphan"
)
