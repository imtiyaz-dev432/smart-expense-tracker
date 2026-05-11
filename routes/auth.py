from flask import Blueprint, request
from dbms.db import db
from models.user import User
from werkzeug.security import generate_password_hash,check_password_hash
import random
import os
from datetime import datetime
from flask_jwt_extended import create_access_token,jwt_required,get_jwt
from block import BLOCKLIST
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    mobile_no=data.get('mobile_no')
    password = data.get('password')

    if User.query.filter_by(email=email).first():
        return {"message": "User already exists"}, 400

    elif User.query.filter_by(username=username).first():
        return {"message": "User already exists"}, 400    

    elif User.query.filter_by(mobile_no=mobile_no).first():
        return {"message": "User already exists"}, 400    

    hashed_password = generate_password_hash(password)
    otp = str(random.randint(100000, 999999))

    new_user = User(
        username=username,
        email=email,
        mobile_no=mobile_no,
        password=hashed_password,
        otp=otp,
        otp_created_at=datetime.utcnow(),
        is_verified=False
    )

    db.session.add(new_user)
    db.session.commit()

    if os.getenv("APP_ENV") == "development":
      print("Register OTP:", otp)
    

    return {"message": "User registered successfully"}, 201


#Login
@auth_bp.route("/login",methods=['POST'])
def login():
    data=request.get_json()
    username=data.get('username')
    password=data.get('password')    
    user = User.query.filter_by(username=username).first()
    if not username:
        return {"message":"Invalid Username"},401

    check=check_password_hash(user.password,password)

    if not check:
        return {"messsage":"Invalid Password"},401
    
    acces_token=create_access_token(identity=str(user.id))


    return {"message":"Login Successfull",
    "token":acces_token,
            "id":user.id,
             "email":user.email,
             "Mobile_no":user.mobile_no}   ,200 

#logout
@auth_bp.route("/logout",methods=["POST"])
@jwt_required()
def logout():
    jti=get_jwt()['jti']
    BLOCKLIST.add(jti)
    return{"message":"Loggesd out successfull"},200

