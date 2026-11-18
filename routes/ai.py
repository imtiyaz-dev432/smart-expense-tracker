from datetime import UTC, datetime

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from dbms.db import db
from models.borrow import Borrow
from models.expense import Expense
from models.income import Income
from models.loan import Loan

ai_bp = Blueprint("ai_bp", __name__)


def format_amount(amount):
    return f"₹{float(amount or 0):,}"


@ai_bp.route("/ai/suggestion", methods=["GET"])
@jwt_required()
def ai():
    user_id = int(get_jwt_identity())
    suggestions = []

    now = datetime.now(UTC)
    month = now.month
    year = now.year

    income = float(Income.query.with_entities(func.sum(Income.amount)).filter(
        Income.user_id == user_id,
        func.extract("month", Income.date) == month,
        func.extract("year", Income.date) == year,
    ).scalar() or 0)

    expense = float(Expense.query.with_entities(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        func.extract("month", Expense.date) == month,
        func.extract("year", Expense.date) == year,
    ).scalar() or 0)

    if income == 0 and expense == 0:
        return jsonify({
            "success": True,
            "summary": {
                "expense_ratio": "N/A",
                "financial_health": "No Data",
                "financial_health_score": 0,
                "total_income": format_amount(0),
                "total_expense": format_amount(0),
                "remaining_balance": format_amount(0),
            },
            "suggestions": [{
                "type": "no_data",
                "priority": "info",
                "title": "Start Tracking",
                "message": "You haven't added any income or expenses yet. Add your first transaction to get personalized insights.",
                "action": "Go to Income or Expense section and add your first entry.",
            }],
        }), 200

    pending_count = Borrow.query.filter(
        Borrow.user_id == user_id,
        Borrow.status == "pending",
    ).count()

    pending_borrow = float(Borrow.query.with_entities(func.sum(Borrow.amount)).filter(
        Borrow.user_id == user_id,
        Borrow.borrow_type == "borrowed",
        Borrow.status == "pending",
    ).scalar() or 0)

    pending_lent = float(Borrow.query.with_entities(func.sum(Borrow.amount)).filter(
        Borrow.user_id == user_id,
        Borrow.borrow_type == "lent",
        Borrow.status == "pending",
    ).scalar() or 0)

    remaining = income - expense

    if income == 0 and expense > 0:
        expense_ratio = 100.0
        health_score = 0.0
        health = "Risky"
    elif income > 0:
        expense_ratio = round((expense / income) * 100, 2)
        health_score = round(max(0, 100 - expense_ratio), 2)
        if expense_ratio > 100:
            health = "Risky"
        elif expense_ratio >= 70:
            health = "Moderate"
        else:
            health = "Good"
    else:
        expense_ratio = 0.0
        health_score = 0.0
        health = "No Income Yet"

    if income > 0 and expense > income:
        suggestions.append({
            "type": "overspending_alert",
            "priority": "high",
            "title": "Overspending Alert",
            "message": "Your expenses are higher than your income this month.",
            "action": "Reduce unnecessary spending like shopping, food delivery, and entertainment.",
        })

    if income > 0 and remaining < income * 0.2:
        suggestions.append({
            "type": "low_balance_warning",
            "priority": "medium",
            "title": "Low Balance Warning",
            "message": f"Your remaining balance is low this month: {format_amount(remaining)}.",
            "action": "Try to save at least 20% of your monthly income.",
        })

    if income > 0 and remaining >= income * 0.2:
        suggestions.append({
            "type": "saving_suggestion",
            "priority": "low",
            "title": "Good Saving Progress",
            "message": f"You saved {format_amount(remaining)} this month.",
            "action": "Move some money into an emergency fund or savings account.",
        })

    category_rows = db.session.query(
        Expense.category, func.sum(Expense.amount)  ).filter(
        Expense.user_id == user_id,
        func.extract("month", Expense.date) == month,
        func.extract("year", Expense.date) == year,
    ).group_by(Expense.category).all() # this and income and expense and all borrow lent is smae query working is same syntax is differ[Ek column → Model.query.with_entities()
