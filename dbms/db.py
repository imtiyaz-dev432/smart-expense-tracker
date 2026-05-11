from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()

# class User(db.Model):
#     __tablename__='user'
#     id=db.Column(db.Integer,primary_key=True)
#     username=db.Column(db.String(100),unique=True,nullable=False)
#     password=db.Column(db.String(200),nullable=False)
#     phone = db.Column(db.String(15), unique=True, nullable=False)
#     email=db.Column(db.String(150),unique=True,nullable=False)
#     is_verified = db.Column(db.Boolean, default=False)
#     otp = db.Column(db.String(6))
#     otp_created_at = db.Column(db.DateTime, default=datetime.utcnow) #utcnow for date time

#     #db.model treated python classes like table
# class Expense(db.Model):
#     __tablename__='expense'
#     id=db.Column(db.Integer,primary_key=True)
#     title=db.Column(db.String(100),nullable=False)
#     amount=db.Column(db.Float,nullable=False)
#     date=db.Column(db.DateTime,nullable=False)
#     user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
#     category_id=db.Column(db.Integer,db.ForeignKey('category.id'))

# class Category(db.Model):
#     __tablename__='category'  
#     id=db.Column(db.Integer,primary_key=True)
#     name=db.Column(db.String(100),unique=True,nullable=False)
#     description=db.Column(db.String(200))
#     expenses=db.relationship('Expense',backref='category',lazy=True) #lazy load related only when needed and backref cretaes reverse link
    
