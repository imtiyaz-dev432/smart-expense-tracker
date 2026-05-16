from flask import Blueprint, request,jsonify
from dbms.db import db
from models.user import User
from werkzeug.security import generate_password_hash
import random
import os
from datetime import datetime,timedelta
from sqlalchemy import or_
from utils.otp import send_otp_mail
from utils.hashed import generate_otp,hash_otp,verify_hashed_otp

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

    plain_otp = generate_otp()
    hashed_otp = hash_otp(plain_otp)

    user.otp = hashed_otp
    user.otp_created_at = datetime.utcnow()

    db.session.commit()

    send_otp_mail(user.email, plain_otp, purpose="reset")

    return jsonify({
        "message": "Reset OTP sent to your registered email"
    }), 200


#reset password

@forgot_bp.route("/reset-password",methods=["POST"])
def reset():
    data=request.get_json()
    identifier = data.get("identifier")
    otp = data.get("otp")
    new_password = data.get("new_password")
  
    if not identifier or not otp or not new_password:
     return jsonify({"message": "All fields are required"}), 400

    user = User.query.filter(
    or_(
        User.email == identifier,
        User.mobile_no == identifier
    )
).first()

    if not user:
     return jsonify({"message": "User not found"}), 404

    if not user.otp or not user.otp_created_at:
     return jsonify({"message": "OTP not generated"}), 400

    if datetime.utcnow() > user.otp_created_at + timedelta(minutes=5):
      return jsonify({"message": "OTP expired. Please request a new OTP."}), 400

    if not verify_hashed_otp(user.otp, otp):
      return jsonify({"message": "Invalid OTP"}), 400

    user.password = generate_password_hash(new_password)
    user.otp = None
    user.otp_created_at = None

    db.session.commit()

    return jsonify({
    "message": "Password reset successfully"
}), 200 




