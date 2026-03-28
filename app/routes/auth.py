"""Registration, login, logout — JWT in httpOnly cookie."""
from datetime import timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies

from app.captcha import generate_challenge, verify_answer
from app.forms import LoginForm, RegistrationForm
from app.services.user_service import (
    authenticate_user,
    clear_lockout_on_success,
    record_failed_login,
    register_user,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _captcha_ttl():
    from flask import current_app

    return int(current_app.config.get("CAPTCHA_TTL_SECONDS", 600))


@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        if not verify_answer(session, form.captcha_answer.data):
            flash("CAPTCHA verification failed. Please try again.", "danger")
            return render_template(
                "register.html",
                form=form,
                captcha_question=generate_challenge(session, _captcha_ttl()),
            )

        user, err = register_user(
            form.username.data,
            form.email.data,
            form.password.data,
            form.role.data,
        )
        if err:
            flash(err, "danger")
            return render_template(
                "register.html",
                form=form,
                captcha_question=generate_challenge(session, _captcha_ttl()),
            )

        flash("Registration successful. Please sign in.", "success")
        return redirect(url_for("auth.login_page"))

    captcha_question = generate_challenge(session, _captcha_ttl())
    return render_template(
        "register.html", form=form, captcha_question=captcha_question
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        if not verify_answer(session, form.captcha_answer.data):
            flash("CAPTCHA verification failed. Please try again.", "danger")
            return render_template(
                "login.html",
                form=form,
                captcha_question=generate_challenge(session, _captcha_ttl()),
            )

        user, err = authenticate_user(form.email.data, form.password.data)
        if err == "bad_password":
            msg = record_failed_login(user)
            flash(msg, "danger")
            return render_template(
                "login.html",
                form=form,
                captcha_question=generate_challenge(session, _captcha_ttl()),
            )
        if err:
            flash(err, "danger")
            return render_template(
                "login.html",
                form=form,
                captcha_question=generate_challenge(session, _captcha_ttl()),
            )

        clear_lockout_on_success(user)
        token_kwargs = {
            "identity": str(user.id),
            "additional_claims": {"role": user.role},
        }
        if form.remember_device.data:
            token_kwargs["expires_delta"] = timedelta(days=7)
        token = create_access_token(**token_kwargs)

        resp = redirect(url_for("main.index"))
        set_access_cookies(resp, token)
        flash("Signed in successfully.", "success")
        return resp

    captcha_question = generate_challenge(session, _captcha_ttl())
    return render_template("login.html", form=form, captcha_question=captcha_question)


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    resp = redirect(url_for("auth.login_page"))
    unset_jwt_cookies(resp)
    flash("You have been signed out.", "info")
    return resp
