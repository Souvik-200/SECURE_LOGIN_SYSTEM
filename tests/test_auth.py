"""End-to-end style tests: registration, login, lockout, RBAC thresholds."""
from app.extensions import db
from app.models import User, UserRole


def _captcha_from_session(client):
    with client.session_transaction() as sess:
        return sess.get("captcha_answer")


def test_register_duplicate_email(client, app):
    with app.app_context():
        u = User(
            username="exists",
            email="dup@example.com",
            password_hash="$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            role=UserRole.USER,
        )
        db.session.add(u)
        db.session.commit()

    client.get("/auth/register")
    ans = _captcha_from_session(client)
    rv = client.post(
        "/auth/register",
        data={
            "username": "newname",
            "email": "dup@example.com",
            "password": "Strong1!a",
            "confirm_password": "Strong1!a",
            "role": "user",
            "captcha_answer": ans,
        },
        follow_redirects=True,
    )
    assert rv.status_code == 200
    body = rv.data.lower()
    assert b"already" in body or b"exists" in body


def test_register_and_login_user_dashboard(client, app):
    client.get("/auth/register")
    ans = _captcha_from_session(client)
    rv = client.post(
        "/auth/register",
        data={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Strong1!a",
            "confirm_password": "Strong1!a",
            "role": "user",
            "captcha_answer": ans,
        },
        follow_redirects=False,
    )
    assert rv.status_code in (302, 301)

    client.get("/auth/login")
    ans2 = _captcha_from_session(client)
    rv2 = client.post(
        "/auth/login",
        data={
            "email": "alice@example.com",
            "password": "Strong1!a",
            "captcha_answer": ans2,
        },
        follow_redirects=True,
    )
    assert rv2.status_code == 200
    assert b"User dashboard" in rv2.data or b"user dashboard" in rv2.data.lower()


def test_lockout_blocks_correct_password(client, app):
    app.config["MAX_FAILED_LOGIN_ATTEMPTS"] = 3
    app.config["LOCKOUT_MINUTES"] = 15
    with app.app_context():
        from app.security import hash_password

        u = User(
            username="bob",
            email="bob@example.com",
            password_hash=hash_password("Correct1!z"),
            role=UserRole.USER,
        )
        db.session.add(u)
        db.session.commit()

    for _ in range(3):
        client.get("/auth/login")
        ca = _captcha_from_session(client)
        client.post(
            "/auth/login",
            data={
                "email": "bob@example.com",
                "password": "wrong",
                "captcha_answer": ca,
            },
        )

    client.get("/auth/login")
    ca = _captcha_from_session(client)
    rv = client.post(
        "/auth/login",
        data={
            "email": "bob@example.com",
            "password": "Correct1!z",
            "captcha_answer": ca,
        },
        follow_redirects=True,
    )
    assert b"locked" in rv.data.lower()


def test_regular_user_gets_403_on_admin(client, app):
    with app.app_context():
        from app.security import hash_password

        db.session.add(
            User(
                username="carl",
                email="carl@example.com",
                password_hash=hash_password("Strong1!a"),
                role=UserRole.USER,
            ),
        )
        db.session.commit()

    client.get("/auth/login")
    ca = _captcha_from_session(client)
    client.post(
        "/auth/login",
        data={
            "email": "carl@example.com",
            "password": "Strong1!a",
            "captcha_answer": ca,
        },
        follow_redirects=True,
    )
    rv = client.get("/admin/dashboard")
    assert rv.status_code == 403
