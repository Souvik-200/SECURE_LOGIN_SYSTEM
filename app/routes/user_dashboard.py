"""Authenticated user (non-admin) dashboard."""
from flask import Blueprint, redirect, render_template, url_for
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import UserRole
from app.services.user_service import find_user_by_id

user_bp = Blueprint("user", __name__)


@user_bp.route("/dashboard")
def dashboard():
    try:
        verify_jwt_in_request()
    except Exception:
        return redirect(url_for("auth.login_page"))
    uid = get_jwt_identity()
    if uid is None:
        return redirect(url_for("auth.login_page"))
    user = find_user_by_id(int(uid))
    if not user or not user.is_active:
        return redirect(url_for("auth.logout"))
    if user.role == UserRole.ADMIN:
        return redirect(url_for("admin.dashboard"))
    return render_template("user_dashboard.html", user=user)
