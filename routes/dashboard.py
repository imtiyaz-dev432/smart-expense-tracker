from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime,timedelta
from models.loan import Loan
from dbms.db import db
from models.income import Income
from models.expense import Expense
from models.borrow import Borrow
from models.subscribe import Subscription
#very very pmi think
dashboard_bp=Blueprint("dashboard-bp",__name__)
@dashboard_bp.route("/dashboard",methods=["GET"])
@jwt_required()
def dashboard():
    current_user_id=int(get_jwt_identity())
    total_income=db.session.query(func.sum(Income.amount)).filter_by(user_id=current_user_id).scalar() or 0 #scalar calculate sum of amount directly
    total_expense=db.session.query(func.sum(Expense.amount)).filter_by(user_id=current_user_id).scalar() or 0
    #user ne dusre ko kitne paise diye hai
    
#user ne kitne paise dusro se liye hai
   
    
    pending_borrow_lend_count = Borrow.query.filter(
    Borrow.user_id == current_user_id,
    Borrow.status == "pending"
).count()
    
    pending_borrow_total=Borrow.query.with_entities(
        func.sum(Borrow.amount)).filter(
            Borrow.user_id==current_user_id,
            Borrow.type=='borrowed',
            Borrow.status=='pending'
        ).scalar() or 0

    pending_lent_total=Borrow.query.with_entities(
        func.sum(Borrow.amount)).filter(
            Borrow.user_id==current_user_id,
            Borrow.type=="lent",
            Borrow.status=="pending"
        ) .scalar() or 0 
    #loan count
    pending_loan_count=Loan.query.filter(
        Loan.user_id==current_user_id,
        Loan.status=='active'
    ).count()
#total loan amount
    total_loan_amount=Loan.query.with_entities(
        func.sum(Loan.total_amount)).filter(
            Loan.user_id==current_user_id,
            Loan.status=="active").scalar() or 0
#total reamianing amount
    total_remaining_amount=Loan.query.with_entities(
        func.sum(Loan.remaining_amount)).filter(
            Loan.user_id==current_user_id,
            Loan.status=="active"
        ).scalar() or 0

#Monthly emi
    total_monthly_emi=Loan.query.with_entities(
        func.sum(Loan.monthly_emi)).filter(
            Loan.user_id==current_user_id,
            Loan.status=="active").scalar() or 0
       #completed loan count 
    completed_loan_count = Loan.query.filter(
    Loan.user_id == current_user_id,
    Loan.status == "completed"
).count()    

    #add subscription logic
    today=datetime.utcnow()
    next_7_days=today+timedelta(days=7)

    active_subscription_count = Subscription.query.filter(
    Subscription.user_id == current_user_id,
    Subscription.status == "active"
).count()

    active_subscriptions = Subscription.query.filter(
    Subscription.user_id == current_user_id,
    Subscription.status == "active"
).all()

    monthly_subscription_total = 0

    for sub in active_subscriptions:
     amount = float(sub.amount or 0)

     if sub.billing_cycle == "monthly":
        monthly_subscription_total += amount

     elif sub.billing_cycle == "yearly":
        monthly_subscription_total += amount / 12

     elif sub.billing_cycle == "weekly":
        monthly_subscription_total += amount * 4

    upcoming_subscription_count = Subscription.query.filter(
    Subscription.user_id == current_user_id,
    Subscription.status == "active",
    Subscription.next_billing_date >= today,
    Subscription.next_billing_date <= next_7_days
).count()

    if total_income is None:
        total_income=0
    elif total_expense is None:
        total_expense=0

    balance=total_income-total_expense
    return jsonify({
        "total_income":total_income,       
       "total_expense": total_expense,
       "balance":balance,
       "pending_borrow_lend_count":pending_borrow_lend_count,
       "pending_borrow_total":pending_borrow_total,
       "pending_lent_total":pending_lent_total,
       "total_loan_remaining": total_remaining_amount,
    "total_monthly_emi": total_monthly_emi,
    "active_loan_count": pending_loan_count,
    "completed_loan_count": completed_loan_count,
    "active_subscription_count": active_subscription_count,
"monthly_subscription_total": monthly_subscription_total,
"upcoming_subscription_count": upcoming_subscription_count
    }),200


#categgory wise expense
@dashboard_bp.route("/dashboard/category-wise-expense",methods=["GET"])
@jwt_required()
def category_expense():
       current_user_id=int(get_jwt_identity())
       category_data = db.session.query(
    Expense.category,
    func.sum(Expense.amount)
).filter(
    Expense.user_id == current_user_id
).group_by(
    Expense.category
).all()

       result={}
       for category,total_amount in category_data:
        result[category]=total_amount

       return jsonify(
        {
            "message":result
        }
       )  ,200

#monthly report
@dashboard_bp.route("/dashboard/monthly-report",methods=["GET"])
@jwt_required()
def monthly_report():
   current_user_id=int(get_jwt_identity())
   current_date=datetime.utcnow()
   current_month=current_date.month
   current_year=current_date.year

   monthly_income = Income.query.with_entities(
    func.sum(Income.amount)
).filter(
    Income.user_id == current_user_id,
    func.extract("month", Income.date) == current_month,
    func.extract("year", Income.date) == current_year
).scalar() or 0
    
   monthly_expense = Expense.query.with_entities(
        func.sum(Expense.amount)
    ).filter(
    Expense.user_id == current_user_id,
        func.extract("month", Expense.date) == current_month,
        func.extract("year", Expense.date) == current_year
    ).scalar() or 0

   monthly_balance=monthly_income-monthly_expense
   #subscription
   monthly_subscription_total=0
   active_subscription=Subscription.query.filter(
    Subscription.user_id==current_user_id,
    Subscription.status=="active"

   ).all()
   for sub in active_subscription:
    amount=float(sub.amount or 0)
    cycle=sub.billing_cycle.strip().lower()
    if cycle=="monthly":
        monthly_subscription_total+=amount
    elif cycle=="weekly":
        monthly_subscription_total+=amount*4

    else:
        monthly_subscription_total+=amount/12
    
    #lend and borrow total 
    total_borrow=Borrow.query.with_entities(
        func.sum(Borrow.amount)).filter(
            Borrow.user_id==current_user_id,
            Borrow.type=="borrowed",
            func.extract("month",Borrow.created_at)==current_month,
            func.extract("year",Borrow.created_at)==current_year
        ).scalar() or 0

    total_lend=Borrow.query.with_entities(
        func.sum(Borrow.amount)).filter(
            Borrow.user_id==current_user_id,
            Borrow.type=="lent",
            Borrow.status=="pending",
            func.extract("month",Borrow.created_at)==current_month,
            func.extract("year",Borrow.created_at)==current_year
        ) .scalar() or 0    
    
    
    
    if total_borrow!=0 or total_lend!=0:
            return jsonify({ "month": current_month, "year": current_year, "monthly_income": monthly_income, "monthly_expense": monthly_expense, "monthly_balance": monthly_balance,
   "monthly_subscription_total":monthly_subscription_total ,
  "total_lend":total_lend,    "total_borrow":total_borrow}), 200

   
   return jsonify({ "month": current_month, "year": current_year, "monthly_income": monthly_income, "monthly_expense": monthly_expense, "monthly_balance": monthly_balance,
   "monthly_subscription_total":monthly_subscription_total}),200