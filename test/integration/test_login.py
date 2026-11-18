import pytest
from werkzeug.security import generate_password_hash

from models.user import User


@pytest.mark.integration
def test_login_with_success_200(make_verified_user,client):
    username="verified user"
    password="Valid@123"
    make_verified_user(username=username,password=password)
    r=client.post("/auth/login",json={"username":username,"password":password})
    assert r.status_code==200


@pytest.mark.integration
def test_login_body_missing(client,make_verified_user):
    username="verified user"
    password="Valid@123"
    make_verified_user(username=username,password=password)
    r = client.post("/auth/login")
    assert r.status_code == 400
    
    
@pytest.mark.integration
def test_login_user_not_found_returns_401(client):
    username="verified user"
    password="Valid@123"
    r=client.post("/auth/login",json={"username":username,"password":password})
    assert r.status_code==401


@pytest.mark.integration
@pytest.mark.parametrize("wrong_passwd",["Wrong@123",
    "valid@123",
    "VALID@123",
    "Valid@1234",
    "Valid@12",
    "xyz",
])
def test_login_wrong_password_returns_401(client,wrong_passwd,make_verified_user):
    username="Valid@123"
    password=wrong_passwd
    make_verified_user(username=username,password="Valid@123")
    r=client.post("/auth/login",json={"username":username,"password":password})
    assert r.status_code==401
    body=r.get_json()
    assert "access_token" not in body


@pytest.mark.integration
def test_unverified_user_403(client,database):
    user=User(
        username="Immu",
        email="immu@gmail.com",
        mobile_no="6543219870",
        password=generate_password_hash("Hello@123"),
        is_verified=False
    )
    database.session.add(user)
    database.session.commit()
    r=client.post("/auth/login",json={"username":"Immu","password":"Hello@123"})
    assert r.status_code==403
    body=r.get_json()
    assert "not verified" not in body

