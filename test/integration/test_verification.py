import time

import pytest

from dbms.db import db
from models.user import User


@pytest.mark.integration
def test_verify_otp_email_success(client, database, seed_otp, make_unverified_user, fake_redis):
    identifier = "original123@test.com"
    make_unverified_user(identifier)
    otp = seed_otp(identifier, otp="654321")
    r = client.post("/otp/verify-otp", json={"email": identifier, "otp": otp})
    assert r.status_code == 200
    assert not fake_redis.exists("otp:verification:original123@test.com")

@pytest.mark.integration
def test_verify_otp_mobile_success(client, database, seed_otp, make_unverified_user, fake_redis):
    mobile_no = "9222222222"
    identifier = "original123@test.com"
    make_unverified_user(identifier,mobile_no=mobile_no)
    otp = seed_otp(identifier, otp="654321")
    r = client.post("/otp/verify-otp", json={"mobile_no": mobile_no, "otp": otp})
    assert r.status_code == 200
    assert not fake_redis.exists("otp:verificaton:9222222222")

@pytest.mark.integration
def test_verify_otp_missing_body_returns_400(client):
    r=client.post("/otp/verify-otp")
    assert r.status_code==400 
    body=r.get_json()
    assert "request body" in body["message"].lower()   

@pytest.mark.integration
@pytest.mark.parametrize(
    "bad_email",["abc",
    "@test.com",
    "user@",
    "a b@c.com",
]
)
def  test_verify_otp_invalid_email_format_returns_400(make_unverified_user,seed_otp,client,database,bad_email):
    identifier=bad_email
    make_unverified_user(identifier)
    otp=seed_otp(identifier,otp="654321")
    r=client.post("/otp/verify-otp",json={"email":identifier,"otp":otp})
    assert r.status_code==400


@pytest.mark.integration
def test_both_fields_missing_returns_400 (client):
    
    r=client.post("/otp/verify-otp",json={"otp":"123456"})
    assert r.status_code==400
    body=r.get_json()
    assert "email or mobile number is required" in body["message"].lower()


@pytest.mark.integration
def test_verify_otp_user_not_found_email_returns_400 (client):
    email="ghost@test.com"
    r=client.post("/otp/verify-otp",json={"email":email,"otp":"123456"})
    assert r.status_code==400
    body=r.get_json()
    assert "user not found" in body["message"].lower()

@pytest.mark.integration
def test_verify_otp_expired_returns_400(seed_otp,client,fake_redis,make_unverified_user):
    email="original123@test.com"
    make_unverified_user(email)
    otp=seed_otp(email,otp="654321",ttl=1)
    time.sleep(2)
    r = client.post("/otp/verify-otp", json={
        "email": email,
        "otp": "123456",
    })
    assert r.status_code == 400
    body = r.get_json()
    assert "expired" in body["message"].lower()


@pytest.mark.integration
def test_verify_otp_wrong_otp_returns_400 (client,make_unverified_user,seed_otp):
    email="alice@test.com"
    make_unverified_user(email)
    otp=seed_otp(email,otp="123456")
    r = client.post("/otp/verify-otp", json={
        "email": email,
        "otp": "456123",
    })
    assert r.status_code == 400
    body = r.get_json()
    assert "user not found" in body["message"].lower()


@pytest.mark.integration
def test_verify_otp_reuse_after_success_returns_400(
    client, make_unverified_user, seed_otp, fake_redis
):
    email = "original123@test.com"
    make_unverified_user(email)
    otp = seed_otp(email, otp="654321")
    r = client.post("/otp/verify-otp", json={"email": email, "otp": otp})
    assert r.status_code == 200
    user = User.query.filter_by(email=email).first()
    assert user.is_verified is True
    assert not fake_redis.exists(f"otp:verification:{email}")
    user.is_verified = False
    db.session.commit()
    r1 = client.post("/otp/verify-otp", json={"email": email, "otp": otp})
    assert r1.status_code == 400
    body = r1.get_json()
    assert "expired" in body["message"].lower()