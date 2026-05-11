from flask import Blueprint, request,jsonify
from dbms.db import db
from flask_jwt_extended import jwt_required,get_jwt_identity
from models.income import Income

income_bp=Blueprint("income_bp",__name__)
@income_bp.route("/income/add",methods=['POST'])
@jwt_required()
def add_income():
    data=request.get_json()
    source=data.get('source')
    amount=data.get('amount')
    description=data.get('description')

    if not source or not amount  :
        return jsonify({
            "message":"source and amount are required"
        }),400

    current_user_id=int(get_jwt_identity())
    new_income=Income(
        source=source,
        amount=float(amount),
        description=description,
        user_id=current_user_id
    )    

    db.session.add(new_income)
    db.session.commit()
    return jsonify({
        "message":"Income added successfully"
    }),201

#get income

@income_bp.route("/income/all",methods=["GET"])
@jwt_required()
def get_income():
   current_user_id=int(get_jwt_identity())
   incomes=Income.query.filter_by(user_id=current_user_id).all()
   income_list=[]
   for income in incomes:
    income_list.append({
      "id":income.id,
     "source":income.source,
     "amount":income.amount,
     "description":income.description,
     "date":income.date})

   return jsonify(
    {
        "income":income_list
    }
   ),200


#Income update

@income_bp.route("/income/update/<int:income_id>",methods=['PUT'])
@jwt_required()
def update_income(income_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json()
    income = Income.query.filter_by(
    id=income_id,
    user_id=current_user_id
).first()
    
    if not income:
        return jsonify ({
            "message":"Income not found"
        }),404

    income.source=data.get("source",income.source)
    if data.get("amount") is not  None:
      income.amount=float(data.get('amount'))
    income.description=data.get("description",income.description)    

    db.session.commit()
    return jsonify({
        "message":"Income updated successfully"
    }),200

#delete income isme whi id dena hai jo income m ein feytch krte tie a rha hai
@income_bp.route("/income/delete/<int:income_id>",methods=['DELETE'])
@jwt_required()
def delete_income(income_id):
    current_user_id=int(get_jwt_identity())
    income=Income.query.filter_by(
        id=income_id,
        user_id=current_user_id
    ).first()

    if not income:
        return jsonify({
            "message":"Income not found"
        }),404

    db.session.delete(income)
    db.session.commit()
    return jsonify ({
        "message":"Income deleted successfully"
    })    ,200