# Multiple columns ya group by → db.session.query()

    if category_rows:
        top_cat, top_amt = None, 0.0
        for cat, amt in category_rows:
            amt = float(amt or 0)
            if amt > top_amt:
                top_amt = amt
                top_cat = cat

        suggestions.append({
            "type": "highest_spending_category",
            "priority": "medium",
            "title": "Highest Spending Category",
            "message": f"Your highest spending category is {top_cat} with {format_amount(top_amt)} this month.",
            "action": f"Set a monthly budget for {top_cat}.",
        })

        for cat, amt in category_rows:
            amt = float(amt or 0)
            if expense > 0:
                pct = (amt / expense) * 100
                if pct >= 40 and amt >= 1000:
                    suggestions.append({
                        "type": "category_budget_warning",
                        "priority": "medium",
                        "title": f"{cat} Spending is High",
                        "message": f"{cat} is {round(pct, 2)}% of your total monthly expense.",
                        "action": f"Try to reduce spending on {cat} next month.",
                    })

    if pending_lent > 0:
        suggestions.append({
            "type": "pending_lent_reminder",
            "priority": "medium",
            "title": "Money to Collect",
            "message": f"You have {format_amount(pending_lent)} pending to collect from others.",
            "action": "Send a polite reminder and mark it as paid when received.",
        })

    if pending_borrow > 0:
        suggestions.append({
            "type": "pending_borrowed_reminder",
            "priority": "medium",
            "title": "Money to Return",
            "message": f"You have {format_amount(pending_borrow)} pending to return.",
            "action": "Plan repayment on time to avoid confusion.",
        })

    if pending_count >= 3:
        suggestions.append({
            "type": "borrow_management",
            "priority": "medium",
            "title": "Multiple Pending Records",
            "message": f"You have {pending_count} pending borrow/lend records.",
            "action": "Review and clear old pending records this week.",
        })

    active_loans = Loan.query.filter_by(user_id=user_id, status="active").all()

    if active_loans:
        emi_total = sum(float(l.monthly_emi or 0) for l in active_loans)
        word = "loan" if len(active_loans) == 1 else "loans"
        suggestions.append({
            "type": "active_loan_warning",
            "priority": "high",
            "title": "Active Loan Repayment",
            "message": f"You have {len(active_loans)} active {word} with total monthly EMI of {format_amount(emi_total)}.",
            "action": "Keep EMI money aside before spending on non-essential items.",
        })

    for loan in active_loans:
        if loan.due_date:
            days_left = (loan.due_date - now).days
            if 0 <= days_left <= 7:
                suggestions.append({
                    "type": "emi_due_soon",
                    "priority": "high",
                    "title": "EMI Due Soon",
                    "message": f"{loan.loan_name} EMI is due in {days_left} days.",
                    "action": f"Keep {format_amount(loan.monthly_emi)} ready to avoid late payment.",
                })

    if expense >= 1000:
        target = 3 * expense
        suggestions.append({
            "type": "emergency_fund",
            "priority": "low",
            "title": "Emergency Fund Goal",
            "message": f"Based on your monthly expense, your 3-month emergency fund target is {format_amount(target)}.",
            "action": "Start saving a fixed small amount every month.",
        })

    if not suggestions:
        suggestions.append({
            "type": "positive_feedback",
            "priority": "low",
            "title": "Good Financial Control",
            "message": "Your income, expenses, and loans look balanced this month.",
            "action": "Keep tracking your transactions regularly.",
        })

    return jsonify({
        "success": True,
        "summary": {
            "expense_ratio": f"{expense_ratio:.2f}%",
            "financial_health": health,
            "financial_health_score": int(health_score),
            "total_income": format_amount(income),
            "total_expense": format_amount(expense),
            "remaining_balance": format_amount(remaining),
        },
        "suggestions": suggestions,
    }), 200