from app import __version__, create_app


def test_app_creates():
    app = create_app(test_config={"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    assert app is not None
    assert app.config["TESTING"] is True


def test_version_defined():
    assert __version__
    assert len(__version__.split(".")) == 3


def test_blueprints_registered(app):
    assert "auth" in app.blueprints
    assert "main" in app.blueprints
