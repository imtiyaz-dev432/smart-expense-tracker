from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dbms.db import db
from models.income import Income
from utils.rate import limiter

income_bp=Blueprint("income_bp",__name__)
@income_bp.route("/income/add",methods=['POST'])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def add_income():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    source = (data.get('source') or '').strip()
    raw_amount=data.get('amount')
    try:
        amount=float(raw_amount) if raw_amount is not None else None
    except (TypeError,ValueError):
         return  jsonify({"success": False, "message": "Amount must be a number"}), 400

    description=data.get('description')

    if not source or amount is None :
        return jsonify({
            "success":False,
            "message":"source and amount are required"
        }),400
    if len(source)>100:
        return jsonify({
            "success":False,
            "message":"Only 100 characters are allowed"
        })   ,400
    if "description" in data:
        description=data.get("description")
        if description is not None:
          description=description.strip()
          if len(description)>200 and description:
            return jsonify({
                "success":False,
                "message":"Only 200 characters are allowed"
            }),400
    if amount<=0:
        return jsonify({
            "success":False,
            "message":"Income Amount cannot be zero or negative"
        }),400

    current_user_id=int(get_jwt_identity())
    new_income=Income(
        source=source,
        amount=amount,
        description=description,
        user_id=current_user_id
    )

    db.session.add(new_income)
    try:
       db.session.commit()
       return jsonify({
        "success":True,
        "message":"Income added successfully"
    }),201
    except Exception :
        db.session.rollback()
        current_app.logger.exception("Db Commit Failed")
        return jsonify({
        "success": False,
        "message": "Internal Server Error"
    }), 500
#get income

@income_bp.route("/income/all",methods=["GET"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def get_income():
   current_user_id=int(get_jwt_identity())
   incomes=Income.query.filter_by(user_id=current_user_id).order_by(Income.date.desc()).all()
   income_list=[]
   for income in incomes:
    income_list.append({
      "id":income.id,
     "source":income.source,
     "amount":float(income.amount),
     "description":income.description,
     "date":income.date.isoformat() if income.date else None})

   return jsonify(
    {    "success":True,
        "income":income_list
    }
   ),200


#Income update

@income_bp.route("/income/update/<int:income_id>",methods=['PATCH'])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def update_income(income_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    income = Income.query.filter_by(
    id=income_id,
    user_id=current_user_id
).first()

    if not income:
        return jsonify ({
            "success":False,
            "message":"Income not found"
        }),404
    if "source" in data:
        source = (data.get("source") or "").strip()
        if not source:
           return jsonify({"success": False, "message": "Source cannot be empty"}), 400
        if len(source)>100:
            return jsonify({
                "success":False,
                "message":"Only 100 characters are allowed"
            }),400
        income.source=source
    if "amount" in data:
        raw_amount=data.get("amount")
        try:
            amount=float(raw_amount) if raw_amount is not None else None
        except (TypeError,ValueError):
              return jsonify({"success": False, "message": "Amount must be a number"}), 400
        if amount<=0:
            return jsonify({
                "success":False,
                "message":"Amount cannot be zero or negative"
            })      ,400
        income.amount=amount
    if "description" in data:
        description=data.get("description")
        if description is not None:
          description=description.strip()
          if len(description)>200:
            return jsonify({
                "success":False,
                "message":"Only 200 characters are allowed"
            })   ,400
        income.description=description
    try:
       db.session.commit()
       return jsonify({
        "success":True,
        "message":"Income updated successfully"
    }),200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit Failed")
        return jsonify({
        "success": False,
        "message": "Internal Server Error"
    }), 500


#delete income
@income_bp.route("/income/delete/<int:income_id>",methods=['DELETE'])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def delete_income(income_id):
    current_user_id=int(get_jwt_identity())
    income=Income.query.filter_by(
        id=income_id,
        user_id=current_user_id
    ).first()

    if not income:
        return jsonify({
            "success":False,
            "message":"Income not found"
        }),404
    try:
       db.session.delete(income)
       db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit is failed")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        })   ,500
    return jsonify ({
        "success":True,
        "message":"Income deleted successfully"
    })    ,200
