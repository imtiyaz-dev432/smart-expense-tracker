import pytest


@pytest.mark.integration
def test_ai_no_data_returns_no_data(login_get_token,client,database):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    r=client.get("/ai/suggestion",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body=r.get_json()
    assert body["summary"]["financial_health"]=="No Data"
    assert body["summary"]["expense_ratio"]=="N/A"
    assert len(body["suggestions"])==1
    assert body["suggestions"][0]["type"]=="no_data"


@pytest.mark.integration
def test_ai_overspending_alert(login_get_token,client,database,build_income_payload,make_valid_expense_payload):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=5000),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(amount=8000),headers=headers)
    r=client.get("/ai/suggestion",headers=headers)
    assert r.status_code==200
    types=[s["type"] for s in r.get_json()["suggestions"]]
    assert "overspending_alert" in types
    assert r.get_json()["summary"]["financial_health"]=="Risky"


@pytest.mark.integration
def test_ai_low_balance_warning(login_get_token,client,database,build_income_payload,make_valid_expense_payload):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=10000),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(amount=9500),headers=headers)
    r=client.get("/ai/suggestion",headers=headers)
    types=[s["type"] for s in r.get_json()["suggestions"]]
    assert "low_balance_warning" in types


@pytest.mark.integration
def test_ai_good_saving_suggestion(login_get_token,client,database,build_income_payload,make_valid_expense_payload):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=10000),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(amount=3000),headers=headers)
    r=client.get("/ai/suggestion",headers=headers)
    types=[s["type"] for s in r.get_json()["suggestions"]]
    assert "saving_suggestion" in types
    assert r.get_json()["summary"]["financial_health"]=="Good"


@pytest.mark.integration
def test_ai_highest_category(login_get_token,client,database,build_income_payload,make_valid_expense_payload):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=20000),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(amount=5000,category="Food"),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(amount=1000,category="Travel",title="Bus"),headers=headers)
    r=client.get("/ai/suggestion",headers=headers)
    types=[s["type"] for s in r.get_json()["suggestions"]]
    assert "highest_spending_category" in types


@pytest.mark.integration
def test_ai_pending_lent_reminder(login_get_token,client,database,build_income_payload,make_valid_borrow_payload):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=10000),headers=headers)
    client.post("/borrow/add",json=make_valid_borrow_payload(amount=2000,borrow_type="lent"),headers=headers)
    r=client.get("/ai/suggestion",headers=headers)
    types=[s["type"] for s in r.get_json()["suggestions"]]
    assert "pending_lent_reminder" in types


@pytest.mark.integration
def test_ai_pending_borrow_reminder(login_get_token,client,database,build_income_payload,make_valid_borrow_payload):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=10000),headers=headers)
    client.post("/borrow/add",json=make_valid_borrow_payload(amount=3000,borrow_type="borrowed"),headers=headers)
    r=client.get("/ai/suggestion",headers=headers)
    types=[s["type"] for s in r.get_json()["suggestions"]]
    assert "pending_borrowed_reminder" in types


@pytest.mark.integration
def test_ai_active_loan_warning(login_get_token,client,database,build_income_payload,make_valid_loan_payload):
    token,_=login_get_token(username="AI@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=50000),headers=headers)
    client.post("/loan/add",json=make_valid_loan_payload(total_amount=100000,monthly_emi=5000),headers=headers)
    r=client.get("/ai/suggestion",headers=headers)
    types=[s["type"] for s in r.get_json()["suggestions"]]
    assert "active_loan_warning" in types


@pytest.mark.integration
def test_ai_without_auth(client,database):
    r=client.get("/ai/suggestion")
    assert r.status_code==401


@pytest.mark.integration
def test_ai_with_fake_token(client,database):
    r=client.get("/ai/suggestion",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_ai_isolated_per_user(login_get_token,client,database,build_income_payload,make_valid_expense_payload):
    token_a,_=login_get_token(username="AIA@123",password="Valid@!234")
    token_b,_=login_get_token(username="AIB@123",password="Valid@!234")
    client.post("/income/add",json=build_income_payload(amount=10000),headers={"Authorization":f"Bearer {token_a}"})
    client.post("/expense/add",json=make_valid_expense_payload(amount=2000),headers={"Authorization":f"Bearer {token_a}"})
    r=client.get("/ai/suggestion",headers={"Authorization":f"Bearer {token_b}"})
    assert r.get_json()["summary"]["financial_health"]=="No Data"
