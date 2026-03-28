import os

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["WTF_CSRF_ENABLED"] = "false"

from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    app = create_app("development")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
