from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import generate_password_hash

from dbms.db import db
from models.user import User
from utils.extensions import redis_client
from utils.hashed import generate_otp, hash_otp, verify_hashed_otp
from utils.otp import send_otp_mail
from utils.rate import limiter
from utils.validators import is_valid_email, is_valid_mobile, is_valid_password

NEUTRAL = {"success": True, "message": "If the account exists, a password reset OTP has been sent."}
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
        email=email.strip().lower()
        if  not is_valid_email(email):
            return jsonify({
                "success":False,
                "message":"Invalid email format"
            })  ,400
        user=User.query.filter_by(email=email).first()

    if mobile_no:
        mobile_no=mobile_no.strip()
        if not is_valid_mobile(mobile_no):
            return jsonify({
                "success":False,
                "message":"Invalid mobile no.. format"
            }),400
        user=User.query.filter_by(mobile_no=mobile_no).first()
    if not user:
       return jsonify(NEUTRAL),200
    plain_otp = generate_otp()
    hashed_otp = hash_otp(plain_otp)
    try:
        redis_client.setex(f"otp:reset:{user.email}",300,str(hashed_otp))
    except Exception:
        current_app.logger.exception("OTP:Redis is Down")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }) ,500
    try:
       send_otp_mail(user.email, plain_otp, purpose="reset")
    except Exception :
        redis_client.delete(f"otp:reset:{user.email}")
        current_app.logger.exception(
        "Error in sending otp")
        return jsonify({
          "success":False,
          "message":"Error in sending mail"
        }),500

    return jsonify(NEUTRAL),200

#reset password
@forgot_bp.route("/reset-password",methods=["POST"])
@limiter.limit("3 per minute")
def reset():
    GENERIC_FAIL = {"success": False, "message": "Invalid credentials or OTP"}
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
        email=email.strip().lower()
        if  not is_valid_email(email):
            return jsonify(GENERIC_FAIL),400
        user=User.query.filter_by(email=email).first()
        if not user:
            return jsonify  (GENERIC_FAIL)    ,400
    if mobile_no:
        mobile_no=mobile_no.strip()
        if not is_valid_mobile(mobile_no):
            return jsonify(
                GENERIC_FAIL
            ),400
        user=User.query.filter_by(mobile_no=mobile_no).first()
        if not user:
            return jsonify  (GENERIC_FAIL),400


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
    try:
        stored_otp=redis_client.get(f"otp:reset:{user.email}")
    except Exception:
        current_app.logger.warning("OTP:Redis is down during verifying otp")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500
    if not stored_otp:
       return jsonify(GENERIC_FAIL),400


    if isinstance(stored_otp,bytes):
        stored_otp_hash=stored_otp.decode('utf-8')
    else:
        stored_otp_hash=stored_otp

    if not verify_hashed_otp(stored_otp_hash,otp):
        return jsonify(GENERIC_FAIL),400
    try:
       user.password = generate_password_hash(new_password)
       db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Password set to  be failed")
        return jsonify({
            "success":False,
            "message":"Reset Password is failed"
        }) ,500
    try:
        redis_client.delete(f"otp:reset:{user.email}")
    except Exception:
        current_app.logger.exception("OTP delete failed for %s", user.email)
    return jsonify({
     "success":True,
    "message": "Password reset successfully"
}), 200

