from datetime import UTC, datetime, timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from dbms.db import db
from models.borrow import Borrow
from models.expense import Expense
from models.income import Income
from models.loan import Loan
from models.subscribe import Subscription

dashboard_bp = Blueprint("dashboard-bp", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())

    income = db.session.query(func.sum(Income.amount)).filter_by(user_id=user_id).scalar() or 0
    expense = db.session.query(func.sum(Expense.amount)).filter_by(user_id=user_id).scalar() or 0

    pending_borrow_count = Borrow.query.filter(
        Borrow.user_id == user_id, Borrow.status == "pending"
    ).count()

    borrow_total = Borrow.query.with_entities(func.sum(Borrow.amount)).filter(
        Borrow.user_id == user_id,
        Borrow.borrow_type == "borrowed",
        Borrow.status == "pending",
    ).scalar() or 0

    lent_total = Borrow.query.with_entities(func.sum(Borrow.amount)).filter(
        Borrow.user_id == user_id,
        Borrow.borrow_type == "lent",
        Borrow.status == "pending",
    ).scalar() or 0

    active_loans = Loan.query.filter(
        Loan.user_id == user_id, Loan.status == "active"
    ).count()

    closed_loans = Loan.query.filter(
        Loan.user_id == user_id, Loan.status == "closed"
    ).count()

    loan_amount = Loan.query.with_entities(func.sum(Loan.total_amount)).filter(
        Loan.user_id == user_id, Loan.status == "active"
    ).scalar() or 0

    loan_remaining = Loan.query.with_entities(func.sum(Loan.remaining_amount)).filter(
        Loan.user_id == user_id, Loan.status == "active"
    ).scalar() or 0

    monthly_emi = Loan.query.with_entities(func.sum(Loan.monthly_emi)).filter(
        Loan.user_id == user_id, Loan.status == "active"
    ).scalar() or 0

    subs = Subscription.query.filter(
        Subscription.user_id == user_id, Subscription.status == "active"
    ).all()

    subs_monthly = 0.0
    for s in subs:
        amt = float(s.amount or 0)
        cycle = (s.billing_cycle or "").strip().lower()
        if cycle == "monthly":
            subs_monthly += amt
        elif cycle == "weekly":
            subs_monthly += amt * 4
        elif cycle == "yearly":
            subs_monthly += amt / 12

    now = datetime.now(UTC)
    week_ahead = now + timedelta(days=7)

    upcoming_subs = Subscription.query.filter(
        Subscription.user_id == user_id,
        Subscription.status == "active",
        Subscription.next_billing_date >= now,
        Subscription.next_billing_date <= week_ahead,
    ).count()

    return jsonify({
        "success": True,
        "total_income": float(income),
        "total_expense": float(expense),
        "balance": float(income - expense),
        "pending_borrow_lend_count": pending_borrow_count,
        "pending_borrow_total": float(borrow_total),
        "pending_lent_total": float(lent_total),
        "active_loan_count": active_loans,
        "completed_loan_count": closed_loans,
        "total_loan_amount": float(loan_amount),
        "total_loan_remaining": float(loan_remaining),
        "total_monthly_emi": float(monthly_emi),
        "active_subscription_count": len(subs),
        "monthly_subscription_total": float(subs_monthly),
        "upcoming_subscription_count": upcoming_subs,
    }), 200


@dashboard_bp.route("/dashboard/category-wise-expense", methods=["GET"])
@jwt_required()
def category_expense():
    user_id = int(get_jwt_identity())

    rows = db.session.query(
        Expense.category,
        func.sum(Expense.amount),
    ).filter(Expense.user_id == user_id).group_by(Expense.category).all()

    data = {cat: float(total or 0) for cat, total in rows}

    return jsonify({"success": True, "category_wise_expense": data}), 200


@dashboard_bp.route("/dashboard/monthly-report", methods=["GET"])
@jwt_required()
def monthly_report():
    user_id = int(get_jwt_identity())
    now = datetime.now(UTC)
    month = now.month
    year = now.year

    income = Income.query.with_entities(func.sum(Income.amount)).filter(
        Income.user_id == user_id,
        func.extract("month", Income.date) == month,
        func.extract("year", Income.date) == year,
    ).scalar() or 0

    expense = Expense.query.with_entities(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        func.extract("month", Expense.date) == month,
        func.extract("year", Expense.date) == year,
    ).scalar() or 0

    subs = Subscription.query.filter(
        Subscription.user_id == user_id, Subscription.status == "active"
    ).all()

    subs_monthly = 0.0
    for s in subs:
        amt = float(s.amount or 0)
        cycle = (s.billing_cycle or "").strip().lower()
        if cycle == "monthly":
            subs_monthly += amt
        elif cycle == "weekly":
            subs_monthly += amt * 4
        elif cycle == "yearly":
            subs_monthly += amt / 12

    borrow = Borrow.query.with_entities(func.sum(Borrow.amount)).filter(
        Borrow.user_id == user_id,
        Borrow.borrow_type == "borrowed",
        func.extract("month", Borrow.created_at) == month,
        func.extract("year", Borrow.created_at) == year,
    ).scalar() or 0

    lend = Borrow.query.with_entities(func.sum(Borrow.amount)).filter(
        Borrow.user_id == user_id,
        Borrow.borrow_type == "lent",
        Borrow.status == "pending",
        func.extract("month", Borrow.created_at) == month,
        func.extract("year", Borrow.created_at) == year,
    ).scalar() or 0

    return jsonify({
        "success": True,
        "month": month,
        "year": year,
        "monthly_income": float(income),
        "monthly_expense": float(expense),
        "monthly_balance": float(income - expense),
        "monthly_subscription_total": float(subs_monthly),
        "total_lend": float(lend),
        "total_borrow": float(borrow),
    }), 200
    