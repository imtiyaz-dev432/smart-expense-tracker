from models.category import Category


def create_default_categories(user):
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
    existing_categories={c.name for c in user.categories}

    for name in default_categories:
         if name not in existing_categories:
             user.categories.append(Category(name=name))
