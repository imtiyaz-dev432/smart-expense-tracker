from datetime import UTC, datetime, timedelta

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dbms.db import db
from models.subscribe import Subscription
from utils.rate import limiter

subscribe_bp=Blueprint("subscribe_bp",__name__)
@subscribe_bp.route("/subscription/add", methods=["POST"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def add_subscription():
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    name = (data.get("name") or '').strip()
    raw_amount = data.get("amount")
    try:
        amount=float(raw_amount) if raw_amount  is not None else None
    except (ValueError,TypeError):
        return jsonify({
            "success":False,
            "message":"Amount must be positive"
        })    ,400
    billing_cycle = data.get("billing_cycle")
    next_billing_date = data.get("next_billing_date")
    note = data.get("note")
    if not name or amount is None or not billing_cycle or not next_billing_date :
        return jsonify({
            "success":False,
            "message": "Name, amount, billing cycle and next billing date are required"
        }), 400
    if note and len(note)>100:
        return jsonify({
            "success":False,
            "message":"Note too long (max 100 char)"
        }) ,400
    if len(name) > 100:
       return jsonify({"success": False, "message": "Name too long (max 100 chars)"}), 400

    if amount<=0:
        return jsonify({
            "success":False,
            "message":"Amount must be greater than zero"
        }),400
    billing_cycle =str(billing_cycle).strip().lower()
    if billing_cycle not in ["monthly", "yearly", "weekly"]:
          return jsonify({
            "success":False,
            "message": "Billing cycle must be monthly, yearly or weekly"
        }), 400

    try:
       next_billing_date_obj = datetime.strptime(next_billing_date, "%Y-%m-%d").replace(tzinfo=UTC)
       if next_billing_date_obj <= datetime.now(UTC):
                return jsonify({"success": False, "message": "next_billing_date must be in the future"}), 400
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "next_billing_date must be YYYY-MM-DD"}), 400
    try:
        new_subscription = Subscription(
        name=name,
        amount=amount,
        billing_cycle=billing_cycle,
        next_billing_date=next_billing_date_obj,
        note=note,
        user_id=current_user_id
    )

        db.session.add(new_subscription)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit is failed")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500
    return jsonify({
        "success":True,
        "message": "Subscription added successfully"
    }), 201


