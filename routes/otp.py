from flask import Blueprint, request,jsonify
from dbms.db import db
from models.user import User
import random
import os
from datetime import datetime,timedelta
from utils.category_default import create_default_categories


def generate_otp():
    return str(random.randint(100000, 999999))
otp_bp = Blueprint('otp', __name__, url_prefix='/otp')
@otp_bp.route('/verify-otp', methods=['POST'])

def verify_otp():
    data = request.get_json()

    email = data.get('email')
    mobile_no=data.get("mobile_no")
    otp = data.get('otp')
    otp_type=data.get('type') #otp has been generated for which purpose

    user=None
    if email:
        user=User.query.filter_by(email=email).first()

    elif mobile_no:
        user=User.query.filter_by(mobile_no=mobile_no).first()

    else:
        return{"message":"Email Or Mobile No is required"}    ,400

    if not user:
        return {"message":"user not found"}     ,404
    
    #otp check
    if user.otp !=otp:
        return{"message":"Invalid otp"} ,400

    #otp expiry check
    if not user.otp_created_at or datetime.utcnow()>user.otp_created_at+timedelta(minutes=3):
        return {"message":"Otp has been expired"},400 

    
    if otp_type=='register':
        user.is_verified=True
        create_default_categories(user.id)

    else:
     return jsonify({
        "message": "Invalid OTP type"
    }), 400   

    user.otp=None
    user.otp_created_at=None
    db.session.commit()
    
    return {"message":"otp verified successfully"},200

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
        }),400
    
    otp=generate_otp()
    user.otp=otp
    user.otp_created_at=datetime.utcnow()
    if os.getenv("APP_ENV") == "development":
      print("Register OTP:", otp)
    db.session.commit()
    db.session.refresh(user) #it refresh db
    return jsonify({
        "message":"Otp sent successfully"
    }),200
   