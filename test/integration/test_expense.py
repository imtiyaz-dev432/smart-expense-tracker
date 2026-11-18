import pytest

from models.category import Category
from models.expense import Expense


@pytest.mark.integration
def test_expense_add_200(login_get_token,client,make_valid_expense_payload):
    token,_=login_get_token(username="Irfan@!23",password="Valid@123")
    payload=make_valid_expense_payload()
    r=client.post("/expense/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    assert r.get_json()["success"] is True


@pytest.mark.integration
@pytest.mark.parametrize("missing", ["title", "amount", "category"])
def test_add_expense_missing_fields(client,make_valid_expense_payload,missing,database,login_get_token):
    token,_=login_get_token(username="Irfan@!23",password="Valid@123")
    payload=make_valid_expense_payload()
    payload.pop(missing)
    r=client.post("/expense/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    assert r.get_json()["success"] is False


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100, "%%$$", "abc"])
def test_add_expense_invalid_amount(login_get_token,make_valid_expense_payload,bad_amount,client):
    token,_=login_get_token(username="Irfan@!23",password="Valid@123")
    payload=make_valid_expense_payload(amount=bad_amount)
    r=client.post("/expense/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    assert r.get_json()["success"] is False


@pytest.mark.integration
def test_add_expense_auto_creates_category(login_get_token,database,make_valid_expense_payload,client):
    token,_=login_get_token(username="Irfan@!23",password="Valid@123")
    payload=make_valid_expense_payload(category="Groceries")
    r=client.post("/expense/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    cat = Category.query.filter_by(name="Groceries").first()
    assert cat is not None


@pytest.mark.integration
def test_add_expense_without_auth(make_valid_expense_payload,client):
    payload=make_valid_expense_payload(category="Groceries")
    r=client.post("/expense/add",json=payload)
    assert r.status_code==401


@pytest.mark.integration
def test_add_expense_with_fake_token_auth(make_valid_expense_payload,client):
    payload=make_valid_expense_payload(category="Groceries")
    r=client.post("/expense/add",json=payload,headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_add_expense_creates_in_database(login_get_token,client,make_valid_expense_payload):
    token,_=login_get_token(username="Irfan@!23",password="Valid@123")
    payload=make_valid_expense_payload()
    r=client.post("/expense/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    assert r.get_json()["success"] is True
    expense=Expense.query.filter_by(title="Lunch").first()
    assert expense.amount==200
    assert expense.category=="Food"


@pytest.mark.integration
def test_with_success_get(login_get_token,client):
    token,_=login_get_token(username="Irfan@!23",password="Valid@123")
    r=client.get("/expense/all",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body = r.get_json()
    assert body["success"] is True
    assert body["expenses"] == []


@pytest.mark.integration
def test_get_expenses_returns_all_user_expenses(login_get_token,client,make_valid_expense_payload):
    token,_=login_get_token(username="Irfan@!23",password="Valid@123")
    payload=make_valid_expense_payload()
    r=client.post("/expense/add",headers={'Authorization':f"Bearer {token}"},json=payload)
    assert r.status_code==201
    payload1=make_valid_expense_payload(title="Movie",amount=500,category="Entertainment")
    r=client.post("/expense/add",headers={'Authorization':f"Bearer {token}"},json=payload1)
    assert r.status_code==201
    r=client.get("/expense/all",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code == 200
    expenses = r.get_json()["expenses"]
    assert len(expenses) == 2


@pytest.mark.integration
def test_without_auth(client):
    r=client.get("/expense/all")
    assert r.status_code==401


@pytest.mark.integration
def test_with_fake_token_auth(client):
    r=client.get("/expense/all",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_get_expenses_returns_only_own_expenses(login_get_token,client,make_verified_user,make_valid_expense_payload):
    token1, _ = login_get_token(username="userA", password="Value@123")
    token2, _ = login_get_token(username="userB", password="Value@123")
    payload=make_valid_expense_payload()
    r=client.post("/expense/add",json=payload,headers={"Authorization":f"Bearer {token1}"})
    assert r.status_code==201
    assert r.get_json()["success"] is True
    payload=make_valid_expense_payload(title="Movies")
    r=client.post("/expense/add",json=payload,headers={"Authorization":f"Bearer {token2}"})
    assert r.status_code==201
    assert r.get_json()["success"] is True
    r = client.get("/expense/all", headers={"Authorization":f"Bearer {token2}"})
    expenses = r.get_json()["expenses"]
    assert len(expenses) == 1
    assert expenses[0]["title"] == "Movies"




@pytest.mark.integration
def test_update_expense_title_success(login_get_token,make_valid_expense_payload,client,database):
    token, _ = login_get_token(username="userB", password="Value@123")
    make_valid_expense_payload()
    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    expense=Expense.query.filter_by(title="Lunch").first()

    r=client.patch(f"/expense/update/{expense.id}",headers={"Authorization":f"Bearer {token}"},json={"title":"Cloth"})
    assert r.status_code==200




@pytest.mark.integration
def test_update_expense_amount_success(login_get_token,make_valid_expense_payload,client,database):
    token, _ = login_get_token(username="userB", password="Value@123")
    make_valid_expense_payload()
    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    expense=Expense.query.filter_by(title="Lunch").first()

    r=client.patch(f"/expense/update/{expense.id}",headers={"Authorization":f"Bearer {token}"},json={"amount":98.76})
    assert r.status_code==200


@pytest.mark.integration
def test_update_expense_category_success(login_get_token,make_valid_expense_payload,client,database):
    token, _ = login_get_token(username="userB", password="Value@123")
    make_valid_expense_payload()
    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    expense=Expense.query.filter_by(title="Lunch").first()

    r=client.patch(f"/expense/update/{expense.id}",headers={"Authorization":f"Bearer {token}"},json={"category":"Food and Beverages"})
    database.session.refresh(expense)
    assert expense.category=="Food and Beverages"
    assert r.status_code==200


@pytest.mark.integration
def test_update_expense_description_success(login_get_token,make_valid_expense_payload,client,database):
    token, _ = login_get_token(username="userB", password="Value@123")
    make_valid_expense_payload()
    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    expense=Expense.query.filter_by(title="Lunch").first()

    r=client.patch(f"/expense/update/{expense.id}",headers={"Authorization":f"Bearer {token}"},json={"description":"my family dinner"})
    assert r.status_code==200


@pytest.mark.integration
def test_update_expense_not_found(login_get_token,make_valid_expense_payload,client,database):
    token, _ = login_get_token(username="userB", password="Value@123")
    make_valid_expense_payload()
    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    Expense.query.filter_by(title="Lunch").first()

    r=client.patch("/expense/update/9877",headers={"Authorization":f"Bearer {token}"},json={"description":"my family dinner"})
    assert r.status_code==404


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100,"abc", "", None])
def test_update_expense_invalid_amount(
    client, database, login_get_token, make_valid_expense_payload, bad_amount
):
    token, _ = login_get_token(username="userA", password="Value@123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(title="Lunch"),
        headers=headers,
    )
    assert r.status_code == 201

    exp = Expense.query.filter_by(title="Lunch").first()
    assert exp is not None

    r = client.patch(
        f"/expense/update/{exp.id}",
        json={"amount": bad_amount},
        headers=headers,
    )
    assert r.status_code == 400
    assert r.get_json()["success"] is False


@pytest.mark.integration
def test_update_expense_empty_body(
    client, database, login_get_token, make_valid_expense_payload
):
    token, _ = login_get_token(username="userA", password="Value@123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(title="Lunch"),
        headers=headers,
    )
    assert r.status_code == 201

    exp = Expense.query.filter_by(title="Lunch").first()

    r = client.patch(
        f"/expense/update/{exp.id}",
        json={},
        headers=headers,
    )
    assert r.status_code == 400
    assert r.get_json()["success"] is False


@pytest.mark.integration
def test_delete_expense_success(
    client, database, login_get_token, make_valid_expense_payload
):
    token, _ = login_get_token(username="userA", password="Value@123")
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(title="To Delete"),
        headers=headers,
    )
    assert r.status_code == 201

    exp = Expense.query.filter_by(title="To Delete").first()
    assert exp is not None
    expense_id = exp.id

    r = client.delete(f"/expense/delete/{expense_id}", headers=headers)
    assert r.status_code == 200
    assert r.get_json()["success"] is True

    database.session.expire_all()
    assert database.session.get(Expense, expense_id) is None

@pytest.mark.integration
def test_delete_expense_not_found_404(client, database, login_get_token):
    token, _ = login_get_token(username="userA", password="Value@123")

    r = client.delete(
        "/expense/delete/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404
    assert r.get_json()["success"] is False


@pytest.mark.integration
def test_delete_other_user_expense_404(
    client, database, login_get_token, make_valid_expense_payload
):
    token_a, _ = login_get_token(username="userA", password="Value@123")
    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(title="A's lunch"),
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 201

    exp = Expense.query.filter_by(title="A's lunch").first()

    token_b, _ = login_get_token(username="userB", password="Value@123")
    r = client.delete(
        f"/expense/delete/{exp.id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 404

    database.session.expire_all()
    assert database.session.get(Expense, exp.id) is not None

@pytest.mark.integration
def test_delete_expense_without_auth_401(
    client, database, login_get_token, make_valid_expense_payload
):
    token, _ = login_get_token(username="userA", password="Value@123")
    r = client.post(
        "/expense/add",
        json=make_valid_expense_payload(title="Lunch"),
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201

    exp = Expense.query.filter_by(title="Lunch").first()

    r = client.delete(f"/expense/delete/{exp.id}")
    assert r.status_code == 401
