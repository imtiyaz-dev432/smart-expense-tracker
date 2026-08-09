from dbms.db import db
from models.category import Category

def create_default_categories(user_id):
    default_categories = [
        "Food",
        "Health",
        "Travel",
        "Shopping",
        "Rent",
        "Bills",
        "Education",
        "Other"
    ]

    for category_name in default_categories:
        existing_category = Category.query.filter_by(
            name=category_name,
            user_id=user_id
        ).first()

        if not existing_category:
            category = Category(
                name=category_name,
                user_id=user_id
            )
            db.session.add(category)

    db.session.commit()