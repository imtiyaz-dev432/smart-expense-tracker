import pytest


@pytest.mark.integration
def test_forgot_with_email(make_verified_user,client):
    email="original123@test.com"
    make_verified_user(username="karan",email=email)
    r=client.post("/forgot-password",json={"email":email})
    assert r.status_code==200
    body=r.get_json()
    assert body["success"] is True


@pytest.mark.integration
def test_forgot_with_mobile_no(make_verified_user,client):
    mobile_no="9222222222"
    make_verified_user(username="karan",mobile_no=mobile_no)
    r=client.post("/forgot-password",json={"mobile_no":mobile_no})
    assert r.status_code==200
    body=r.get_json()
    assert body["success"] is True

@pytest.mark.integration
def test_forgot_without_body(client):
    r = client.post("/forgot-password")
    assert r.status_code == 400


@pytest.mark.integration
def test_forgot_both_fields_missing_returns_400(client):
    r=client.post("/forgot-password",json={"otp":"852741"})
    assert r.status_code==400


@pytest.mark.integration
def test_forgot_both_fields_present_returns_400(client):
    email="original123@test.com"
    mobile_no="9222222222"
    r=client.post("/forgot-password",json={"email":email,"mobile_no":mobile_no})
    assert r.status_code==400

@pytest.mark.integration
@pytest.mark.parametrize("bad_email", [
    "abc",
    "@test.com",
    "user@",
    "a b@c.com",
])
def test_forgot_invalid_email_format_returns_400(client, bad_email):
    email=bad_email
    r=client.post("/forgot-password",json={"email":email})
    assert r.status_code==400
    body=r.get_json()
    assert body["success"] is False



@pytest.mark.integration
@pytest.mark.parametrize("bad_mobile", [
    "12345",
    "abcdefghij",
    "+919876543210",
    "98765 43210",
])
def test_forgot_invalid_mobile_format_returns_400(client, bad_mobile):
    r = client.post("/forgot-password", json={"mobile_no": bad_mobile})

    assert r.status_code == 400
    body = r.get_json()
    assert "mobile" in body["message"].lower()



@pytest.mark.integration
def test_forgot_user_not_found_email_returns_200(mock_send_otp,fake_redis,client):
    email = "ghost@test.com"
    r = client.post("/forgot-password", json={"email": email})
    assert r.status_code == 200
    body = r.get_json()
    assert "if the account exists" in body["message"].lower()
    mock_send_otp.assert_not_called()
    assert not fake_redis.exists(f"forgot_password_otp:{email}")


@pytest.mark.integration
def test_forgot_user_not_found_mobile_returns_200(client, fake_redis, mock_send_otp):
    mobile_no = "9999999999"

    r = client.post("/forgot-password", json={"mobile_no": mobile_no})

    assert r.status_code == 200
    body = r.get_json()
    assert "if the account exists" in body["message"].lower()

    mock_send_otp.assert_not_called()
    assert not fake_redis.exists(f"forgot_password_otp:{mobile_no}")
