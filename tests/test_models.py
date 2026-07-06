from app.models import SiteSetting, User


def test_user_password_hashing(db):
    user = User(email="a@b.com", display_name="A")
    user.set_password("SuperSecret1")
    db.session.add(user)
    db.session.commit()

    assert user.password_hash != "SuperSecret1"
    assert user.check_password("SuperSecret1") is True
    assert user.check_password("wrong") is False


def test_pending_user_cannot_login(db):
    """Users with password_hash='pending' (invited but not registered) can't check_password."""
    user = User(
        email="pending@test.com",
        display_name="Pending",
        password_hash="pending",
        invite_token="tok123",
    )
    db.session.add(user)
    db.session.commit()

    assert user.check_password("anything") is False


def test_site_setting_unique_key(db):
    db.session.add(SiteSetting(key="theme", value="dark"))
    db.session.commit()

    got = SiteSetting.query.filter_by(key="theme").first()
    assert got is not None
    assert got.value == "dark"
