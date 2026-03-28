"""Server-side math CAPTCHA stored in session (brute-force mitigation)."""
import random
import secrets
from datetime import datetime, timezone


def generate_challenge(session, ttl_seconds: int) -> str:
    """Store answer in session; return question text for the template."""
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    answer = str(a + b)
    nonce = secrets.token_hex(8)
    session["captcha_id"] = nonce
    session["captcha_answer"] = answer
    session["captcha_created"] = datetime.now(timezone.utc).timestamp()
    session["captcha_ttl"] = ttl_seconds
    return f"What is {a} + {b}?"


def verify_answer(session, user_answer: str | None) -> bool:
    """Validate CAPTCHA; reject if missing or past TTL; clear after verify (one-shot)."""
    if not captcha_fresh(session):
        return False
    if not user_answer or not str(user_answer).strip():
        return False
    expected = session.pop("captcha_answer", None)
    session.pop("captcha_id", None)
    session.pop("captcha_created", None)
    session.pop("captcha_ttl", None)
    if expected is None:
        return False
    try:
        return secrets.compare_digest(expected.strip(), str(user_answer).strip())
    except Exception:
        return False


def captcha_fresh(session) -> bool:
    """Drop expired captcha from session."""
    created = session.get("captcha_created")
    ttl = session.get("captcha_ttl", 0)
    if created is None:
        return False
    now = datetime.now(timezone.utc).timestamp()
    if now - float(created) > float(ttl):
        session.pop("captcha_answer", None)
        session.pop("captcha_id", None)
        session.pop("captcha_created", None)
        session.pop("captcha_ttl", None)
        return False
    return True