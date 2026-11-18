from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dbms.db import db
from models.loan import Loan
from utils.rate import limiter

loan_bp=Blueprint("loan-bp",__name__)
@loan_bp.route("/loan/add",methods=["POST"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def add_loan():
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request Body is required"
        }),400
    loan_name = (data.get("loan_name") or "").strip()
    _amount=data.get("total_amount")
    try:
        total_amount=float(_amount) if _amount is not None else None
    except (ValueError,TypeError):
        return  jsonify({
            "success":False,
            "message":"total amount must be number"
        })    ,400
    _emi=data.get('monthly_emi')
    try:
        monthly_emi=float(_emi) if _emi is not None else None
    except (ValueError,TypeError):
        return  jsonify({
            "success":False,
            "message":"monthly emi must be number"
        })    ,400

    due_date=data.get("due_date")
    if not loan_name or  total_amount is None or monthly_emi is None  or  not due_date:
        return jsonify({
            "success":False,
            "message": "All loan fields are required"
        }), 400
    if len(loan_name) > 100:
        return jsonify({
            "success":False,
            "message": "Loan name too long (max 100 characters)"}),400
    
    if total_amount<=0 or  monthly_emi<=0:
        return jsonify({
            "success":False,
            "message":"All amount's must be positive"
        })    ,400
        
    
    if total_amount<=monthly_emi:
        return jsonify({
            "success":False,
            "message":"Monthly EMI must be less than total amount"
        }),400
    current_user_id=int(get_jwt_identity())
    
    try:
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "due_date must be YYYY-MM-DD"}), 400
    if due_date_obj <= datetime.now(UTC):
      return jsonify({
        "success": False,
        "message": "Due date must be in the future"
    }), 400
    try:
        new_loan=Loan(
        loan_name=loan_name,
        total_amount=total_amount,
        monthly_emi=monthly_emi,
        remaining_amount=total_amount,
        due_date=due_date_obj,
        user_id=current_user_id
    )    

        db.session.add(new_loan)
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
        "message":"Loan added successfully"
    }),201

