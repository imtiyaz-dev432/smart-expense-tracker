from flask import Blueprint, request,jsonify
from dbms.db import db
from flask_jwt_extended import jwt_required,get_jwt_identity
from models.loan import Loan
from datetime import datetime 

loan_bp=Blueprint("loan-bp",__name__)
@loan_bp.route("/loan",methods=["POST"])
@jwt_required()
def add_loan():
    data=request.get_json()
    loan_name=data.get("loan_name")
    total_amount=data.get("total_amount")
    monthly_emi=data.get('monthly_emi')
    remaining_amount=data.get('remaining_amount')
    due_date=data.get("due_date")
    if not loan_name or not total_amount or not monthly_emi or not remaining_amount or not due_date:
        return jsonify({
            "message": "All loan fields are required"
        }), 400
    
    current_user_id=int(get_jwt_identity())
    due_date_obj=datetime.strptime(due_date,"%Y-%m-%d")
    new_loan=Loan(
        loan_name=loan_name,
        total_amount=float(total_amount),
        monthly_emi=float(monthly_emi),
        remaining_amount=float(remaining_amount),
        due_date=due_date_obj,
        user_id=current_user_id
    )    

    db.session.add(new_loan)
    db.session.commit()
    return jsonify({
        "message":"Loan added successfully"
    }),201

#get all loan detail
@loan_bp.route("/loan/get",methods=["GET"])
@jwt_required()
def get_loan():
    current_user_id=int(get_jwt_identity())
    loans=Loan.query.filter_by(user_id=current_user_id).all()
    result=[]
    for loan in loans:
        result.append({
            "id":loan.id,
            "loan_name":loan.loan_name,
            "total_amount":loan.total_amount,
            "monthly_emi":loan.monthly_emi,
            "remaining_amount":loan.remaining_amount,
            "due_date":loan.due_date,
            "status":loan.status,
            "created_at":loan.created_at
        })
    return jsonify({
        "loans":result
    })    ,200

#update loan
@loan_bp.route("/loan/update/<int:loan_id>",methods=["PUT"])
@jwt_required()
def update_loan(loan_id):
        current_user_id=int(get_jwt_identity())
        data=request.get_json()
        loan=Loan.query.filter_by(id=loan_id,user_id=current_user_id).first()
        
        if not loan:
            return jsonify({
                "message":"Loan not found"
            }),404

        loan.loan_name=data.get("loan_name",loan.loan_name) 
        loan.total_amount=data.get("total_amount",loan.total_amount)
        loan.monthly_emi=data.get("monthly_emi",loan.monthly_emi)
        loan.remaining_amount=data.get("remaining_amount",loan.remaining_amount)
        loan.status=data.get("status",loan.status)   
        if data.get("due_date"):
         loan.due_date = datetime.strptime(data.get("due_date"), "%Y-%m-%d")
        db.session.commit()
        return jsonify({
            "message":"loan updated successfuly"
        }),200

#delete loan
@loan_bp.route("/loan/delete/<int:loan_id>",methods=["DELETE"])
@jwt_required()
def delete_loan(loan_id):
    current_user_id=int(get_jwt_identity())
    loan=Loan.query.filter_by(
        id=loan_id,
        user_id=current_user_id
    )    .first()


    if not loan:
        return jsonify({
            "message":"Loan not found"
        }),404
    db.session.delete(loan)
    db.session.commit()
    return jsonify({
        "message":"loan deleted successfully"
    }),200


#loan repayment

@loan_bp.route("/loan/repayment/<int:loan_id>",methods=["POST"])
@jwt_required()
def repayment(loan_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json()
    paid_amount=data.get("paid_amount")
    
    if not paid_amount:
        return jsonify({
            "message":"paid amount is required"
        }),400

    paid_amount=float(paid_amount)    
    if paid_amount<=0:
        return jsonify({
            "message":"Paid amount is not equal to or less than 0"
        })    ,404

    loan=Loan.query.filter_by(
        id=loan_id,
        user_id=current_user_id).first()

    if not loan:
        return jsonify({
            "message":"Loan not found"
        })        ,404

    if loan.status=='completed':
        return jsonify({
            "message":"This loan is already completed"
        })    ,400


    if paid_amount>loan.remaining_amount:
        return jsonify({
            "message":"paid amount is not greater than remaining amount"
        })    ,400

    loan.remaining_amount=loan.remaining_amount-paid_amount

    if loan.remaining_amount==0:
        loan.status='completed'
    

    db.session.commit()
    return jsonify({
        "message":"Repayment added successfully",
        "remaining_amount":loan.remaining_amount,
        "status":loan.status
    })    ,200