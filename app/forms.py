"""WTForms with server-side validation (length, email, password policy)."""
import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, Email, Length, ValidationError

PASSWORD_PATTERN = re.compile(
    r"^(?=.{8,128}$)(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$"
)


def password_strength(form, field):
    if not field.data:
        return
    if not PASSWORD_PATTERN.match(field.data):
        raise ValidationError(
            "Password must be 8–128 characters and include uppercase, lowercase, "
            "a number, and a special character."
        )


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=80, message="Username must be 3–80 characters."),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email address."),
            Length(max=255),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required."),
            password_strength,
        ],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(message="Please confirm your password.")],
    )
    role = SelectField(
        "Role",
        choices=[("user", "User"), ("admin", "Admin")],
        validators=[DataRequired()],
    )
    captcha_answer = StringField(
        "CAPTCHA",
        validators=[DataRequired(message="Please solve the CAPTCHA.")],
    )

    def validate_confirm_password(self, field):
        if self.password.data != field.data:
            raise ValidationError("Passwords do not match.")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email address."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required.")],
    )
    captcha_answer = StringField(
        "CAPTCHA",
        validators=[DataRequired(message="Please solve the CAPTCHA.")],
    )
    remember_device = BooleanField("Remember session (longer token default off)", default=False)


class CSRFForm(FlaskForm):
    """POST actions that only need CSRF protection (IDs come from URL)."""

    pass
