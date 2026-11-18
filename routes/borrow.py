from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dbms.db import db
from models.borrow import Borrow
from utils.rate import limiter

borrow_bp=Blueprint("borrow_bp",__name__)
@borrow_bp.route("/borrow/add",methods=["POST"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def borrow():
    current_user_id=int(get_jwt_identity())
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is Required"
        }),400
    person_name=(data.get("person_name") or '').strip()
    status=(data.get("status") or "pending").strip().lower()
    raw_amount=data.get("amount")
    try:
        amount=float(raw_amount) if raw_amount is not None else None
    except (ValueError,TypeError):
        return jsonify({
            "success":False,
            "message":"Amount must be number"
        })    ,400

    borrow_type=data.get("borrow_type")
    due_date=data.get("due_date")
    note=data.get("note")

    if not person_name or amount is None or not borrow_type:
        return jsonify({
            "success":False,
            "message":"All the fields are required "
        }) ,400
    if amount<=0:
        return jsonify({
        "success": False,
        "message": "Amount must be greater than zero"
    }), 400
    borrow_type = borrow_type.strip().lower()
    if status not in["overdue","pending","paid"]:
        return jsonify({
            "success":False,
            "message":"Status must be active or pending"
        }),400
    if len(note)>25:
        return jsonify({
            "success":False,
            "message":"Note length upto 25 character"
        }),400

    if borrow_type not in ['borrowed','lent']:
        return jsonify({
            "success":False,
            "message":"Type must be borrowed or lent "
        }),400
    due_date_obj = None
    if due_date:
      try:
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=UTC)
      except (ValueError, TypeError):
        return jsonify({"success": False, "message": "due_date must be YYYY-MM-DD"}), 400
    try:
        new_borrower=Borrow(
        person_name=person_name,
        amount=amount,
        borrow_type=borrow_type,
        due_date=due_date_obj,
        note=note,
        status=status,
        user_id=current_user_id
    )

        db.session.add(new_borrower)
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
        "message":"Borrow/Lent added successfully"
    })    ,201


#get all borrower
@borrow_bp.route("/borrow/get",methods=["GET"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity()) #always called with 0 args
def get_borrow():
    current_user_id=int(get_jwt_identity())
    borrows=Borrow.query.filter_by(
        user_id=current_user_id
    ).order_by(Borrow.created_at.desc()).all()

    borrow_list=[]
    for borrow in borrows:
        borrow_list.append({
            "id":borrow.id,
            "person_name":borrow.person_name,
            "amount":float(borrow.amount),
            "type":borrow.borrow_type,
            "due_date":borrow.due_date.isoformat() if borrow.due_date else None,
            "status":borrow.status,
            "note":borrow.note,
            "created_at":borrow.created_at.isoformat() if borrow.created_at else None
        })

    return jsonify({
        "success":True,
        "borrow":borrow_list
    }),200


#Update
@borrow_bp.route("/borrow/update/<int:borrow_id>",methods=["PATCH"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def update_borrow(borrow_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"}),400
    borrow=Borrow.query.filter_by(
        user_id=current_user_id,
        id=borrow_id
    ).first()

    if not borrow:
        return jsonify({
            "success":False,
            "message":"Borrow not found"
        }),404
    if "amount" in data:
        raw_amount=data.get("amount")
        if raw_amount is None:
            return jsonify({"success": False, "message": "amount cannot be null"}), 400
        try:
            amount=float(raw_amount) if raw_amount is not None else None
        except (ValueError,TypeError):
            return jsonify({
                "success":False,
                "message":"Amount must be number"
            })    ,400
        if amount<=0:
            return jsonify({
                "success":False,
                "message":"Amount must be positive"
            })    ,400
        borrow.amount=amount
    if "borrow_type" in data:
        borrow_type=data.get("borrow_type")
        if borrow_type is  None:
            return jsonify({"success": False, "message": "borrow_type cannot be null"}), 400
        borrow_type=str(borrow_type).strip().lower()
        if borrow_type not in ['borrowed','lent']:
              return jsonify({
            "success":False,
            "message":"Type must be borrowed or lent "
        }),400
        borrow.borrow_type=borrow_type
    if "status" in data:
        status=data.get("status")
        if status is None:
            return jsonify({
                "success":False,
                "message":"status cannot be null"
            }),400
        status=str(status).strip().lower()
        if status not in["overdue","pending","paid"]:
           return jsonify({
            "success":False,
            "message":"Status must be active or pending"
        }),400
        borrow.status=status
    if "note" in data:
        note=data.get("note")
        if note is None:
            return jsonify({
                "success":False,
                "message":"note cannot be null"
            }),400
        note=str(note).strip()
        if len(note)>100:
              return jsonify({
            "success":False,
            "message":"Note length upto 100 character's"
        }),400
        borrow.note=note
    if "person_name" in data:
        person_name=(data.get("person_name") or '').strip()
        if not person_name:
            return jsonify({
                "success":False,
                "message":"person_name cannot be empty"
            }),400
        if len(person_name)>100:
            return jsonify({
            "success":False,
            "message":"Person name length up to 100 characters"
        }),400
        borrow.person_name=person_name
    if "due_date" in data:
          try:
            due = datetime.strptime(data["due_date"], "%Y-%m-%d").replace(tzinfo=UTC)
          except (ValueError, TypeError):
            return jsonify({"success": False, "message": "due_date must be YYYY-MM-DD"}), 400
          if due <= datetime.now(UTC):
            return jsonify({"success": False, "message": "Due date must be in the future"}), 400
          borrow.due_date = due
    try:
       db.session.commit()
       return jsonify({
        "success":True,
        "message":"Borrow/Lend Updated successfully"
    }),200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit is failed")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        }),500

#dalete borrow
@borrow_bp.route("/borrow/delete/<int:borrow_id>",methods=["DELETE"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def delete_borrow(borrow_id):
    current_user_id=int(get_jwt_identity())
    borrow=Borrow.query.filter_by(
        id=borrow_id,
        user_id=current_user_id
    ).first()

    if not borrow:
        return jsonify({
            "success":False,
            "message":"borrow not found"
        }),404
    try:
        db.session.delete(borrow)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit is failed")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        })    ,500
    return jsonify({
        "success":True,
        "message":"Borrow/Lend deleted successfully"
    })    ,200

#mark paid route
@borrow_bp.route("/borrow/mark-paid/<int:borrow_id>",methods=["PUT"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def mark_paid(borrow_id):
    current_user_id=int(get_jwt_identity())
    borrow=Borrow.query.filter_by(
        id=borrow_id,
        user_id=current_user_id
    ).first()

    if not borrow:
        return jsonify({
            "success":False,
            "message":"Borrow/Lend not found"
        }),404
    if borrow.status == "paid":
         return jsonify({
        "success": False,
        "message": "Borrow is already marked as paid"
    }), 400
    try:

       borrow.status="paid"
       db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit is failed")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        })   ,500
    return jsonify({
        "success":True,
        "message":"mark-paid successfully",
        "borrow_id": borrow.id,
        "status": borrow.status
    })    ,200
