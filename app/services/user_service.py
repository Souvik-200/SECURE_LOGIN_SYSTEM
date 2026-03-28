"""User registration and account lockout logic."""
from datetime import datetime, timedelta, timezone

from flask import current_app

from app.extensions import db
from app.models import User, UserRole
from app.security import hash_password, verify_password


def find_user_by_email(email: str) -> User | None:
    return User.query.filter_by(email=email.lower().strip()).first()


def find_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def register_user(
    username: str,
    email: str,
    password: str,
    requested_role: str,
) -> tuple[User | None, str | None]:
    """
    Create user. Returns (user, error_message).
    Admin role only if ALLOW_PUBLIC_ADMIN_REGISTRATION is True.
    """
    email_n = email.lower().strip()
    username_n = username.strip()

    if find_user_by_email(email_n):
        return None, "An account with this email already exists."
    if User.query.filter_by(username=username_n).first():
        return None, "This username is already taken."

    role = UserRole.USER
    if (
        requested_role == UserRole.ADMIN
        and current_app.config.get("ALLOW_PUBLIC_ADMIN_REGISTRATION")
    ):
        role = UserRole.ADMIN

    user = User(
        username=username_n,
        email=email_n,
        password_hash=hash_password(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user, None


def clear_lockout_on_success(user: User) -> None:
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()


def record_failed_login(user: User) -> str:
    """
    Increment failures; lock if threshold reached. Returns error message for display.
    """
    max_attempts = current_app.config["MAX_FAILED_LOGIN_ATTEMPTS"]
    lock_minutes = current_app.config["LOCKOUT_MINUTES"]

    if user.is_locked():
        return "This account is temporarily locked due to repeated failed logins."

    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= max_attempts:
        user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=lock_minutes)
        db.session.commit()
        return (
            f"Too many failed attempts. Account locked for {lock_minutes} minutes."
        )

    db.session.commit()
    return "Invalid email or password."


def authenticate_user(email: str, password: str) -> tuple[User | None, str | None]:
    """
    Verify credentials.
    Returns (user, err) where err is None on success, or message / 'bad_password'.
    """
    user = find_user_by_email(email)
    if user is None:
        return None, "Invalid email or password."

    if not user.is_active:
        return None, "This account has been deactivated."

    if user.is_locked():
        return None, "This account is temporarily locked. Try again later."

    if verify_password(password, user.password_hash):
        return user, None

    return user, "bad_password"
