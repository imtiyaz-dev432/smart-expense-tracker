from flask import Blueprint, request,jsonify
from dbms.db import db
from models.user import User
from werkzeug.security import generate_password_hash,check_password_hash
import random
import os
from datetime import datetime
from flask_jwt_extended import create_access_token,jwt_required,get_jwt,create_refresh_token,get_jwt_identity
from block import BLOCKLIST
from utils.otp import send_otp_mail
from utils.hashed import generate_otp,hash_otp
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
    plain_otp = generate_otp()
    hashed_otp = hash_otp(plain_otp)

    new_user = User(
        username=username,
        email=email,
        mobile_no=mobile_no,
        password=hashed_password,
        otp=hashed_otp,
        otp_created_at=datetime.utcnow(),
        is_verified=False
    )
    
    db.session.add(new_user)
    db.session.commit()
    send_otp_mail(email, plain_otp, purpose="verification")
    return {"message": "User registered successfully"}, 201


#Login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "Username and password are required"}, 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return {"message": "Invalid username"}, 401

    if not check_password_hash(user.password, password):
        return {"message": "Invalid password"}, 401

    if not user.is_verified:
        return {"message": "Please verify your OTP before login"}, 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return {
        "message": "Login successful",
        "token": access_token,
        "refresh_token":refresh_token,
        "id": user.id,
        "email": user.email,
        "mobile_no": user.mobile_no
    }, 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()

    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({
        "access_token": new_access_token
    }), 200    
#logout
@auth_bp.route("/logout",methods=["POST"])
@jwt_required()
def logout():
    jti=get_jwt()['jti']
    BLOCKLIST.add(jti)
    return{"message":"Loggesd out successfull"},200

