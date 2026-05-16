from flask import Blueprint, jsonify,request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from dbms.db import db
from models.borrow import Borrow

borrow_bp=Blueprint("borrow_bp",__name__)
@borrow_bp.route("/borrow/add",methods=["POST"])
@jwt_required()
def borrow():
    current_user_id=int(get_jwt_identity())
    data=request.get_json()
    person_name=data.get("person_name")
    amount=data.get("amount")
    borrow_type=data.get("type")
    due_date=data.get("due_date")
    note=data.get("note")
    if not person_name or not amount or not borrow_type:
        return jsonify({
            "message":"All the fields are required "
        }) ,400

    borrow_type = borrow_type.strip().lower()    

    if borrow_type not in ['borrowed','lent']:
        return jsonify({
            "message":"Type must be borrowed or lent "
        }),400


    due_date_obj = None
    if due_date:
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
    
    new_borrower=Borrow(
        person_name=person_name,
        amount=float(amount),
        type=borrow_type,
        due_date=due_date_obj,
        note=note,
        user_id=current_user_id
    )

    db.session.add(new_borrower)
    db.session.commit()
    return jsonify({
        "message":"Borrowed/Lend added successfully"
    }),201


#get all borrower
@borrow_bp.route("/borrow/get",methods=["GET"])
@jwt_required()
def get_borrow():
    current_user_id=int(get_jwt_identity())
    borrows=Borrow.query.filter_by(
        user_id=current_user_id
    ).all()

    borrow_list=[]
    for borrow in borrows:
        borrow_list.append({
            "id":borrow.id,
            "person_name":borrow.person_name,
            "amount":borrow.amount,
            "type":borrow.type,
            "due_date":borrow.due_date,
            "status":borrow.status,
            "note":borrow.note,
            "created_at":borrow.created_at
        })

    return jsonify({
        "message":borrow_list
    }),200


#Update
@borrow_bp.route("/borrow/update/<int:borrow_id>",methods=["PUT"])
@jwt_required()
def update_borrow(borrow_id):
    current_user_id=int(get_jwt_identity())
    data=request.get_json()
    borrow=Borrow.query.filter_by(
        user_id=current_user_id,
        id=borrow_id
    ).first()

    if not borrow:
        return jsonify({
            "message":"Borrow not found"
        }),400

    borrow.person_name=data.get("person_name",borrow.person_name)
    if data.get("amount"):
        borrow.amount = float(data.get("amount"))
    borrow.type=data.get("type",borrow.type)
    borrow.status=data.get("status",borrow.status)
    borrow.note=data.get("note",borrow.note)
    if data.get("due_date"):
        borrow.due_date=datetime.strptime(data.get("due_date"),"%Y-%m-%d")

    db.session.commit()
    return jsonify({
        "message":"Borrow/Lend Updated successfully"
    }),200

#dalete borrow
@borrow_bp.route("/borrow/delete/<int:borrow_id>",methods=["DELETE"])
@jwt_required()
def delete_borrow(borrow_id):
    current_user_id=int(get_jwt_identity())
    borrow=Borrow.query.filter_by(
        id=borrow_id,
        user_id=current_user_id
    ).first()

    if not borrow:
        return jsonify({
            "messag":"borrow not found"
        }),404

    db.session.delete(borrow)
    db.session.commit()
    return jsonify({
        "message":"Borrow/Lend deleted successfully"
    })    ,200

#mark paid route
@borrow_bp.route("/borrow/mark-paid/<int:borrow_id>",methods=["PUT"])
@jwt_required()
def mark_paid(borrow_id):
    current_user_id=int(get_jwt_identity())
    borrow=Borrow.query.filter_by(
        id=borrow_id,
        user_id=current_user_id
    ).first()

    if not borrow:
        return jsonify({
            "message":"Borrow/Lend not found"
        }),404


    borrow.status="paid" 
    db.session.commit()
    return jsonify({
        "message":"mark-paid successfull"
    })    ,200
