from unittest.mock import MagicMock

import pytest
from fakeredis import FakeRedis
from flask_jwt_extended import decode_token
from werkzeug.security import generate_password_hash

from app import create_app
from dbms.db import db
from models.user import User
from utils.hashed import hash_otp


@pytest.fixture(scope='session')
def app():
    return create_app("testing")

@pytest.fixture
def database(app):
    with app.app_context():
        db.create_all()
        try:
            yield db
        finally:
            db.session.remove()
            db.drop_all()

@pytest.fixture
def client(app, database):
    return app.test_client()


@pytest.fixture
def fake_redis(monkeypatch):
    server = FakeRedis(decode_responses=True)

    monkeypatch.setattr("utils.extensions.redis_client", server)
    monkeypatch.setattr("routes.auth.redis_client", server)
    monkeypatch.setattr("routes.otp.redis_client", server)
    monkeypatch.setattr("routes.forgot.redis_client", server)
    monkeypatch.setattr("app.redis_client", server)

    return server


@pytest.fixture
def mock_send_otp(monkeypatch):
    sent = []
    mock = MagicMock(return_value=True)

    def fake_send(email, otp, purpose="verification"):
        sent.append({"email": email, "otp": otp, "purpose": purpose})
        return True
    mock.side_effect = fake_send
    monkeypatch.setattr("routes.auth.send_otp_mail", mock)
    monkeypatch.setattr("routes.otp.send_otp_mail", mock)
    monkeypatch.setattr("routes.forgot.send_otp_mail", mock)
    mock.sent = sent
    return mock


@pytest.fixture
def seed_otp(fake_redis):
    def _seed(identifier, otp="654321", ttl=300):
        fake_redis.set(
            f"otp:verification:{identifier}",
            str(hash_otp(otp)),
            ex=ttl
        )
        return otp
    return _seed

@pytest.fixture
def make_unverified_user(database):
    def make(username="Unverified user",email="original123@test.com",mobile_no="9222222222",password="Valid@123"):
      hash_password=generate_password_hash(password)
      user=User(
        username=username,
        email=email,
        mobile_no=mobile_no,
        password=hash_password,
        is_verified=False
    )
      database.session.add(user)
      database.session.commit()
      return user
    return make


@pytest.fixture
def make_verified_user(database):
    def make(username,email=None,mobile_no=None,password="Valid@123"):
        hash_password=generate_password_hash(password)
        user=User(
        username=username,
        email=email or f"{username}@test.com",
        mobile_no=mobile_no or f"9{abs(hash(username)) % 1000000000:09d}",
        password=hash_password,
        is_verified=True
        )
        db.session.add(user)
        db.session.commit()
        return user
    return make

@pytest.fixture
def login_get_token(make_verified_user,database,client):
    def _login(username=None, password="Valid@123"):
      make_verified_user(username=username,password=password)
      r=client.post("/auth/login",json={"username":username,"password":password})
      token=r.get_json()["token"]
      jti=decode_token(token)['jti']
      return token,jti
    return _login

@pytest.fixture
def seed_forgot_otp(fake_redis):
    def _seed(identifier, otp="654321", ttl=300):
        fake_redis.set(
            f"otp:reset:{identifier}",
            str(hash_otp(otp)),
            ex=ttl
        )
        return otp
    return _seed

@pytest.fixture
def make_valid_expense_payload():
    def _make(**kwargs):
      payload = {
        "title": "Lunch",
        "amount": 200,
        "category": "Food",
        "description": "Team lunch",
        **kwargs,}
      return payload
    return _make




@pytest.fixture
def build_income_payload():
    def _make(**kwargs):
     payload= {
        "source": "Salary",
        "amount": 5000,
        "description": "Monthly salary",
        **kwargs,
    }
     return payload
    return _make


@pytest.fixture
def make_valid_loan_payload():
    def _make(**kwargs):
        payload={
            "loan_name": "Home Loan",
        "total_amount": 500000,
        "monthly_emi": 5000,
        "due_date": "2030-01-01",
        **kwargs,}
        return payload
    return _make


@pytest.fixture
def make_valid_subscription_payload():
    def _make(**kwargs):
        payload={"name": "Netflix",
        "amount": 499,
        "billing_cycle": "monthly",
        "next_billing_date": "2030-01-15",
        "note": "Premium plan",
        **kwargs,}
        return payload
    return _make

@pytest.fixture
def make_valid_borrow_payload():
    def _make(**kwargs):
     payload= {
        "person_name": "Rahul",
        "amount": 5000,
        "borrow_type": "lent",
        "due_date": "2030-01-15",
        "note": "For bike repair",
        **kwargs,}
     return payload
    return _make

@pytest.fixture
def login_get_refresh_token(make_verified_user, database, client):
    def _login(username=None, password="Valid@123"):
        make_verified_user(username=username, password=password)   # ← user banao
        r = client.post("/auth/login", json={"username": username, "password": password})
        assert r.status_code == 200, r.get_json()                  # ← debug ke liye
        body = r.get_json()
        refresh = body.get("refresh_token") or body.get("token")   # ← dono keys try
        jti = decode_token(refresh)["jti"]
        return refresh, jti
    return _login
