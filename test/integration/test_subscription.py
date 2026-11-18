from datetime import UTC, datetime, timedelta

import pytest

from models.subscribe import Subscription


@pytest.mark.integration
def test_subscription_with_success(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    body=r.get_json()
    assert body["success"] is True
    subscribe=Subscription.query.filter_by(name="Netflix").first()
    assert subscribe.amount==499


@pytest.mark.integration
@pytest.mark.parametrize("missing",["name","amount","billing_cycle","next_billing_date"])
def test_subscription_with_missing_fields(login_get_token,missing,make_valid_subscription_payload,client):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    payload.pop(missing)
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==400

@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100,"pok908","po@#","%%$$", "abc"])
def test_subscription_with_bad_amount(bad_amount,client,make_valid_subscription_payload,login_get_token):
       token,_=login_get_token(username="Nancy2123",password="Validity@1234")
       payload=make_valid_subscription_payload(amount=bad_amount)
       r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
       assert r.status_code==400



@pytest.mark.integration
def test_subscription_without_auth(client,database,make_valid_subscription_payload):
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",json=payload)
    assert r.status_code==401

@pytest.mark.integration
def test_subscription_with_fake_token(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":"Bearer fake.invalid.token"},json=payload)
    assert r.status_code==422

def test_subscription_without_body(login_get_token,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400
    body=r.get_json()
    assert body["success"] is False



@pytest.mark.integration
def test_get_subscription_success(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    r=client.get("/subscription/get",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    body=r.get_json()
    assert body["success"] is True
    assert len(body["message"])==1


@pytest.mark.integration
def test_get_subscription_empty_list(login_get_token,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    r=client.get("/subscription/get",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert r.get_json()["message"]==[]


@pytest.mark.integration
def test_get_subscription_without_auth(client,database):
    r=client.get("/subscription/get")
    assert r.status_code==401


@pytest.mark.integration
def test_get_subscription_with_fake_token(client,database):
    r=client.get("/subscription/get",headers={"Authorization":"Bearer fake.invalid.token"})
    assert r.status_code==422


@pytest.mark.integration
def test_get_subscription_another_user(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    token1,_=login_get_token(username="Other@123",password="Value@!234")
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload(name="Netflix"))
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload(name="Spotify"))
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token1}"},json=make_valid_subscription_payload(name="Prime"))
    r=client.get("/subscription/get",headers={"Authorization":f"Bearer {token}"})
    assert len(r.get_json()["message"])==2
    r=client.get("/subscription/get",headers={"Authorization":f"Bearer {token1}"})
    assert len(r.get_json()["message"])==1



@pytest.mark.integration
def test_update_success_subsription(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    body=r.get_json()
    assert body["success"] is True
    subscribe=Subscription.query.filter_by(name="Netflix").first()
    r=client.patch(f"/subscription/update/{subscribe.id}",json={"name":"Amazon prime"},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert subscribe.name=="Amazon prime"

@pytest.mark.integration
def test_update_subscription_empty_name(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    sub=Subscription.query.first()
    r=client.patch(f"/subscription/update/{sub.id}",json={"name":""},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_update_subscription_invalid_cycle(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    sub=Subscription.query.first()
    r=client.patch(f"/subscription/update/{sub.id}",json={"billing_cycle":"daily"},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_update_subscription_past_date(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    sub=Subscription.query.first()
    r=client.patch(f"/subscription/update/{sub.id}",json={"next_billing_date":"2020-01-01"},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_update_subscription_invalid_date_format(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    sub=Subscription.query.first()
    r=client.patch(f"/subscription/update/{sub.id}",json={"next_billing_date":"01/01/2030"},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_update_subscription_long_note(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    sub=Subscription.query.first()
    r=client.patch(f"/subscription/update/{sub.id}",json={"note":"A"*151},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_update_subscription_empty_body(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    sub=Subscription.query.first()
    r=client.patch(f"/subscription/update/{sub.id}",json={},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400

@pytest.mark.integration
@pytest.mark.parametrize("bad_amount", [-100,"dfgh@#","$%#","rt4#",  "abc", ""])
def test_update_subscribe_with_bad_amount(login_get_token,bad_amount,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    body=r.get_json()
    assert body["success"] is True
    subscribe=Subscription.query.filter_by(name="Netflix").first()
    r=client.patch(f"/subscription/update/{subscribe.id}",json={"amount":bad_amount},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==400


@pytest.mark.integration
def test_subscribe_not_found(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    body=r.get_json()
    assert body["success"] is True
    r=client.patch("/subscription/update/8745",json={"smount":500,"name":"mx player"},headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==404

@pytest.mark.integration
def test_update_subscription_with_other_user(login_get_token,make_valid_subscription_payload,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    body=r.get_json()
    assert body["success"] is True
    subscribe=Subscription.query.filter_by(name="Netflix").first()
    token1,_=login_get_token(username="Immu@123",password="Validity@1234")
    r=client.patch(f"/subscription/update/{subscribe.id}",json={"name":"Amazon prime"},headers={"Authorization":f"Bearer {token1}"})
    assert r.status_code==404


@pytest.mark.integration
def test_delete_subscription_success(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    payload=make_valid_subscription_payload()
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    sub=Subscription.query.first()
    r=client.delete(f"/subscription/delete/{sub.id}",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    database.session.expire_all()
    assert Subscription.query.get(sub.id) is None


@pytest.mark.integration
def test_delete_subscription_not_found(login_get_token,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    r=client.delete("/subscription/delete/99999",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==404


@pytest.mark.integration
def test_delete_subscription_other_user(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    token1,_=login_get_token(username="Other@123",password="Value@!234")
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    assert r.status_code==201
    sub=Subscription.query.first()
    r=client.delete(f"/subscription/delete/{sub.id}",headers={"Authorization":f"Bearer {token1}"})
    assert r.status_code==404


@pytest.mark.integration
def test_delete_subscription_without_auth(client,database,login_get_token,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=make_valid_subscription_payload())
    assert r.status_code==201
    sub=Subscription.query.first()
    r=client.delete(f"/subscription/delete/{sub.id}")
    assert r.status_code==401

@pytest.mark.integration
def test_upcoming_subscription_empty(login_get_token,client,database):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    r=client.get("/subscription/upcoming",headers={"Authorization":f"Bearer {token}"})
    assert r.status_code==200
    assert r.get_json()["upcoming_subscriptions"]==[]


@pytest.mark.integration
def test_upcoming_subscription_within_7_days(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    within_7=datetime.now(UTC)+timedelta(days=3)
    payload=make_valid_subscription_payload(next_billing_date=within_7.strftime("%Y-%m-%d"))
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    r=client.get("/subscription/upcoming",headers={"Authorization":f"Bearer {token}"})
    assert len(r.get_json()["upcoming_subscriptions"])==1


@pytest.mark.integration
def test_upcoming_subscription_excludes_far_future(login_get_token,client,database,make_valid_subscription_payload):
    token,_=login_get_token(username="Nancy2123",password="Validity@1234")
    far_future=datetime.now(UTC)+timedelta(days=30)
    payload=make_valid_subscription_payload(next_billing_date=far_future.strftime("%Y-%m-%d"))
    r=client.post("/subscription/add",headers={"Authorization":f"Bearer {token}"},json=payload)
    assert r.status_code==201
    r=client.get("/subscription/upcoming",headers={"Authorization":f"Bearer {token}"})
    assert r.get_json()["upcoming_subscriptions"]==[]
