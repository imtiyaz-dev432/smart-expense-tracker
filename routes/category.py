
from flask import Blueprint, request, jsonify
from dbms.db import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.category import Category

category_bp=Blueprint("category-bp",__name__)
@category_bp.route("/category",methods=["POST"])
@jwt_required()
def add_category():
    current_user_id=int(get_jwt_identity())
    data = request.get_json()
    name=data.get('name')
    if not name:
        return jsonify({
            "message":"name is required"
        }),400

    existing_category=Category.query.filter_by(
        name=name,
        user_id=current_user_id
    ) .first()   

    if existing_category:
        return jsonify ({
            "message":"name is already exist"
        }),409

    new_category=Category(
        name=name,
        user_id=current_user_id
    )    

    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        "message":"Added successfully"
    }) ,201   