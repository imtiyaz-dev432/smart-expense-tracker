from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dbms.db import db
from models.category import Category
from models.expense import Expense
from utils.rate import limiter

expense_bp=Blueprint("expense-bp",__name__,url_prefix="/expense")
@expense_bp.route("/add",methods=["POST"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda: get_jwt_identity())
def add_expense():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request BOdy is Required"
        }),400
    title=data.get('title')
    raw_amount=data.get("amount")
    category=data.get('category')
    description=data.get("description")
    try:
        amount=float(raw_amount) if raw_amount is  not None else None
    except (TypeError,ValueError):
        return  jsonify({"success": False, "message": "Amount must be a number"}), 400


    if not title or amount is None or not category:
        return jsonify({
            "success":False,
            "message":"Title,amount and category are required"
        }),400
    category=category.strip()
    if not category:
        return jsonify({
            "success":False,
            "message":"Category must be required"
        }),400
    if amount<0:
        return jsonify({
            "success":False,
            "message":"Amount cannot be negative"
        }),400
    current_user_id=int(get_jwt_identity())
    try:
        existing=Category.query.filter(
            Category.user_id==current_user_id,
            db.func.lower(Category.name)==(category.lower())
        ).first()
        if not existing:
            db.session.add(Category(name=category,user_id=current_user_id))
        else:
            category=existing.name
        new_expense=Expense(
        title=title,
        amount=amount,
        category=category,
        description=description,
        user_id=current_user_id
    )

        db.session.add(new_expense)
        db.session.commit()
        return jsonify({
        "success":True,
        "message":"Expense added successfully"
    }),201
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db Commit Failed")
        return jsonify({
        "success": False,
        "message": "Internal Server Error"
    }), 500


@expense_bp.route("/categories",methods=["GET"]) #without this we do not get list of expense categories
@jwt_required()
def list_categories():
    current_user_id=int(get_jwt_identity())
    category=Category.query.filter(
        Category.user_id==current_user_id,
        Category.name!="Other",
    ).order_by(Category.name).all()
    return jsonify([{"id": c.id, "name": c.name} for c in category]), 200



    #get all expense
@expense_bp.route("/all",methods=['GET'])
@jwt_required()
def get_expense():
   current_user_id=int(get_jwt_identity())
   expenses=Expense.query.filter_by(user_id=current_user_id).order_by(Expense.date.desc()).all()
   expense_list=[]

   for expense in expenses:
    expense_list.append(
        {
            "id":expense.id,
            "title":expense.title,
            "amount":float(expense.amount),
            "category":expense.category,
            "description":expense.description,
            "date":expense.date.isoformat() if expense.date else None
        }
    )

   return jsonify({
    "success":True,
        "expenses":expense_list
    }),200

#update  expense

@expense_bp.route("/update/<int:expense_id>",methods=['PATCH'])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda: get_jwt_identity())
def update_expense(expense_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json(silent=True)
    if not data :
        return jsonify({
            "success":False,
            "message":"Request Body is Required"
        }),400
    expense=Expense.query.filter_by(id=expense_id,
    user_id=current_user_id).first()

    if not expense:
        return jsonify({
            "success":False,
            "message":"Expense not found"
        }),404

    if "title" in data:
        if not data.get("title"):
            return jsonify({
                "success":False,
                "message": "Title cannot be empty"}), 400
        expense.title=data.get("title")
    if "category" in data:
        new_category = (data.get("category") or "").strip()
        if not new_category:
            return jsonify({
                "success":False,
                "message": "Category cannot be empty"}), 400
        existing=Category.query.filter(
            Category.user_id==current_user_id,
            db.func.lower(Category.name)==(new_category.lower())
        ).first()
        if existing:
            expense.category=existing.name
        else:
            db.session.add(Category(name=new_category,user_id=current_user_id))
            expense.category=new_category


    if 'amount' in data:
        try:
            raw_amount=data.get('amount')
            amount=float(raw_amount)
        except (TypeError,ValueError):
           return jsonify({"success": False, "message": "Amount must be a number"}), 400
        if amount<0:
            return jsonify({
                "success":False,
                "message":"Amount cannot be negative"
            }) ,400
        expense.amount=amount
    expense.description=data.get('description',expense.description)
    try:
       db.session.commit()
       return jsonify ({
        "success":True,
        "message":"Expense Updated Successfully"
       })    ,200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db Commit Failed")
        return jsonify({
        "success": False,
        "message": "Internal Server Error"
    }), 500

#delete expense

@expense_bp.route("/delete/<int:expense_id>",methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    current_user_id=int(get_jwt_identity())
    expense=Expense.query.filter_by(
        id=expense_id,
        user_id=current_user_id).first()
    if not expense:
        return jsonify({
            "success":False,
            "message":"Expense not found"
        }),404
    try:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({
        "success":True,
        "message":"Expense deleted Successfully"
    }),200
    except Exception:
        db.session.rollback()
        current_app.logger.exception("DB Commit Failed")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500
