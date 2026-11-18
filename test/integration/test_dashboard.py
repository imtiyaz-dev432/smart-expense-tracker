import pytest


@pytest.mark.integration
def test_dashboard_empty_state(login_get_token,client,database):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    r=client.get("/dashboard",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body=r.get_json()
    assert body["total_income"]==0.0
    assert body["total_expense"]==0.0
    assert body["balance"]==0.0


@pytest.mark.integration
def test_dashboard_with_expense(login_get_token,client,database,make_valid_expense_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    client.post("/expense/add",json=make_valid_expense_payload(amount=200),headers={"Authorization":f"Bearer {token}"})
    client.post("/expense/add",json=make_valid_expense_payload(amount=300,title="Dinner"),headers={"Authorization":f"Bearer {token}"})
    r=client.get("/dashboard",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body=r.get_json()
    assert body["total_expense"]==500.0


@pytest.mark.integration
def test_dashboard_with_income(login_get_token,client,database,build_income_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    client.post("/income/add",json=build_income_payload(amount=5000),headers={"Authorization":f"Bearer {token}"})
    r=client.get("/dashboard",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body=r.get_json()
    assert body["total_income"]==5000.0


@pytest.mark.integration
def test_dashboard_balance_calculation(login_get_token,client,database,build_income_payload,make_valid_expense_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=10000),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(amount=3000),headers=headers)
    r=client.get("/dashboard",headers=headers)
    assert r.status_code==200
    body=r.get_json()
    assert body["total_income"]==10000.0
    assert body["total_expense"]==3000.0
    assert body["balance"]==7000.0


@pytest.mark.integration
def test_dashboard_loan_counts(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/loan/add",json=make_valid_loan_payload(total_amount=100000,monthly_emi=5000),headers=headers)
    r=client.get("/dashboard",headers=headers)
    assert r.status_code==200
    body=r.get_json()
    assert body["active_loan_count"]==1
    assert body["total_loan_remaining"]==100000.0


@pytest.mark.integration
def test_dashboard_borrow_counts(login_get_token,client,database,make_valid_borrow_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/borrow/add",json=make_valid_borrow_payload(amount=5000,borrow_type="lent"),headers=headers)
    client.post("/borrow/add",json=make_valid_borrow_payload(amount=3000,borrow_type="borrowed",person_name="Amit"),headers=headers)
    r=client.get("/dashboard",headers=headers)
    assert r.status_code==200
    body=r.get_json()
    assert body["pending_lent_total"]==5000.0
    assert body["pending_borrow_total"]==3000.0


@pytest.mark.integration
def test_dashboard_subscription_counts(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/subscription/add",json=make_valid_subscription_payload(amount=499,billing_cycle="monthly"),headers=headers)
    client.post("/subscription/add",json=make_valid_subscription_payload(name="Prime",amount=1499,billing_cycle="yearly"),headers=headers)
    r=client.get("/dashboard",headers=headers)
    assert r.status_code==200
    body=r.get_json()
    assert body["active_subscription_count"]==2
    assert body["monthly_subscription_total"]>499


@pytest.mark.integration
def test_dashboard_without_auth(client,database):
    r=client.get("/dashboard")
    assert r.status_code==401


@pytest.mark.integration
def test_dashboard_with_fake_token(client,database):
    r=client.get("/dashboard",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_dashboard_isolated_per_user(login_get_token,client,database,make_valid_expense_payload):
    token_a,_=login_get_token(username="DashA@123",password="Valid@!234")
    token_b,_=login_get_token(username="DashB@123",password="Valid@!234")
    client.post("/expense/add",json=make_valid_expense_payload(amount=200),headers={"Authorization":f"Bearer {token_a}"})
    client.post("/expense/add",json=make_valid_expense_payload(amount=500,title="B"),headers={"Authorization":f"Bearer {token_b}"})
    r=client.get("/dashboard",headers={"Authorization":f"Bearer {token_a}"})
    assert r.get_json()["total_expense"]==200.0
    r=client.get("/dashboard",headers={"Authorization":f"Bearer {token_b}"})
    assert r.get_json()["total_expense"]==500.0


@pytest.mark.integration
def test_category_wise_expense_empty(login_get_token,client,database):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    r=client.get("/dashboard/category-wise-expense",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert r.get_json()["category_wise_expense"]=={}


@pytest.mark.integration
def test_category_wise_expense_with_data(login_get_token,client,database,make_valid_expense_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/expense/add",json=make_valid_expense_payload(category="Food",amount=200),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(category="Food",amount=300,title="Dinner"),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(category="Travel",amount=500,title="Bus"),headers=headers)
    r=client.get("/dashboard/category-wise-expense",headers=headers)
    assert r.status_code==200
    body=r.get_json()["category_wise_expense"]
    assert body["Food"]==500.0
    assert body["Travel"]==500.0


@pytest.mark.integration
def test_category_wise_expense_without_auth(client,database):
    r=client.get("/dashboard/category-wise-expense")
    assert r.status_code==401


@pytest.mark.integration
def test_monthly_report_empty(login_get_token,client,database):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    r=client.get("/dashboard/monthly-report",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body=r.get_json()
    assert body["monthly_income"]==0.0
    assert body["monthly_expense"]==0.0
    assert body["monthly_balance"]==0.0


@pytest.mark.integration
def test_monthly_report_with_data(login_get_token,client,database,build_income_payload,make_valid_expense_payload):
    token,_=login_get_token(username="Dash@123",password="Valid@!234")
    headers={"Authorization":f"Bearer {token}"}
    client.post("/income/add",json=build_income_payload(amount=5000),headers=headers)
    client.post("/expense/add",json=make_valid_expense_payload(amount=1500),headers=headers)
    r=client.get("/dashboard/monthly-report",headers=headers)
    assert r.status_code==200
    body=r.get_json()
    assert body["monthly_income"]==5000.0
    assert body["monthly_expense"]==1500.0
    assert body["monthly_balance"]==3500.0
    assert "month" in body
    assert "year" in body


@pytest.mark.integration
def test_monthly_report_without_auth(client,database):
    r=client.get("/dashboard/monthly-report")
    assert r.status_code==401
