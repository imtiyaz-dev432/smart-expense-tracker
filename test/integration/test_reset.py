import pytest
from werkzeug.security import check_password_hash

from models.user import User


@pytest.mark.integration
def test_reset_password_with_email_success(database,client,make_verified_user,seed_forgot_otp,fake_redis):
         email="original123@test.com"
         otp=seed_forgot_otp(email,otp="654321")
         make_verified_user(username="Immu",email=email)
         new_password="Ghost@123"
         r=client.post("/reset-password",json={"email":email,"otp":otp,"new_password":new_password})
         assert r.status_code==200
         r.get_json()
         user=User.query.filter_by(email=email).first()
         database.session.refresh(user)
         assert check_password_hash(user.password,new_password)
         assert not fake_redis.exists("otp:reset:original123@test.com")

@pytest.mark.integration
def test_reset_password_with_no_body(client):
    r=client.post("/reset-password")
    assert r.status_code==400

@pytest.mark.integration
def test_reset_password_with_missing_email(client):
    new_password="Ghost@123"
    r=client.post("/reset-password",json={"new_password":new_password,"otp":"654321"})
    assert r.status_code==400


@pytest.mark.integration
def test_reset_password_with_both_fields(client):
    email="alice@test.com"
    mobile_no="9876543210"
    new_password="Ghost@123"
    r=client.post("/reset-password",json={"email":email,"otp":"654321","mobile_no":mobile_no,"new_password":new_password})
    assert r.status_code==400


@pytest.mark.integration
def test_with_missing_otp(client,make_verified_user):
   email="original123@test.com"
   make_verified_user(email)
   r=client.post("/reset-password",json={"email":email,"new_password":"Valid@123"})
   assert r.status_code==400

@pytest.mark.integration
def test_with_missing_password(client):
    email="alice@test.com"
    otp="654321"
    r=client.post("/reset-password",json={"email":email,"otp":otp})
    assert r.status_code==400


@pytest.mark.integration
@pytest.mark.parametrize(
    "bad_email",["abc",
    "@test.com",
    "user@",
    "a b@c.com",
]
)
def test_with_invalid_email_format(client,bad_email):
    email=bad_email
    new_password="Ghost@123"
    otp="654321"
    r=client.post("/reset-password",json={"email":email,"otp":otp,"new_password":new_password})
    assert r.status_code==400


@pytest.mark.integration
@pytest.mark.parametrize("bad_mobile", [
    "12345",
    "abcdefghij",
    "+919876543210",
    "98765 43210",

])
def test_with_invalid_mobile_no_format(client,bad_mobile):
    mobile_no=bad_mobile
    new_password="Ghost@123"
    otp="654321"
    r=client.post("/reset-password",json={"mobile_no":mobile_no,"otp":otp,"new_password":new_password})
    assert r.status_code==400


@pytest.mark.integration
@pytest.mark.parametrize("wrong_passwd",[
    "VALID@123",

    "valid@123",
    "Valid0987",
    "Valid@#$",
    "123456",

    "xyz",
])
def test_with_invalid_password_format(client,wrong_passwd):
    email="alice@test.com"
    new_password=wrong_passwd
    otp="654321"
    r=client.post("/reset-password",json={"email":email,"otp":otp,"new_password":new_password})
    assert r.status_code==400


@pytest.mark.integration
def test_user_not_fond_with_email(client):
    email="ghost@test.com"
    new_password="Ghost@123"
    otp="654321"
    r=client.post("/reset-password",json={"email":email,"new_password":new_password,"otp":otp})
    assert r.status_code==400


@pytest.mark.integration
def test_user_not_fond_with_mobile_no(client):
    mobile_no="9876541230"
    new_password="Ghost@123"
    otp="654321"
    r=client.post("/reset-password",json={"mobile_no":mobile_no,"new_password":new_password,"otp":otp})
    assert r.status_code==400


@pytest.mark.integration
def test_user_with_expired_otp(client,make_verified_user,fake_redis):
    mobile_no="9876541230"
    make_verified_user(username="Immu",mobile_no=mobile_no)
    new_password="Ghost@123"
    otp="654321"
    r=client.post("/reset-password",json={"mobile_no":mobile_no,"new_password":new_password,"otp":otp})
    assert r.status_code==400

@pytest.mark.integration
def test_user_with_wrong_otp(client,make_verified_user,seed_forgot_otp):
    mobile_no="9876541230"
    seed_forgot_otp(mobile_no,otp="654321")
    make_verified_user(username="Immu",mobile_no=mobile_no)
    new_password="Ghost@123"
    r=client.post("/reset-password",json={"mobile_no":mobile_no,"new_password":new_password,"otp":"123456"})
    assert r.status_code==400
    body=r.get_json()
    assert "invalid" in body["message"].lower()

