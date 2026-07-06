from app.models import User


def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Log in" in response.data


def test_login_success(client, admin_user):
    response = client.post(
        "/login",
        data={"email": "admin@test.com", "password": "Password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_login_wrong_password(client, admin_user):
    response = client.post(
        "/login",
        data={"email": "admin@test.com", "password": "wrong"},
        follow_redirects=True,
    )
    assert b"Invalid email or password" in response.data


def test_logout(logged_in_client):
    response = logged_in_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Log in" in response.data


def test_index_requires_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_register_via_invite(client, db):
    user = User(
        email="new@test.com",
        password_hash="pending",
        display_name="new@test.com",
        invite_token="abc123",
    )
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/register/abc123",
        data={
            "display_name": "New User",
            "password": "GoodPass1",
            "password2": "GoodPass1",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    refreshed = User.query.filter_by(email="new@test.com").first()
    assert refreshed.invite_token is None
    assert refreshed.display_name == "New User"
    assert refreshed.check_password("GoodPass1")


def test_register_password_mismatch(client, db):
    user = User(
        email="new@test.com",
        password_hash="pending",
        display_name="new@test.com",
        invite_token="abc123",
    )
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/register/abc123",
        data={
            "display_name": "New User",
            "password": "GoodPass1",
            "password2": "Different1",
        },
        follow_redirects=True,
    )
    assert b"Passwords do not match" in response.data
    refreshed = User.query.filter_by(email="new@test.com").first()
    assert refreshed.invite_token == "abc123"


def test_forgot_password_creates_token(client, admin_user, db):
    response = client.post(
        "/forgot-password",
        data={"email": "admin@test.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    refreshed = db.session.get(User, admin_user.id)
    assert refreshed.reset_token is not None
    assert refreshed.reset_token_expires_at is not None


def test_forgot_password_unknown_email_no_leak(client):
    """Should show generic message even for unknown emails (anti-enumeration)."""
    response = client.post(
        "/forgot-password",
        data={"email": "nobody@test.com"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"sent a password reset link" in response.data
