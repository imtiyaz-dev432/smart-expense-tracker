from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime,timedelta
from dbms.db import db
from models.subscribe import Subscription
subscribe_bp=Blueprint("subscribe_bp",__name__)
@subscribe_bp.route("/subscription/add", methods=["POST"])
@jwt_required()
def add_subscription():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    

    name = data.get("name")
    amount = data.get("amount")
    billing_cycle = data.get("billing_cycle")
    next_billing_date = data.get("next_billing_date")
    note = data.get("note")

    if not name or amount is None or not billing_cycle or not next_billing_date:
        return jsonify({
            "message": "Name, amount, billing cycle and next billing date are required"
        }), 400

    billing_cycle = billing_cycle.strip().lower()

    if billing_cycle not in ["monthly", "yearly", "weekly"]:
        return jsonify({
            "message": "Billing cycle must be monthly, yearly or weekly"
        }), 400

    next_billing_date_obj = datetime.strptime(next_billing_date, "%Y-%m-%d")

    new_subscription = Subscription(
        name=name,
        amount=float(amount),
        billing_cycle=billing_cycle,
        next_billing_date=next_billing_date_obj,
        note=note,
        user_id=current_user_id
    )

    db.session.add(new_subscription)
    db.session.commit()

    return jsonify({
        "message": "Subscription added successfully"
    }), 201


#get all
@subscribe_bp.route("/subscription/get",methods=["GET"])
@jwt_required()
def get__subscription():
    current_user_id=int(get_jwt_identity())
    subscribes=Subscription.query.filter_by(
        user_id=current_user_id
    )   .all()
    
    subscription_list=[]

    for subscribe in subscribes:
        subscription_list.append({
            "id":subscribe.id,
            "name":subscribe.name,
            "amount":subscribe.amount,
            "billing_cycle":subscribe.billing_cycle,
            "next_billing_date":subscribe.next_billing_date,
            "status":subscribe.status,
            "note":subscribe.note,
            "created_at":subscribe.created_at
        })


    return jsonify({
        "message":subscription_list
    })    ,200

#update 

@subscribe_bp.route("/subscription/update/<int:subscription_id>", methods=["PUT"])
@jwt_required()
def update_subscription(subscription_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    subscription = Subscription.query.filter_by(
        id=subscription_id,
        user_id=current_user_id
    ).first()

    if not subscription:
        return jsonify({
            "message": "Subscription not found"
        }), 404

    subscription.name = data.get("name", subscription.name)

    if data.get("amount"):
        subscription.amount = float(data.get("amount"))

    if data.get("billing_cycle"):
        billing_cycle = data.get("billing_cycle").strip().lower()

        if billing_cycle not in ["monthly", "yearly", "weekly"]:
            return jsonify({
                "message": "Billing cycle must be monthly, yearly or weekly"
            }), 400

        subscription.billing_cycle = billing_cycle

    if data.get("next_billing_date"):
        subscription.next_billing_date = datetime.strptime(
            data.get("next_billing_date"),
            "%Y-%m-%d"
        )

    subscription.status = data.get("status", subscription.status)
    subscription.note = data.get("note", subscription.note)

    db.session.commit()

    return jsonify({
        "message": "Subscription updated successfully"
    }), 200


# Delete subscription
@subscribe_bp.route("/subscription/delete/<int:subscription_id>", methods=["DELETE"])
@jwt_required()
def delete_subscription(subscription_id):
    current_user_id = int(get_jwt_identity())

    subscription = Subscription.query.filter_by(
        id=subscription_id,
        user_id=current_user_id
    ).first()

    if not subscription:
        return jsonify({
            "message": "Subscription not found"
        }), 404

    db.session.delete(subscription)
    db.session.commit()

    return jsonify({
        "message": "Subscription deleted successfully"
    }), 200


# Upcoming subscriptions in next 7 days
@subscribe_bp.route("/subscription/upcoming", methods=["GET"])
@jwt_required()
def upcoming_subscriptions():
    current_user_id = int(get_jwt_identity())

    today = datetime.utcnow()
    next_7_days = today + timedelta(days=7)

    subscriptions = Subscription.query.filter(
        Subscription.user_id == current_user_id,
        Subscription.status == "active",
        Subscription.next_billing_date >= today,
        Subscription.next_billing_date <= next_7_days
    ).all()

    upcoming_list = []

    for sub in subscriptions:
        upcoming_list.append({
            "id": sub.id,
            "name": sub.name,
            "amount": sub.amount,
            "billing_cycle": sub.billing_cycle,
            "next_billing_date": sub.next_billing_date,
            "status": sub.status
        })

    return jsonify({
        "upcoming_subscriptions": upcoming_list
    }), 200