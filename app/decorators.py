"""RBAC decorators for admin-only routes."""
from functools import wraps

from flask import abort, redirect, url_for
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import User, UserRole
from app.services.user_service import find_user_by_id


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=False)
        except Exception:
            return redirect(url_for("auth.login_page"))
        uid = get_jwt_identity()
        if uid is None:
            abort(401)
        user = find_user_by_id(int(uid))
        if not user or user.role != UserRole.ADMIN or not user.is_active:
            abort(403)
        return fn(*args, **kwargs)

    return wrapper