#get all loan detail
@loan_bp.route("/loan/get",methods=["GET"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def get_loan():
    current_user_id=int(get_jwt_identity())
    loans=Loan.query.filter_by(user_id=current_user_id).order_by(Loan.created_at.desc()).all()
    result=[]
    for loan in loans:
        result.append({
            "id":loan.id,
            "loan_name":loan.loan_name,
            "total_amount":float(loan.total_amount),
            "monthly_emi":float(loan.monthly_emi),
            "remaining_amount":float(loan.remaining_amount),
            "due_date": loan.due_date.isoformat() if loan.due_date else None,
            "created_at": loan.created_at.isoformat() if loan.created_at else None,
            "status":loan.status,
        })
    return jsonify({
        "success":True,
        "loans":result
    })    ,200

#update loan
@loan_bp.route("/loan/update/<int:loan_id>",methods=["PATCH"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def update_loan(loan_id):
        current_user_id=int(get_jwt_identity())
        data=request.get_json(silent=True)
        if not data:
            return jsonify({
                "success":False,
                "message":"Request Body is required"
            }),400
        loan=Loan.query.filter_by(id=loan_id,user_id=current_user_id).first()
        
        if not loan:
            return jsonify({
                "success":False,
                "message":"Loan not found"
            }),404
        new_total = loan.total_amount
        new_emi = loan.monthly_emi

        if "loan_name" in data:
            raw = data.get("loan_name")
            loan_name = str(raw).strip() if raw is not None else ""
    
            if not loan_name:
                return jsonify({
            "success": False,
            "message": "Loan name cannot be empty"
        }), 400
            if len(loan_name) > 100:
                 return jsonify({
            "success": False,
            "message": "Loan name too long (max 100)"
        }), 400
            loan.loan_name = loan_name

        if "total_amount" in data:
            amount=data.get("total_amount")
            try:
                new_total=float(amount)
            except (ValueError,TypeError):
                return jsonify({
                    "success":False,
                    "message":"Total amount must be in number"
                }),400
        if "monthly_emi" in data:
            emi=data.get("monthly_emi")
            try:
                new_emi=float(emi)    
            except ( TypeError, ValueError):
               return jsonify({"success": False, "message": "Monthly EMI must be a number"}), 400

        if new_total <= 0 or new_emi <= 0:
          return jsonify({"success": False, "message": "Amounts must be greater than zero"}), 400

        if new_emi >= new_total:
           return jsonify({"success": False, "message": "Monthly EMI must be less than total amount"}), 400
        if new_total < float(loan.remaining_amount):
            return jsonify({
                "success":False,
                "message":"Total cannot be less than remaining"
            }),400

        
        if "due_date" in data:
          try:
            due = datetime.strptime(data["due_date"], "%Y-%m-%d").replace(tzinfo=UTC)
          except (ValueError, TypeError):
            return jsonify({"success": False, "message": "due_date must be YYYY-MM-DD"}), 400
          if due <= datetime.now(UTC):
            return jsonify({"success": False, "message": "Due date must be in the future"}), 400
          loan.due_date = due

        if "status" in data:
            s = (data.get("status") or "").strip().lower()
            if s not in ("active", "closed", "defaulted"):
              return jsonify({"success": False, "message": "Invalid status"}), 400
            loan.status = s
        
        try:
            loan.monthly_emi=new_emi
            loan.total_amount=new_total
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Db commit is failed")    
            return jsonify({
                "success":False,
                "message":"Something Went Wrong"
            }),500
        return jsonify({
            "success":True,
            "message":"loan updated successfully"
        }),200

#delete loan
@loan_bp.route("/loan/delete/<int:loan_id>",methods=["DELETE"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def delete_loan(loan_id):
    current_user_id=int(get_jwt_identity())
    loan=Loan.query.filter_by(
        id=loan_id,
        user_id=current_user_id
    )    .first()
    if not loan:
        return jsonify({
            "success":False,
            "message":"Loan not found"
        }),404
    try:
        db.session.delete(loan)
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Db commit is failed")
        return jsonify({
            "success":False,
            "message":"Something went wrong"
        })  ,500   
    return jsonify({
        "success":True,
        "message":"loan deleted successfully"
    }),200


#loan repayment

@loan_bp.route("/loan/repayment/<int:loan_id>",methods=["POST"])
@jwt_required()
@limiter.limit("25 per minute",key_func=lambda:get_jwt_identity())
def repayment(loan_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json(silent=True)
    if not data:
        return jsonify({
            "success":False,
            "message":"Request body is required"
        }),400
    paid_amount=data.get("paid_amount")
    if not paid_amount:
        return jsonify({
            "success":False,
            "message":"paid amount is required"
        }),400
    try:
            paid_amount=float(paid_amount) if paid_amount is not None else None
    except (ValueError,TypeError):
            return jsonify({
                "success":False,
                "message":"Paid amount must be number"
            })    ,400
    

    if paid_amount<=0:
        return jsonify({
            "success":False,
            "message":"Paid amount must be positive"
        })    ,400

    loan=Loan.query.filter_by(
        id=loan_id,
        user_id=current_user_id).first()

    if not loan:
        return jsonify({
            "success":False,
            "message":"Loan not found"
        })        ,404

    if loan.status=='closed':
        return jsonify({
            "success":False,
            "message":"This loan is already completed"
        })    ,400
    m=float(loan.remaining_amount)
    
    if paid_amount>m:
        return jsonify({
            "success":False,
            "message": f"Payment cannot exceed remaining amount ({m})"
        })    ,400

    loan.remaining_amount=m-paid_amount

    if loan.remaining_amount==0:
        loan.status='closed'
    
    try:
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
        "message":"Repayment added successfully",
        "remaining_amount":float(loan.remaining_amount),
        "status":loan.status
    })    ,200