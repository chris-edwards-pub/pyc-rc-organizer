def test_admin_users_requires_admin(client, regular_user):
    client.post(
        "/login",
        data={"email": "user@test.com", "password": "Password123"},
        follow_redirects=True,
    )
    response = client.get("/admin/users", follow_redirects=True)
    assert b"Access denied" in response.data


def test_admin_users_allowed_for_admin(logged_in_client):
    response = logged_in_client.get("/admin/users")
    assert response.status_code == 200
    assert b"Users" in response.data


def test_admin_users_requires_login(client):
    response = client.get("/admin/users")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
