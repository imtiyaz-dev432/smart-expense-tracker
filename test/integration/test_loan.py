import pytest

from models.loan import Loan


@pytest.mark.integration
def test_add_loan_success(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    assert loan.total_amount==500000
    assert loan.loan_name=="Home Loan"
    assert loan.remaining_amount==500000


@pytest.mark.integration
def test_add_loan_default_status_active(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(status="Active")
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201


@pytest.mark.integration
@pytest.mark.parametrize("missing",["loan_name","total_amount","monthly_emi","due_date"])
def test_add_loan_missing_fields(login_get_token,missing,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(status="Active")
    payload.pop(missing)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount",[-100, "%%$$", "abc"])
def test_add_loan_invalid_amount(login_get_token,bad_amount,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=bad_amount)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_add_loan_emi_greater_than_total(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=5000,monthly_emi=6000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_add_loan_emi_equal_to_total(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=5000,monthly_emi=5000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
@pytest.mark.parametrize("bad_emi",[-100,0,"abc"])
def test_add_loan_invalid_emi(login_get_token,bad_emi,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(monthly_emi=bad_emi)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_add_loan_past_due_date(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(due_date="2020-01-01")
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
@pytest.mark.parametrize("bad_date",["01/01/2030","2030-13-45","not-a-date",""])
def test_add_loan_invalid_date_format(login_get_token,bad_date,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(due_date=bad_date)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_add_loan_long_name(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="A"*101)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_add_loan_without_auth(client,make_valid_loan_payload):
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload)
    assert r.status_code==401


@pytest.mark.integration
def test_add_loan_with_fake_token(client,make_valid_loan_payload):
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_add_loan_empty_body(login_get_token,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    r=client.post("/loan/add",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400



@pytest.mark.integration
def test_get_loan_success(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    r=client.get("/loan/get",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200

@pytest.mark.integration
def test_get_loan_without_auth(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    r=client.get("/loan/get")
    assert r.status_code==401


@pytest.mark.integration
def test_get_loan_with_fake_token(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    r=client.get("/loan/get",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422



@pytest.mark.integration
def test_get_loan_another_user(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    token1,_=login_get_token(username="Iffu@123",password="Value@!234")
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    r=client.post("/loan/add",json=make_valid_loan_payload(loan_name="Bike Loan ",total_amount=8700),headers={"Authorization":f"Bearer {token}"})
    r=client.get("/loan/get",headers={"Authorization":f"Bearer {token}"})
    body=r.get_json()["loans"]
    assert len(body)==2
    r=client.post("/loan/add",json=make_valid_loan_payload(loan_name="Edu Loan",amount=80000),headers={"Authorization":f"Bearer {token1}"})
    assert r.status_code==201
    r=client.get("/loan/get",headers={"Authorization":f"Bearer {token1}"})
    body=r.get_json()["loans"]
    assert len(body)==1

@pytest.mark.integration
def test_get_loan_empty_list(login_get_token,database,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    r=client.get("/loan/get",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert r.get_json()["loans"]==[]


@pytest.mark.integration
def test_get_loan_amount_is_float(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    r=client.get("/loan/get",headers={"Authorization":f"Bearer {token}"})
    loan=r.get_json()["loans"][0]
    assert isinstance(loan["total_amount"],float)
    assert isinstance(loan["remaining_amount"],float)
    assert isinstance(loan["monthly_emi"],float)


@pytest.mark.integration
def test_get_loan_date_is_isoformat(login_get_token,database,make_valid_loan_payload,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    r=client.get("/loan/get",headers={"Authorization":f"Bearer {token}"})
    body=r.get_json()
    loan=body["loans"][0]
    assert isinstance(loan["due_date"],str)
    assert "T" in loan["due_date"]

@pytest.mark.integration
def test_loan_update_success_with_actual_changes_in_db(login_get_token,make_valid_loan_payload,database,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    r=client.patch(f"/loan/update/{loan.id}",json={"loan_name":"Home Loan","total_amount":100000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    database.session.refresh(loan)
    assert loan.loan_name=="Home Loan"
    assert loan.total_amount==100000

@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100,  "abc", ""])
def test_with_bad_amount(login_get_token,make_valid_loan_payload,bad_amount,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    total_amount=bad_amount
    r=client.patch(f"/loan/update/{loan.id}",json={"loan_name":"Home Loan","total_amount":total_amount},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert body["success"]  is False


@pytest.mark.integration
def test_update_loan_past_due_date(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    r=client.patch(f"/loan/update/{loan.id}",json={"due_date":"2020-01-01"},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400

@pytest.mark.integration
def test_update_loan_emi_greater_than_total(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload()
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    r=client.patch(f"/loan/update/{loan.id}",json={"total_amount":5000,"monthly_emi":6000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400

@pytest.mark.integration
def test_with_empty_body(login_get_token,make_valid_loan_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    r=client.patch(f"/loan/update/{loan.id}",json={},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert body["success"]  is False


@pytest.mark.integration
def test_update_loan_not_found(login_get_token,make_valid_loan_payload,database,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    r=client.patch("/loan/update/7895",json={"loan_name":"Home Loan","total_amount":10000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==404
    body=r.get_json()
    assert body["success"]  is False


@pytest.mark.integration
def test_update_loan_other_user_404(client, database, login_get_token, make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    token1,_=login_get_token(username="Immu@123",password="Pokemon@123")
    r=client.patch(f"/loan/update/{loan.id}",json={"loan_name":"Home Loan","total_amount":10000},headers={"Authorization":f"Bearer {token1}"})
    assert r.status_code==404



@pytest.mark.integration
def test_update_loan_without_token(client, database, make_valid_loan_payload,login_get_token):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    r=client.patch(f"/loan/update/{loan.id}",json={"loan_name":"Home Loan","total_amount":10000})
    assert r.status_code==401


@pytest.mark.integration
def test_update_loan_with_fake_token(login_get_token,make_valid_loan_payload,database,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    r=client.patch(f"/loan/update/{loan.id}",json={"loan_name":"Home Loan","total_amount":100000},headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_with_delete_success(login_get_token,database,client,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    r=client.delete(f"/loan/delete/{loan.id}",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200


@pytest.mark.integration
def test_delete_loan_without_token(client, database, make_valid_loan_payload,login_get_token):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    r=client.delete(f"/loan/delete/{loan.id}")
    assert r.status_code==401

@pytest.mark.integration
def test_delete_loan_with_fake_token(login_get_token,make_valid_loan_payload,database,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    r=client.delete(f"/loan/delete/{loan.id}",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422

@pytest.mark.integration
def test_delete_loan_not_found(login_get_token,make_valid_loan_payload,database,client):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    r=client.delete("/loan/delete/7895",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==404
    body=r.get_json()
    assert body["success"]  is False



@pytest.mark.integration
def test_delete_loan_other_user_404(client, database, login_get_token, make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    token1,_=login_get_token(username="Immu@123",password="Pokemon@123")
    r=client.delete(f"/loan/delete/{loan.id}",headers={"Authorization":f"Bearer {token1}"})
    assert r.status_code==404



@pytest.mark.integration
def test_repayment_with_success(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":5000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert loan.remaining_amount==5000


@pytest.mark.integration
def test_repayment_without_auth(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":5000})
    assert r.status_code==401


@pytest.mark.integration
def test_repayment_with_fake_token_auth(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":5000},headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_repayment_with_loan_not_found(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post("/loan/repayment/54887",json={"paid_amount":5000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==404
    body=r.get_json()
    assert "loan not found" in body["message"].lower()


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount",[-123,"pok","kop%%","8ujj",""])
def test_repayment_with_bad_paid_amount(login_get_token,bad_amount,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":bad_amount},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_repay_loan_other_user_404(client, database, login_get_token, make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(loan_name="Education Loan",total_amount=98000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Education Loan").first()
    database.session.refresh(loan)
    token1,_=login_get_token(username="Immu@123",password="Pokemon@123")
    r=client.post(f"/loan/repayment/{loan.id}",headers={"Authorization":f"Bearer {token1}"},json={"paid_amount":8500})
    assert r.status_code==404



@pytest.mark.integration
def test_repayment_with_complete(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":10000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert loan.remaining_amount==0
    assert loan.status=="closed"



@pytest.mark.integration
def test_repayment_more_than_remain(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":11000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert "payment cannot exceed remaining amount" in body["message"].lower()



@pytest.mark.integration
def test_repayment_already_completed(login_get_token,client,database,make_valid_loan_payload):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_loan_payload(total_amount=10000)
    r=client.post("/loan/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    loan=Loan.query.filter_by(loan_name="Home Loan").first()
    database.session.refresh(loan)
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":10000},headers={"Authorization":f"Bearer {token}"})
    r=client.post(f"/loan/repayment/{loan.id}",json={"paid_amount":10000},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert "this loan is already completed" in body["message"].lower()


