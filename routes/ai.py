from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from datetime import datetime

from dbms.db import db
from models.income import Income
from models.expense import Expense
from models.loan import Loan
from models.borrow import Borrow
from models.subscribe import Subscription

def format_amount(amount):
    return f"{int(amount):,}"
ai_bp = Blueprint("ai_bp", __name__)


@ai_bp.route("/ai/suggestion", methods=["GET"])
@jwt_required()
def ai():
    current_user_id = int(get_jwt_identity())

    suggestions = []

    current_date = datetime.utcnow()
    current_month = current_date.month
    current_year = current_date.year

    # Monthly income
    total_income = Income.query.with_entities(
        func.sum(Income.amount)
    ).filter(
        Income.user_id == current_user_id,
        func.extract("month", Income.date) == current_month,
        func.extract("year", Income.date) == current_year
    ).scalar() or 0

    # Monthly expense
    total_expense = Expense.query.with_entities(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user_id,
        func.extract("month", Expense.date) == current_month,
        func.extract("year", Expense.date) == current_year
    ).scalar() or 0

    total_income = float(total_income or 0)
    total_expense = float(total_expense or 0)

    remaining_balance = total_income - total_expense

    #Borrow and lend count
    pending_borrow_lent_count=Borrow.query.filter(
        Borrow.user_id==current_user_id,
        Borrow.status=='pending'
    ).count()
    
    #amount of both lend and borrow
    pending_borrow_total=Borrow.query.with_entities(
        func.sum(Borrow.amount)).filter(
          Borrow.user_id==current_user_id,
          Borrow.type=="borrowed",
          Borrow.status=="pending").scalar() or 0

    pending_lent_total=Borrow.query.with_entities(
        func.sum(Borrow.amount)).filter(
            Borrow.user_id==current_user_id,
            Borrow.type=="lent",
            Borrow.status=="pending"
        ).scalar() or 0      


    # Financial health
    total_income = total_income or 0
    total_expense = total_expense or 0

    remaining_balance = total_income - total_expense

    financial_health = "Good"
    expense_ratio = 0
    financial_health_score = 100

    if total_income == 0 and total_expense > 0:
     expense_ratio = 100
     financial_health_score = 0
     financial_health = "Risky"

    elif total_income > 0:
       expense_ratio = round((total_expense / total_income) * 100, 2)
       financial_health_score = round(max(0, 100 - expense_ratio), 2)

       if expense_ratio > 100:
        financial_health = "Risky"
       elif expense_ratio >= 70:
        financial_health = "Moderate"
       else:
        financial_health = "Good"

    else:
     expense_ratio = 0
     financial_health_score = 100
     financial_health = "Good"
    # Overspending alert
    if total_income > 0 and total_expense > total_income:
        suggestions.append({
            "type": "overspending_alert",
            "priority": "high",
            "title": "Overspending Alert",
            "message": "Your expenses are higher than your income this month.",
            "action": "Reduce unnecessary spending like shopping, food delivery, and entertainment."
        })

    # Low balance warning
    if total_income > 0 and remaining_balance < (total_income * 0.2):
        suggestions.append({
            "type": "low_balance_warning",
            "priority": "medium",
            "title": "Low Balance Warning",
            "message": f"Your remaining balance is low this month: {format_amount(remaining_balance)}.",
            "action": "Try to save at least 20% of your monthly income."
        })

    # Good saving suggestion
    if total_income > 0 and remaining_balance >= (total_income * 0.2):
        suggestions.append({
            "type": "saving_suggestion",
            "priority": "low",
            "title": "Good Saving Progress",
            "message": f"You saved {format_amount(remaining_balance)} this month.",
            "action": "Move some money into an emergency fund or savings account."
        })
   
    # Category-wise expense
    category_data = db.session.query(
        Expense.category,
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == current_user_id,
        func.extract("month", Expense.date) == current_month,
        func.extract("year", Expense.date) == current_year
    ).group_by(
        Expense.category
    ).all()

    # Highest spending category
    if category_data:
        highest_category = None
        highest_amount = 0.0

        for category, amount in category_data:
            amount = float(amount or 0)

            if amount > highest_amount:
                highest_amount = amount
                highest_category = category

        suggestions.append({
            "type": "highest_spending_category",
            "priority": "medium",
            "title": "Highest Spending Category",
            "message": f"Your highest spending category is {highest_category} with {format_amount(highest_amount)} this month.",
            "action": f"Set a monthly budget for {highest_category}."
        })

        # Category spending warning
        for category, amount in category_data:
            amount = float(amount or 0)

            if total_expense > 0:
                percentage = (amount / total_expense) * 100

                if percentage >= 40 and amount >= 1000:
                    suggestions.append({
                        "type": "category_budget_warning",
                        "priority": "medium",
                        "title": f"{category} Spending is High",
                        "message": f"{category} is {round(percentage, 2)}% of your total monthly expense.",
                        "action": f"Try to reduce spending on {category} next month."
                    })

    #Borrow / Lend conditions
    if pending_lent_total>0:
        suggestions.append({
        "type": "pending_lent_reminder",
        "priority": "medium",
        "title": "Money to Collect",
        "message": f"You have {format_amount(pending_lent_total)} pending to collect from others.",
        "action": "Send a polite reminder and mark it as paid when received."
    })    


    if  pending_borrow_total>0:
            suggestions.append({
        "type": "pending_borrowed_reminder",
        "priority": "medium",
        "title": "Money to Return",
        "message": f"You have {format_amount(pending_borrow_total)} pending to return.",
        "action": "Plan repayment on time to avoid confusion."
    })


    if pending_borrow_lent_count >= 3:
     suggestions.append({
        "type": "borrow_lend_management",
        "priority": "medium",
        "title": "Multiple Pending Records",
        "message": f"You have {pending_borrow_lent_count} pending borrow/lend records.",
        "action": "Review and clear old pending records this week."
    })                

    # Active loan warning
    active_loans = Loan.query.filter_by(
        user_id=current_user_id,
        status="active"
    ).all()

    if active_loans:
        total_monthly_emi = 0.0

        for loan in active_loans:
            total_monthly_emi += float(loan.monthly_emi or 0)
            loan_text = "loan" if len(active_loans) == 1 else "loans"
        suggestions.append({
            "type": "active_loan_warning",
            "priority": "high",
            "title": "Active Loan Repayment",
            "message": f"You have {len(active_loans)} active {loan_text} with total monthly EMI of {format_amount(total_monthly_emi)}.",
            "action": "Keep EMI money aside before spending on non-essential items."
        })

    # EMI due soon
    today = datetime.utcnow()

    for loan in active_loans:
        if loan.due_date:
            days_left = (loan.due_date - today).days

            if 0 <= days_left <= 7:
                suggestions.append({
                    "type": "emi_due_soon",
                    "priority": "high",
                    "title": "EMI Due Soon",
                    "message": f"{loan.loan_name} EMI is due in {days_left} days.",
                    "action": f"Keep {format_amount(loan.monthly_emi)} ready to avoid late payment."
                })

    # Emergency fund suggestion
    if total_expense >= 1000:
        emergency_fund_target = 3 * total_expense

        suggestions.append({
            "type": "emergency_fund",
            "priority": "low",
            "title": "Emergency Fund Goal",
            "message": f"Based on your monthly expense, your 3-month emergency fund target is {format_amount(emergency_fund_target)}.",
            "action": "Start saving a fixed small amount every month."
        })

    # Positive fallback
    if not suggestions:
        suggestions.append({
            "type": "positive_feedback",
            "priority": "low",
            "title": "Good Financial Control",
            "message": "Your income, expenses, and loans look balanced this month.",
            "action": "Keep tracking your transactions regularly."
        })

    return jsonify({
        "summary": {
            "expense_ratio":f"{expense_ratio}%",
            "financial_health": financial_health,
            "financial_health_score":int(financial_health_score),
            "total_income": format_amount(total_income),
            "total_expense": format_amount(total_expense),
            "remaining_balance":format_amount(remaining_balance)
        },
        "suggestions": suggestions
    }), 200


    