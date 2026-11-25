
from flask import Blueprint, current_app, jsonify, request

from dbms.db import db
from models.user import User
from utils.extensions import redis_client
from utils.hashed import generate_otp, hash_otp, verify_hashed_otp
from utils.otp import send_otp_mail
from utils.rate import limiter

GENERIC = {"success": False, "message": "Invalid or expired OTP"}
otp_bp = Blueprint('otp', __name__, url_prefix='/otp')
@otp_bp.route('/verify-otp', methods=['POST'])
@limiter.limit("3 per minute")
def verify_otp():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body Is Required"
        }),400

    email = data.get('email')
    mobile_no = data.get("mobile_no")
    otp = data.get('otp')
    if not otp:
        return jsonify({"success":False,"message": "OTP is required"}), 400

    user = None

    if email:
        email=email.lower().strip()
        user = User.query.filter_by(email=email).first()
    elif mobile_no:
        mobile_no=mobile_no.strip()
        user = User.query.filter_by(mobile_no=mobile_no).first()
    else:
        return jsonify(GENERIC), 400

    if not user:
        return jsonify(GENERIC),400
    if user.is_verified is True:
       return jsonify(GENERIC),200
    otp_key=user.email
    try:
        stored_otp=redis_client.get(f"otp:verification:{otp_key}")
    except Exception:
        current_app.logger.warning("OTP:Redis is down during verifying otp")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500
    if not stored_otp:
        return jsonify(GENERIC),400
    if isinstance(stored_otp,bytes):
        stored_orp_hash=stored_otp.decode('utf-8')
    else:
        stored_orp_hash=stored_otp
    if not verify_hashed_otp(stored_orp_hash,otp):
        return jsonify(GENERIC),400
    try:
       user.is_verified = True
       db.session.commit()

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"OTP verification failed: {e!s}", exc_info=True)
        return jsonify({
            "success": False,
            "message": "Something went wrong. Please try again later."
        }), 500
    try:
        redis_client.delete(f"otp:verification:{otp_key}")
    except Exception:
        current_app.logger.exception(
            "OTP verify: Redis delete failed email=%s", email)

    return jsonify({
        "success": True,
        "message": "User verified successfully",
    }), 200


#resend otp
NEUTRAL = {"success": True, "message": "If the account exists, a verification OTP has been sent."}
@otp_bp.route("/resend-otp",methods=["POST"])
@limiter.limit("3 per minute")
def resend_otp():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    email = (data.get("email") or "").lower().strip()
    mobile_no = (data.get("mobile_no") or "").strip()
    if not mobile_no and not email:
        return jsonify({
            "success":False,
            "message":"Mobile no and email is required"
        }),400
    if email and mobile_no:
        user= User.query.filter_by(email=email,mobile_no=mobile_no).first()
    elif email:
        user= User.query.filter_by(email=email).first()
    elif mobile_no:
        user= User.query.filter_by(mobile_no=mobile_no).first()
    if not user:
        return jsonify(NEUTRAL),200
    if user.is_verified is True:
       return jsonify(NEUTRAL),200
    plain_otp=generate_otp()
    hashed_otp=hash_otp(plain_otp)
    otp_key=user.email
    try:
       redis_client.setex(f"otp:verification:{otp_key}", 300, str(hashed_otp))
    except Exception:
        current_app.logger.exception("Redis setex failed for %s", otp_key)
        return jsonify({"success": False, "message": "Something went wrong"}), 503

    try:
        send_otp_mail(user.email, plain_otp, purpose="verification")
    except Exception:
        redis_client.delete(f"otp:verification:{otp_key}")
        current_app.logger.exception("OTP email failed for %s", otp_key)
        return jsonify({"success": False, "message": "Failed to send OTP"}), 500

    return jsonify(NEUTRAL),200
