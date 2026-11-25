import time

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from dbms.db import db
from models.user import User
from utils.category_default import create_default_categories
from utils.extensions import redis_client
from utils.hashed import generate_otp, hash_otp
from utils.otp import send_otp_mail
from utils.rate import get_contact_identity, get_ip_identity, get_login_identity, limiter
from utils.validators import is_valid_email, is_valid_mobile, is_valid_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3 per minute",key_func=get_contact_identity,scope="register-contact-ip",override_defaults=False)
@limiter.limit("5 per hour",key_func=get_ip_identity,scope="register-ip",override_defaults=False)
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    username = data.get('username')
    email = data.get('email')
    mobile_no=data.get('mobile_no')
    password = data.get('password')
    if not username or not  email  or not mobile_no or not password:
        return jsonify({
            "success":False,
            "message":"All fields are required"
        }),400
    email=email.strip().lower()
    mobile_no=mobile_no.strip()
    if not is_valid_email(email):
        return jsonify({
            "success":False,
            "message":"Invalid Email"
        }) ,400
    if not is_valid_mobile(mobile_no):
        return jsonify({
            "success":False,
            "message":"Invalid Mobile No.."
        })  ,400
    if not is_valid_password(password):
        return jsonify({
            "success":False,
            "message":"Password must be at least 8 characters long and include an"
              " uppercase letter, lowercase letter, number, and special"
              " character (@$!%*?&)"
        }) ,400
    if User.query.filter_by(email=email).first():
        return {"success":False,"message": "User already exists"}, 409

    if User.query.filter_by(username=username).first():
        return {"success":False,"message": "User already exists"}, 409

    if User.query.filter_by(mobile_no=mobile_no).first():
        return {"success":False,"message": "User already exists"}, 409

    hashed_password = generate_password_hash(password)
    plain_otp = generate_otp()
    hashed_otp = hash_otp(plain_otp)

    try:
      redis_client.setex(
        f"otp:verification:{email}",
        300,
        str(hashed_otp)
    )
    except Exception:
        current_app.logger.warning("Redis is Down")
        return jsonify({
            "success":False,
            "message":"Some thing went wrong"
        }),503
    new_user = User(
        username=username,
        email=email,
        mobile_no=mobile_no,
        password=hashed_password,
        is_verified=False
    )

    db.session.add(new_user)
    db.session.flush()
    create_default_categories(new_user)
    otp_sent=False
    try:
      db.session.commit()
    except IntegrityError:
        db.session.rollback()
        redis_client.delete(f"otp:verification:{email}")
        current_app.logger.warning("Register: duplicate race email=%s mobile=%s", email, mobile_no)
        return jsonify({
            "success": False,
            "message": "Email or mobile number is already registered"
        }), 409
    except Exception:
        db.session.rollback()
        redis_client.delete(f"otp:verification:{email}")
        current_app.logger.exception("Register: DB commit failed email=%s", email)
        return jsonify({
        "success": False,
        "message": "Internal Server Error"
    }), 500
    try:
       send_otp_mail(email, plain_otp, purpose="verification")
       otp_sent=True
    except Exception :
        current_app.logger.exception(
        "Error in sending otp")

    return {"message": "User registered successfully","otp_sent":otp_sent}, 201

#Login
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("3 per minute", key_func=get_ip_identity,scope="login-ip",override_defaults=False
)
@limiter.limit("5 per minute",key_func=get_login_identity,scope="login-user",override_defaults=False)

def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {"message": "Username and password are required"}, 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
       return {"success": False, "message": "Invalid credentials"}, 401

    if not user.is_verified:
        return {"message": "Please verify your OTP before login"}, 403

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return {
        "message": "Login successful",
        "token": access_token,
        "refresh_token":refresh_token,
        "id": user.id,
    }, 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    user=db.session.get(User,int(current_user_id))
    if not user:
        return {"success": False, "message": "Account not found"}, 401
    if not user.is_verified:
        return {"success": False, "message": "Account not verified"}, 403

    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({
        "access_token": new_access_token
    }), 200
#logout
@auth_bp.route("/logout",methods=["POST"])
@jwt_required(refresh=True)
def logout():
    refresh_token = get_jwt()
    refresh_jti = refresh_token["jti"]
    refresh_sub = refresh_token["sub"]
    now = int(time.time())

    data = request.get_json(silent=True) or {}
    access_token = data.get("access_token")

    if access_token:
        if not isinstance(access_token, str):
            return jsonify({"success": False, "message": "Invalid access token format"}), 400

        try:
            decoded = decode_token(access_token)

            if decoded.get("type") != "access":
                return jsonify({"success": False, "message": "Token is not an access token"}), 400

            if decoded.get("sub") != refresh_sub:
                current_app.logger.warning(
                    "Logout ownership mismatch: refresh_sub=%s, access_sub=%s",
                    refresh_sub,
                    decoded.get("sub"),
                )
                return jsonify({"success": False, "message": "Token ownership mismatch"}), 403

            access_jti = decoded["jti"]
            access_ttl = max(decoded["exp"] - now, 1)
            redis_client.setex(f"blacklist:{access_jti}", access_ttl, "revoked")

        except Exception:
            return jsonify({"success": False, "message": "Invalid access token"}), 400

    refresh_ttl = max(refresh_token["exp"] - now, 1)
    redis_client.setex(f"blacklist:{refresh_jti}", refresh_ttl, "revoked")

    return jsonify({
        "success": True,
        "message": "User logged out successfully"
    }), 200
