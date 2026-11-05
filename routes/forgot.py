from flask import Blueprint, request,jsonify
from dbms.db import db
from models.user import User
from werkzeug.security import generate_password_hash
import random
import os
from datetime import datetime,timedelta,timezone
from sqlalchemy import or_
from utils.otp import send_otp_mail
from utils.hashed import generate_otp,hash_otp,verify_hashed_otp
from utils.validators import is_valid_email,is_valid_mobile,is_valid_password
from utils.rate import limiter

forgot_bp=Blueprint("forgot-bp",__name__)


@forgot_bp.route("/forgot-password",methods=["POST"])
@limiter.limit("3 per minute")
def forgot_password():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    email=data.get("email")
    mobile_no=data.get("mobile_no")
    if not email and not mobile_no:
        return jsonify({"success":False,
        "message":"Either email or mobile no is required for forgetting password"}),400
    if email and mobile_no:
        return jsonify({
            "success":False,
            "message":"Only one field is required either email or mobile no"
        })    ,400
    if email:
        email=email.lower()
        if  not is_valid_email(email):
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            })  ,400
        user=User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                "success":False,
                "message":"If the account exists, a password reset OTP has been sent."
            })    ,200
    if mobile_no:
        if not is_valid_mobile(mobile_no):
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }),400
        user=User.query.filter_by(mobile_no=mobile_no).first()
        if not user:
            return jsonify  ({"success":False,
                "message":"If the account exists, a password reset OTP has been sent."
            })    ,200   
    
    plain_otp = generate_otp()
    hashed_otp = hash_otp(plain_otp)
    user.otp = hashed_otp
    print(plain_otp)
    user.otp_created_at = datetime.now(timezone.utc)
    db.session.commit()
    send_otp_mail(user.email, plain_otp, purpose="reset")
    return jsonify({
        "message": "Reset OTP sent to your registered email"
    }), 200


#reset password
@forgot_bp.route("/reset-password",methods=["POST"])
@limiter.limit("3 per minute")
def reset():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body Is required"
        }),400
    email=data.get("email")
    mobile_no=data.get("mobile_no")
    if not email and not mobile_no:
        return jsonify({"success":False,
        "message":"Either email or mobile no is required for forgetting password"}),400
    if email and mobile_no:
        return jsonify({
            "success":False,
            "message":"Only one field is required either email or mobile no"
        })    ,400
    if email:
        email=email.lower()
        if  not is_valid_email(email):
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            })  ,400
        user=User.query.filter_by(email=email).first()
        if not user:
            return jsonify({
                "success":False,
                "message":"Invalid credentials or OTP"
            })    ,400
    if mobile_no:
        if not is_valid_mobile(mobile_no):
            return jsonify({
                "success":False,
                "message":"Invalid Credentials"
            }),400
        user=User.query.filter_by(mobile_no=mobile_no).first()
        if not user:
            return jsonify  ({"success":False,
                "message":"Invalid credentials or OTP"
            })    ,400 

    otp = data.get("otp")
    new_password = data.get("new_password")
    if not otp or not new_password:
        return jsonify({
            "success":False,
            "message":"otp and password is required"
        }),400
    if not is_valid_password(new_password):
        return jsonify({
            "success":False,
             "message":"Password must be at least 8 characters long and include an"
              " uppercase letter, lowercase letter, number, and special"
              " character (@$!%*?&)" 
        }),400
  

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




