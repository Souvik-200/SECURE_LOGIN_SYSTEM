"""Admin-only RBAC: manage users."""
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from app.decorators import admin_required
from app.extensions import db
from app.forms import CSRFForm
from app.models import User, UserRole
from app.services.user_service import find_user_by_id

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    action_form = CSRFForm()
    return render_template(
        "admin_dashboard.html",
        users=users,
        current_uid=int(get_jwt_identity()),
        action_form=action_form,
        UserRole=UserRole,
    )


@admin_bp.post("/users/<int:target_id>/toggle-active")
@admin_required
def toggle_active(target_id: int):
    form = CSRFForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("admin.dashboard"))
    actor_id = int(get_jwt_identity())
    if target_id == actor_id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("admin.dashboard"))
    user = find_user_by_id(target_id)
    if not user:
        abort(404)
    user.is_active = not user.is_active
    try:
        db.session.commit()
        flash(f"User {user.username} active={user.is_active}.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Failed to update user status due to a database error.", "danger")
    return redirect(url_for("admin.dashboard"))


@admin_bp.post("/users/<int:target_id>/set-role")
@admin_required
def set_role(target_id: int):
    form = CSRFForm()
    if not form.validate_on_submit():
        flash("Invalid request.", "danger")
        return redirect(url_for("admin.dashboard"))
    user = find_user_by_id(target_id)
    if not user:
        abort(404)
    actor_id = int(get_jwt_identity())
    if user.role == UserRole.ADMIN:
        new_role = UserRole.USER
    else:
        new_role = UserRole.ADMIN
    if target_id == actor_id and new_role == UserRole.USER:
        flash("You cannot remove your own admin role.", "warning")
        return redirect(url_for("admin.dashboard"))
    user.role = new_role
    try:
        db.session.commit()
        flash(f"Role for {user.username} set to {new_role}.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Failed to update user role due to a database error.", "danger")
    return redirect(url_for("admin.dashboard"))
