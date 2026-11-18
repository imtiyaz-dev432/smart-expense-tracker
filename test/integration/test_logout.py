import pytest


@pytest.mark.integration
def test_logout_success(client,fake_redis,login_get_token):

    token,jti=login_get_token(username="verified user",password="Valid@123")
    r=client.post("/auth/logout",headers={"Authorization": f"Bearer {token}",}
    )
    assert r.status_code == 200
    body = r.get_json()
    assert "logged out" in body["message"].lower()
    assert fake_redis.exists(f"blacklist:{jti}")


@pytest.mark.integration
def test_logout_without_token_returns_401(client):
    r=client.post("/auth/logout")
    assert r.status_code==401


@pytest.mark.integration
def test_logout_invalid_token_returns_422(client):
    r=client.post("/auth/logout",headers={
        "Authorization": "Bearer fake.invalid.token",})
    assert r.status_code==422

