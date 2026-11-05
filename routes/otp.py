from flask import Blueprint, request,jsonify
from dbms.db import db
from models.user import User
import random
import os
from datetime import datetime,timedelta
from utils.category_default import create_default_categories
from utils.hashed import verify_hashed_otp
from utils.otp import send_otp_mail
from utils.hashed import hash_otp,generate_otp



otp_bp = Blueprint('otp', __name__, url_prefix='/otp')
@otp_bp.route('/verify-otp', methods=['POST'])

def verify_otp():
    data = request.get_json()

    email = data.get('email')
    mobile_no = data.get("mobile_no")
    otp = data.get('otp')
    otp_type = data.get('type')

    if not otp:
        return jsonify({"message": "OTP is required"}), 400

    user = None

    if email:
        user = User.query.filter_by(email=email).first()
    elif mobile_no:
        user = User.query.filter_by(mobile_no=mobile_no).first()
    else:
        return jsonify({"message": "Email or mobile number is required"}), 400

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not user.otp:
        return jsonify({
            "message": "OTP not found. Please request a new OTP."
        }), 400

    

    if not verify_hashed_otp(user.otp, otp):
        return jsonify({"message": "Invalid OTP"}), 400

    if otp_type == "verification":
        user.is_verified = True

    user.otp = None
    


    db.session.commit()

    return jsonify({"message": "OTP verified successfully"}), 200

#resend otp
@otp_bp.route("/resend-otp",methods=["POST"])
def resend_otp():
    data=request.get_json()
    email=data.get("email")
    mobile_no=data.get('mobile_no')
    if not mobile_no and not email:
        return jsonify({
            "message":"Mobile no and email is required"
        }),400

    user = User.query.filter(
    (User.email == email) | (User.mobile_no == mobile_no)
).first()
    if not user:
        return jsonify({
            "message":"User not found"
        }),404
    
    plain_otp=generate_otp()
    user.otp=hash_otp(plain_otp)
    user.otp_created_at=datetime.utcnow()
    db.session.commit()
    db.session.refresh(user) 
    send_otp_mail(user.email, plain_otp, purpose="verification")
    return jsonify({
        "message":"Otp sent successfully"
    }),200
   