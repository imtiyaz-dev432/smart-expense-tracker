from flask import Blueprint, request,jsonify
from dbms.db import db
from models.expense import Expense
from flask_jwt_extended  import get_jwt_identity,jwt_required
expense_bp=Blueprint("expense-bp",__name__)

@expense_bp.route("/expense",methods=["POST"])
@jwt_required()
def add_expense():
    data=request.get_json()
    title=data.get('title')
    amount=data.get('amount')
    category=data.get('category')
    description=data.get("description")
    
    if not title or not amount or not category:
        return jsonify({
            "message":"Title,amount and category are required"
        }),400

    current_user_id=get_jwt_identity()

    new_expense=Expense(
        title=title,
        amount=float(amount),
        category=category,
        description=description,
        user_id=current_user_id
    )

    db.session.add(new_expense)
    db.session.commit()

    return jsonify({
        "message":"Expense added successfully"
    }),201


    #get all expense
@expense_bp.route("/expense/all",methods=['GET'])
@jwt_required()
def get_expense():
   current_user_id=get_jwt_identity()
   expenses=Expense.query.filter_by(user_id=current_user_id).all()
   expense_list=[]

   for expense in expenses:
    expense_list.append(
        {
            "id":expense.id,
            "title":expense.title,
            "amount":expense.amount,
            "category":expense.category,
            "description":expense.description,
            "date":expense.date
        }
    )

   return jsonify({
        "expenses":expense_list
    }),200

#update  expense

@expense_bp.route("/expense/update/<int:expense_id>",methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    current_user_id=get_jwt_identity()
    data=request.get_json()
    expense=Expense.query.filter_by(id=expense_id,
    user_id=current_user_id).first()

    if not expense:
        return jsonify({
            "message":"Expense not found"
        }),404

    expense.title=data.get('title',expense.title) 
    
    if data.get("amount") is not None:
      expense.amount=float(data.get('amount'))
    expense.category=data.get("category",expense.category) 
    expense.description=data.get('description',expense.description)

    db.session.commit()
    return jsonify ({
        "message":"Expense Updated Successfully"
    })    ,200


#delete expense

@expense_bp.route("/expense/delete/<int:expense_id>",methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    current_user_id=get_jwt_identity()
    expense=Expense.query.filter_by(
        id=expense_id,
        user_id=current_user_id).first()
    if not expense:
        return jsonify({
            "message":"Expense not found"
        }),404

    db.session.delete(expense)
    db.session.commit()
    return jsonify({
        "message":"Expense deleted Successfully"
    }),200        