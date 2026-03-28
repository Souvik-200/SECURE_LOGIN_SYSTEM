"""Public pages and post-login redirect hub."""
from flask import Blueprint, redirect, url_for
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import UserRole
from app.services.user_service import find_user_by_id

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
    except Exception:
        uid = None
    if not uid:
        return redirect(url_for("auth.login_page"))
    user = find_user_by_id(int(uid))
    if not user or not user.is_active:
        return redirect(url_for("auth.logout"))
    if user.role == UserRole.ADMIN:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("user.dashboard"))


@main_bp.route("/health")
def health():
    return {"status": "ok"}, 200
