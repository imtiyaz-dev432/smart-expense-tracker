import pytest

from models.category import Category
from models.user import User


@pytest.mark.integration
def test_get_categories_returns_list(client, database, login_get_token):
    token, _ = login_get_token(username="userA", password="Value@123")
    r = client.get("/expense/categories", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


@pytest.mark.integration
def test_get_categories_excludes_other(client, database, login_get_token):
    token, _ = login_get_token(username="userA", password="Value@123")
    user = User.query.filter_by(username="userA").first()
    database.session.add(Category(name="Other", user_id=user.id))
    database.session.add(Category(name="CustomCat", user_id=user.id))
    database.session.commit()

    r = client.get("/expense/categories", headers={"Authorization": f"Bearer {token}"})
    names = [c["name"] for c in r.get_json()]
    assert "CustomCat" in names
    assert "Other" not in names


@pytest.mark.integration
def test_get_categories_own_only(
    client, database, login_get_token, make_verified_user
):
    token_a, _ = login_get_token(username="userA", password="Value@123")
    token_b, _ = login_get_token(username="userB", password="Value@123")
    user_a = User.query.filter_by(username="userA").first()
    user_b=User.query.filter_by(username="userB").first()
    database.session.add(Category(name="AOnly", user_id=user_a.id))
    database.session.add(Category(name="BOnly", user_id=user_b.id))
    database.session.commit()

    r = client.get("/expense/categories", headers={"Authorization": f"Bearer {token_a}"})
    names = [c["name"] for c in r.get_json()]
    assert "AOnly" in names
    assert "BOnly" not in names


@pytest.mark.integration
def test_get_categories_without_auth(client, database):
    r = client.get("/expense/categories")
    assert r.status_code == 401