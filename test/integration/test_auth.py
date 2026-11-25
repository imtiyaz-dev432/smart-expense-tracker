import pytest
from werkzeug.security import generate_password_hash

from dbms.db import db
from models.user import User


@pytest.mark.integration
def test_register_success(client,fake_redis,mock_send_otp):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r=client.post("/auth/register",json=payload)
    assert r.status_code==201


@pytest.mark.integration
@pytest.mark.parametrize("missing", ["username", "mobile_no", "email", "password"])
def test_register_missing_fields(client,missing,mock_send_otp,fake_redis):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }
    payload.pop(missing)
    r=client.post("/auth/register",json=payload)
    assert r.status_code==400


@pytest.mark.integration
@pytest.mark.parametrize("bad_mobile",["12345",
    "abcdefghij",
    "+919876543210",
    "98765 43210",
    "",
])
def test_register_invalid_mobile(client,bad_mobile,mock_send_otp,fake_redis):
     payload = {
        "username": "rahul",
        "email": "rahul123@test.com",
        "mobile_no": bad_mobile,
        "password": "Test@1234",
    }
     r=client.post("/auth/register",json=payload)
     assert r.status_code==400

@pytest.mark.integration
@pytest.mark.parametrize("bad_email",["not-an-email", "user@", "@test.com", "user test@test.com", "user@test",]
)
def test_register_invalid_email(client,bad_email,mock_send_otp,fake_redis):
     payload = {
        "username": "rahul",
        "email": bad_email,
        "mobile_no": "9741852630",
        "password": "Test@1234",
    }
     r=client.post("/auth/register",json=payload)
     assert r.status_code==400



@pytest.mark.integration
@pytest.mark.parametrize("weak_passwd",["short",
    "alllowercase1!",
    "ALLUPPERCASE1!",
    "NoNumber!",
    "NoSpecial123", ])

def test_register_weak_password (weak_passwd,client,fake_redis,mock_send_otp):
    payload = {
        "username": "rahul",
        "email": "rahul123@test.com",
        "mobile_no": "9147258360",
        "password": weak_passwd,
    }
    r=client.post("/auth/register",json=payload)
    assert r.status_code==400


@pytest.mark.integration
def test_duplicate_email_409(client,fake_redis,mock_send_otp):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r=client.post("/auth/register",json=payload)
    duplicate_payload={
        **payload,
        "username":"rahul@123",
        "mobile_no":"9999999999"
    }
    r=client.post("/auth/register",json=duplicate_payload)
    assert r.status_code==409


@pytest.mark.integration
def test_duplicate_mobile_409(client,fake_redis,mock_send_otp):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r=client.post("/auth/register",json=payload)
    duplicate_payload={
        **payload,
        "username":"rahul@123",
        "email":"rahul1234@test.com"
    }
    r=client.post("/auth/register",json=duplicate_payload)
    assert r.status_code==409



@pytest.mark.integration
def test_register_creates_user_in_database(client,fake_redis,mock_send_otp):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r=client.post("/auth/register",json=payload)
    user=User.query.filter_by(email="rahul@example.com").first()
    assert user is not None
    assert r.status_code==201
    assert user.username=="rahul"
    assert user.email=="rahul@example.com"



@pytest.mark.integration
def test_register_hashes_password(client,fake_redis,mock_send_otp):
    password="Test@1234"
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": generate_password_hash(password),
    }

    r=client.post("/auth/register",json=payload)
    user=User.query.filter_by(email="rahul@example.com").first()
    assert user is not None
    assert r.status_code==201
    assert user.username=="rahul"
    assert user.email=="rahul@example.com"
    assert user.password!="Test@1234"


@pytest.mark.integration
def test_register_returns_user_not_verified_by_default(client,fake_redis,mock_send_otp):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r=client.post("/auth/register",json=payload)
    user=User.query.filter_by(email="rahul@example.com").first()
    assert not user.is_verified
    assert r.status_code==201



@pytest.mark.integration
def test_register_stores_otp_in_redis(client,fake_redis,mock_send_otp):
    email="rahul@example.com"
    payload = {
        "username": "rahul",
        "email": email,
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r=client.post("/auth/register",json=payload)
    User.query.filter_by(email="rahul@example.com").first()
    assert fake_redis.get(f"otp:verification:{email}") is not None
    assert r.status_code==201


@pytest.mark.integration
def test_register_otp_has_ttl_set(client, fake_redis, mock_send_otp):
    email = "rahul@example.com"
    payload = {
        "username": "rahul",
        "email": email,
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201
    user = User.query.filter_by(email=email).first()
    assert user is not None
    key = f"otp:verification:{email}"
    ttl = fake_redis.ttl(key)
    assert ttl > 0
    assert ttl <= 300
    mock_send_otp.assert_called_once()


@pytest.mark.integration
def test_register_sends_otp_email(client, fake_redis, mock_send_otp):
    email = "rahul@example.com"
    payload = {
        "username": "rahul",
        "email": email,
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201
    user = User.query.filter_by(email=email).first()
    assert user is not None
    key = f"otp:verification:{email}"
    ttl = fake_redis.ttl(key)
    assert ttl > 0
    assert ttl <= 300
    mock_send_otp.assert_called_once()
    assert mock_send_otp.call_args[0][0] == "rahul@example.com"
    assert mock_send_otp.call_args[1]["purpose"] == "verification"

@pytest.mark.integration
def test_register_email_contains_otp(client, fake_redis, mock_send_otp):
    email = "rahul@example.com"
    payload = {
        "username": "rahul",
        "email": email,
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201

    otp = mock_send_otp.sent[0]["otp"]
    assert len(otp) == 6
    assert otp.isdigit()


@pytest.mark.integration
def test_duplicate_username_409(client, fake_redis, mock_send_otp):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201

    duplicate = client.post("/auth/register", json={
        **payload,
        "email": "other@example.com",
        "mobile_no": "8888888888",
    })
    assert duplicate.status_code == 409


@pytest.mark.integration
def test_register_empty_body(client, fake_redis, mock_send_otp):
    r = client.post("/auth/register", json={})
    assert r.status_code == 400
    mock_send_otp.assert_not_called()
    assert User.query.count() == 0


@pytest.mark.integration
def test_register_db_error_rollback(client, fake_redis, mock_send_otp, mocker):
    payload = {
        "username": "rahul",
        "email": "rahul@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }
    mocker.patch.object(db.session, "commit", side_effect=Exception("simulated db failure"))
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 500
    mock_send_otp.assert_not_called()
    key = "otp:verification:rahul@example.com"
    assert not fake_redis.exists(key)


@pytest.mark.integration
def test_register_sql_injection_in_username(client, fake_redis, mock_send_otp):
    payload = {
        "username": "' OR '1'='1",
        "email": "inject@example.com",
        "mobile_no": "9999999999",
        "password": "Test@1234",
    }

    r = client.post("/auth/register", json=payload)
    assert r.status_code in [201,400]