#get subscription
@subscribe_bp.route("/subscription/get",methods=["GET"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def get__subscription():
    current_user_id=int(get_jwt_identity())
    subscribes=Subscription.query.filter_by(
        user_id=current_user_id
    ).order_by(Subscription.next_billing_date.asc()).all()

    subscription_list=[]

    for subscribe in subscribes:
        subscription_list.append({
            "id":subscribe.id,
            "name":subscribe.name,
            "amount":float(subscribe.amount),
            "billing_cycle":subscribe.billing_cycle,
            "next_billing_date":subscribe.next_billing_date.isoformat() if subscribe.next_billing_date else None,
            "status":subscribe.status,
            "note":subscribe.note,
            "created_at":subscribe.created_at.isoformat() if subscribe.created_at else None

        })


    return jsonify({
        "success":True,
        "message":subscription_list
    })    ,200

#update subscription
@subscribe_bp.route("/subscription/update/<int:subscription_id>", methods=["PATCH"])
@jwt_required()
@limiter.limit("25 per minute", key_func=lambda: get_jwt_identity())
def update_subscription(subscription_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Request Body is required"}), 400

    subscription = Subscription.query.filter_by(
        id=subscription_id, user_id=current_user_id
    ).first()
    if not subscription:
        return jsonify({"success": False, "message": "Subscription not found"}), 404
    if "name" in data:
        raw = data.get("name")
        if raw is None:
            return jsonify({"success": False, "message": "name cannot be null"}), 400
        name = str(raw).strip()
        if not name:
            return jsonify({"success": False, "message": "name cannot be empty"}), 400
        if len(name) > 100:
            return jsonify({"success": False, "message": "Name too long (max 100 chars)"}), 400
        subscription.name = name

    if "amount" in data:
        raw = data.get("amount")
        if raw is None:
            return jsonify({"success": False, "message": "amount cannot be null"}), 400
        try:
            amount = float(raw)
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Amount must be a number"}), 400
        if amount <= 0:
            return jsonify({"success": False, "message": "Amount must be greater than zero"}), 400
        subscription.amount = amount
    if "billing_cycle" in data:
        raw = data.get("billing_cycle")
        if raw is None:
            return jsonify({"success": False, "message": "billing_cycle cannot be null"}), 400
        cycle = str(raw).strip().lower()
        if cycle not in ("monthly", "yearly", "weekly"):
            return jsonify({
                "success": False,
                "message": "billing_cycle must be 'monthly', 'yearly' or 'weekly'"
            }), 400
        subscription.billing_cycle = cycle

    if "next_billing_date" in data:
        raw = data.get("next_billing_date")
        if raw is None:
            return jsonify({"success": False, "message": "next_billing_date cannot be null"}), 400
        try:
            due = datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=UTC)
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "next_billing_date must be YYYY-MM-DD"}), 400
        if due <= datetime.now(UTC):
            return jsonify({"success": False, "message": "next_billing_date must be in the future"}), 400
        subscription.next_billing_date = due

    if "status" in data:
        raw = data.get("status")
        if raw is None:
            return jsonify({"success": False, "message": "status cannot be null"}), 400
        s = str(raw).strip().lower()
        if s not in ("active", "paused", "cancelled"):
            return jsonify({
                "success": False,
                "message": "status must be 'active', 'paused', or 'cancelled'"
            }), 400
        subscription.status = s
    if "note" in data:
        raw = data.get("note")
        if raw is None:
            subscription.note = None
        else:
            note = str(raw).strip()
            if len(note) > 100:
                return jsonify({"success": False, "message": "Note too long (max 150 chars)"}), 400
            subscription.note = note or None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Subscription update failed")
        return jsonify({"success": False, "message": "Something went wrong"}), 500

    return jsonify({
        "success": True,
        "message": "Subscription updated successfully"
    }), 200

# Delete subscription
@subscribe_bp.route("/subscription/delete/<int:subscription_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def delete_subscription(subscription_id):
    current_user_id = int(get_jwt_identity())
    subscription = Subscription.query.filter_by(
        id=subscription_id,
        user_id=current_user_id
    ).first()

    if not subscription:
        return jsonify({
            "success":False,
            "message": "Subscription not found"
        }), 404
    try:
       db.session.delete(subscription)
       db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit is failed")
        return jsonify({
            "success":False,
            "message":"Something Went wrong"
        }),500
    return jsonify({
        "success":True,
        "message": "Subscription deleted successfully"
    }), 200


# Upcoming subscriptions in next 7 days
@subscribe_bp.route("/subscription/upcoming", methods=["GET"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def upcoming_subscriptions():
    current_user_id = int(get_jwt_identity())
    today = datetime.now(UTC)
    next_7_days = today + timedelta(days=7)
    subscriptions = Subscription.query.filter(
        Subscription.user_id == current_user_id,
        Subscription.status == "active",
        Subscription.next_billing_date >= today,
        Subscription.next_billing_date <= next_7_days
    ).order_by(Subscription.next_billing_date.asc()).all()
    upcoming_list = []

    for sub in subscriptions:
        upcoming_list.append({
            "id": sub.id,
            "name": sub.name,
            "amount":float(sub.amount),
            "billing_cycle": sub.billing_cycle,
            "next_billing_date": sub.next_billing_date.isoformat() if sub.next_billing_date is not None else None,
            "status": sub.status
        })

    return jsonify({
        "success":True,
        "upcoming_subscriptions": upcoming_list
    }), 200
