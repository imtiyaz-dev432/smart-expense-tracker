import pytest

from models.borrow import Borrow


@pytest.mark.integration
def test_borrow_with_success(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    body=r.get_json()
    assert body["success"] is True
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    assert borrow.amount==5000


@pytest.mark.integration
@pytest.mark.parametrize("missing",["amount","person_name","borrow_type"])
def test_borrow_with_success_missing_fields(login_get_token,client,missing,database,make_valid_borrow_payload):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    payload=make_valid_borrow_payload()
    payload.pop(missing)
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert body["success"] is False


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100, "%%$$", "abc","#@pok"])
def test_with_bad_amount(login_get_token,bad_amount,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    payload=make_valid_borrow_payload(amount=bad_amount)
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400




@pytest.mark.integration
def test_borrow_without_auth(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload)
    assert r.status_code==401

@pytest.mark.integration
def test_borrow_with_fake_token(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422
    


@pytest.mark.integration
def test_borrow_without_body(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_borrow_with_get_success(database,client,login_get_token,make_valid_borrow_payload):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    r=client.get("/borrow/get",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert r.get_json()["borrow"]==[]


@pytest.mark.integration
def test_get_borrow_returns_all_user_incomes(
    client, database, login_get_token, make_valid_borrow_payload
):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/borrow/add", json=make_valid_borrow_payload(), headers=headers)
    client.post("/borrow/add", json=make_valid_borrow_payload(amount=8000), headers=headers)
    r = client.get("/borrow/get", headers=headers)
    assert r.status_code==200


@pytest.mark.integration
def test_own_borrow_only(login_get_token,make_valid_borrow_payload,client,database):
    token, _ = login_get_token(username="Poki@!22", password="Valid@!234")
    token1, _ = login_get_token(username="Lopp@123", password="Pokemon@!234")
    client.post("/borrow/add",json=make_valid_borrow_payload(),headers={"Authorization":f"Bearer {token}"})
    client.post("/borrow/add",json=make_valid_borrow_payload(person_name="Rahul"),headers={"Authorization":f"Bearer {token}"})
    client.post("/borrow/add",json=make_valid_borrow_payload(borrow_type="borrowed",person_name="Alisha"),headers={"Authorization":f"Bearer {token1}"})
    r=client.get("/borrow/get",headers={"Authorization":f"Bearer {token}"})
    body=r.get_json()
    assert len((body)["borrow"])==2

  

@pytest.mark.integration
def test_get_borrow_with_no_token(database,client,login_get_token,make_valid_borrow_payload):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    r=client.get("/borrow/get")
    assert r.status_code==401


@pytest.mark.integration
def test_borrow_with_fake_token(database,client,login_get_token,make_valid_borrow_payload):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    r=client.get("/borrow/get",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_update_with_success(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!23",password="Pokib@12234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"person_name":"Deepanshu","amount":8700})
    assert r.status_code==200 
    database.session.refresh(borrow)
    assert borrow.person_name=="Deepanshu"
    assert borrow.amount==8700

@pytest.mark.integration
def test_update_borrow_person_name(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"person_name":"Deepanshu"})
    assert r.status_code==200
    database.session.refresh(borrow)
    assert borrow.person_name=="Deepanshu"
    assert borrow.amount==5000


@pytest.mark.integration
def test_update_borrow_amount(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"amount":8700})
    assert r.status_code==200
    database.session.refresh(borrow)
    assert borrow.amount==8700
    assert borrow.person_name=="Rahul"


@pytest.mark.integration
def test_update_borrow_type(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"borrow_type":"borrowed"})
    assert r.status_code==200
    database.session.refresh(borrow)
    assert borrow.borrow_type=="borrowed"


@pytest.mark.integration
def test_update_borrow_note(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"note":"Updated note"})
    assert r.status_code==200
    database.session.refresh(borrow)
    assert borrow.note=="Updated note"


@pytest.mark.integration
def test_update_borrow_due_date(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"due_date":"2031-06-20"})
    assert r.status_code==200
    database.session.refresh(borrow)
    assert borrow.due_date.strftime("%Y-%m-%d")=="2031-06-20"


@pytest.mark.integration
@pytest.mark.parametrize("bad_amount",[-100,"abc","",None])
def test_update_borrow_invalid_amount(login_get_token,bad_amount,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"amount":bad_amount})
    assert r.status_code==400


@pytest.mark.integration
def test_update_borrow_invalid_type(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={"borrow_type":"garbage"})
    assert r.status_code==400


@pytest.mark.integration
def test_update_borrow_empty_body(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token}"},json={})
    assert r.status_code==400


@pytest.mark.integration
def test_update_borrow_not_found(login_get_token,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    r=client.patch("/borrow/update/99999",headers={"Authorization":f"Bearer {token}"},json={"person_name":"X"})
    assert r.status_code==404


@pytest.mark.integration
def test_update_borrow_other_user(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    token1,_=login_get_token(username="Other@123",password="Value@!234")
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":f"Bearer {token1}"},json={"person_name":"Hacked"})
    assert r.status_code==404


@pytest.mark.integration
def test_update_borrow_without_auth(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",json={"person_name":"X"})
    assert r.status_code==401


@pytest.mark.integration
def test_update_borrow_with_fake_token(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.patch(f"/borrow/update/{borrow.id}",headers={"Authorization":"Bearer fake.invalid.token"},json={"person_name":"X"})
    assert r.status_code==422


@pytest.mark.integration
def test_delete_borrow_success(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.delete(f"/borrow/delete/{borrow.id}",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body=r.get_json()
    assert body["success"] is True
    database.session.expire_all()
    assert Borrow.query.get(borrow.id) is None


@pytest.mark.integration
def test_delete_borrow_not_found(login_get_token,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    r=client.delete("/borrow/delete/99999",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==404
    body=r.get_json()
    assert body["success"] is False


@pytest.mark.integration
def test_delete_borrow_other_user(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    token1,_=login_get_token(username="Other@123",password="Value@!234")
    r=client.delete(f"/borrow/delete/{borrow.id}",headers={"Authorization":f"Bearer {token1}"})
    assert r.status_code==404
    database.session.expire_all()
    assert Borrow.query.get(borrow.id) is not None


@pytest.mark.integration
def test_delete_borrow_without_auth(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.delete(f"/borrow/delete/{borrow.id}")
    assert r.status_code==401


@pytest.mark.integration
def test_delete_borrow_with_fake_token(login_get_token,make_valid_borrow_payload,client,database):
    token,_=login_get_token(username="Poki@!22",password="Valid@!234")
    payload=make_valid_borrow_payload()
    r=client.post("/borrow/add",json=payload,headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==201
    borrow=Borrow.query.filter_by(person_name="Rahul").first()
    r=client.delete(f"/borrow/delete/{borrow.id}",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422