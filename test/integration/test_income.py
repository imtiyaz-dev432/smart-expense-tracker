import pytest

from models.income import Income


@pytest.mark.integration
def test_income_add_success_200(client,login_get_token,database,build_income_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=build_income_payload()
    r=client.post("/income/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    body=r.get_json()
    assert body["success"] is True
    income=Income.query.filter_by(source="Salary").first()
    database.session.refresh(income)
    assert income.amount==5000

@pytest.mark.integration
@pytest.mark.parametrize("missing",["source","amount"])
def test_add_income_missing_fields(login_get_token,missing,client,build_income_payload):
     token,_=login_get_token(username="Poki@!22",password="Valid@!234")
     payload=build_income_payload()
     payload.pop(missing)
     r=client.post("/income/add",json=payload,headers={"Authorization":f"Bearer {token}"})
     assert r.status_code==400
     body=r.get_json()
     assert body["success"] is False


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100, "%%$$", "abc"])
def test_add_income_invalid_amount(login_get_token,client,bad_amount,build_income_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=build_income_payload(amount=bad_amount)
    r=client.post("/income/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert body["success"] is False



@pytest.mark.integration
def test_add_income_without_auth( client,build_income_payload):
    payload=build_income_payload()
    r=client.post("/income/add",json=payload)
    assert r.status_code==401


@pytest.mark.integration
def test_add_income_with_fake_token_auth(client,build_income_payload):
    payload=build_income_payload()
    r=client.post("/income/add",json=payload,headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422



@pytest.mark.integration
def test_add_income_empty_body(client,login_get_token,database,build_income_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    build_income_payload()
    r=client.post("/income/add",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert body["success"] is False



@pytest.mark.integration
def test_get_income_empty_returns_empty_list(client, database, login_get_token):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    r = client.get("/income/all", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json()["income"] == []


@pytest.mark.integration
def test_get_income_returns_all_user_incomes(
    client, database, login_get_token, build_income_payload
):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/income/add", json=build_income_payload(source="Salary"), headers=headers)
    client.post("/income/add", json=build_income_payload(source="Freelance"), headers=headers)
    r = client.get("/income/all", headers=headers)
    body=r.get_json()
    assert len((body)["income"]) == 2


@pytest.mark.integration
def test_get_income_only_own(client, database, login_get_token, build_income_payload):
    token_a, _ = login_get_token(username="userA", password="Value@123")
    token_b, _ = login_get_token(username="userB", password="Value@123")
    client.post("/income/add", json=build_income_payload(source="A Salary"),
                headers={"Authorization": f"Bearer {token_a}"})
    client.post("/income/add", json=build_income_payload(source="B Salary"),
                headers={"Authorization": f"Bearer {token_b}"})
    r = client.get("/income/all", headers={"Authorization": f"Bearer {token_a}"})
    body=r.get_json()
    assert len((body)["income"]) == 1


@pytest.mark.integration
def test_get_income_without_auth_401(client, database):
    r = client.get("/income/all")
    assert r.status_code == 401


@pytest.mark.integration
def test_get_income_amount_is_float(
    client, database, login_get_token, build_income_payload
):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/income/add", json=build_income_payload(), headers=headers)
    r = client.get("/income/all", headers=headers)

    income = r.get_json()["income"][0]
    assert isinstance(income["amount"], float)

@pytest.mark.integration
def test_get_income_with_fake_token_auth(client):
    r=client.get("/income/all",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422



@pytest.mark.integration
def test_update_income_success(client,build_income_payload,database,login_get_token):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    payload=build_income_payload()
    r=client.post("/income/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    income=Income.query.filter_by(source="Salary").first()
    r=client.patch(f"/income/update/{income.id}",headers={"Authorization":f"Bearer {token}"},json={"amount":850,"source":"Business"})
    assert r.status_code==200
    database.session.refresh(income)
    assert income.amount==850
    assert income.source=="Business"


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100,  "abc", ""])
def test_update_income_invalid_amount(
    client, database, login_get_token, build_income_payload, bad_amount
):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/income/add", json=build_income_payload(source="Salary"), headers=headers)
    income = Income.query.filter_by(source="Salary").first()

    r = client.patch(
        f"/income/update/{income.id}",
        json={"source": "Business", "amount": bad_amount},
        headers=headers,
    )
    assert r.status_code == 400
    assert r.get_json()["success"] is False


@pytest.mark.integration
def test_update_income_empty_body(
    client, database, login_get_token, build_income_payload
):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/income/add", json=build_income_payload(source="Salary"), headers=headers)
    income = Income.query.filter_by(source="Salary").first()

    r = client.patch(
        f"/income/update/{income.id}",
        json={},
        headers=headers,
    )
    assert r.status_code == 400
    assert r.get_json()["success"] is False


@pytest.mark.integration
def test_update_income_not_found_404(client, database, login_get_token):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")

    r = client.patch(
        "/income/update/99999",
        json={"source": "Business", "amount": 850},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


@pytest.mark.integration
def test_update_income_other_user_404(
    client, database, login_get_token, build_income_payload
):
    token_a, _ = login_get_token(username="userA", password="Value@123")
    client.post(
        "/income/add",
        json=build_income_payload(source="A Salary"),
        headers={"Authorization": f"Bearer {token_a}"},
    )
    income = Income.query.filter_by(source="A Salary").first()

    token_b, _ = login_get_token(username="userB", password="Value@123")
    r = client.patch(
        f"/income/update/{income.id}",
        json={"source": "Hacked", "amount": 999},
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 404

    database.session.expire_all()
    assert Income.query.get(income.id).source == "A Salary"


@pytest.mark.integration
def test_success_with_delete(login_get_token,client,build_income_payload,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=build_income_payload()
    r=client.post("/income/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    income=Income.query.filter_by(source="Salary").first()
    database.session.refresh(income)
    r=client.delete(f"/income/delete/{income.id}",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200


@pytest.mark.integration
def test_success_with_delete_unauth(login_get_token,client,build_income_payload,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=build_income_payload()
    r=client.post("/income/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    income=Income.query.filter_by(source="Salary").first()
    database.session.refresh(income)
    r=client.delete(f"/income/delete/{income.id}")
    assert r.status_code==401

@pytest.mark.integration
def test_success_with_delete_with_fake_token(login_get_token,client,build_income_payload,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=build_income_payload()
    r=client.post("/income/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    income=Income.query.filter_by(source="Salary").first()
    database.session.refresh(income)
    r=client.delete(f"/income/delete/{income.id}",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422

@pytest.mark.integration
def test_delete_income_not_found_404(client, database, login_get_token):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")

    r = client.delete(
        "/income/delete/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404
    assert r.get_json()["success"] is False


@pytest.mark.integration
def test_delete_income_other_user_404(
    client, database, login_get_token, build_income_payload
):
    token_a, _ = login_get_token(username="userA", password="Value@123")
    client.post(
        "/income/add",
        json=build_income_payload(source="A Income"),
        headers={"Authorization": f"Bearer {token_a}"},
    )
    income = Income.query.filter_by(source="A Income").first()

    token_b, _ = login_get_token(username="userB", password="Value@123")
    r = client.delete(
        f"/income/delete/{income.id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 404
    database.session.expire_all()
    assert Income.query.get(income.id) is not None
