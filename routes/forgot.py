from flask import Blueprint, request,jsonify
from dbms.db import db
from models.user import User
from werkzeug.security import generate_password_hash
import random
import os
from datetime import datetime,timedelta

forgot_bp=Blueprint("forgot-bp",__name__)
#Forgot password
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    if os.getenv("APP_ENV") == "development":
        print(f"Forgot OTP sent to email {email}: {otp}")


def send_otp_mobile(mobile_no, otp):
    if os.getenv("APP_ENV") == "development":
        print(f"Forgot OTP sent to mobile {mobile_no}: {otp}")

@forgot_bp.route("/forgot-password",methods=["POST"])
def forgot_password():
    data=request.get_json()
    identifier=data.get("identifier")

    if not identifier:
        return jsonify({
            "message":"Email or Mobile no is required"
        }),400

    
    user = User.query.filter(
    (User.email == identifier) | (User.mobile_no == identifier)
).first()
    if not user:
        return jsonify({
            "message":"User not found"
        }),404

    otp=generate_otp()
    user.otp=otp
    user.otp_created_at=datetime.utcnow()   
    db.session.commit()

    if identifier==user.email:
        send_otp_email(user.email,otp) 

    elif identifier==user.mobile_no:
        send_otp_mobile(user.mobile_no,otp)

    return jsonify({
        "message":"otp sent suessfully"
    })        ,200



#reset password

@forgot_bp.route("/reset-password",methods=["POST"])
def reset():
    data=request.get_json()
    identifier=data.get("identifier")    
    otp = data.get("otp")
    new_password = data.get("new_password")

   

    user = User.query.filter(
    (User.email == identifier) | (User.mobile_no == identifier)
).first()
    
   
    
    if not user:
        return {"message":"User not found"},404

    elif user.otp!=otp:
        return jsonify({
            "message":"Invalid otp"
        })    ,400
    
    elif not user.otp_created_at or datetime.utcnow()>user.otp_created_at+timedelta(minutes=3):
        return {"message":"Otp has been expired"},400 

    if not identifier or not otp or not new_password:
     return jsonify({
        "message": "Identifier, OTP and new password are required"
    }), 400
    user.password=generate_password_hash(new_password)
    user.otp=None
    user.otp_created_at = None
    db.session.commit()

    return jsonify({
    "message":"password updated successfully"})  ,200  




