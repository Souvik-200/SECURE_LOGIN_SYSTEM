"""Flask application factory."""
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from config import Config

_REPO_ROOT = Path(__file__).resolve().parent.parent
from app.extensions import csrf, db, jwt

__all__ = ["create_app"]


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(_REPO_ROOT / "templates"),
        static_folder=str(_REPO_ROOT / "static"),
    )
    app.config.from_object(Config)
    if os.environ.get("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
        url = app.config["SQLALCHEMY_DATABASE_URI"]
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = (
            {"pool_pre_ping": True, "pool_recycle": 300}
            if url.startswith("mysql")
            else {}
        )

    if config_name == "development":
        app.config["DEBUG"] = True

    _ensure_instance_folder(app)
    db.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)

    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")

    with app.app_context():
        db.create_all()

    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.user_dashboard import user_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    _register_cli(app)

    @app.shell_context_processor
    def shell_ctx():
        from app.models import User

        return {"db": db, "User": User}

    return app


def _ensure_instance_folder(app):
    instance_path = app.instance_path
    os.makedirs(instance_path, exist_ok=True)


def _register_cli(app):
    import click

    from app.models import User, UserRole
    from app.security import hash_password

    @app.cli.command("create-admin")
    @click.argument("username")
    @click.argument("email")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, email, password):
        """Create an admin user (CLI). Bypasses public registration policy."""
        db.create_all()
        email_l = email.lower().strip()
        if User.query.filter_by(email=email_l).first():
            click.echo("Email already registered.")
            return
        if User.query.filter_by(username=username.strip()).first():
            click.echo("Username taken.")
            return
        u = User(
            username=username.strip(),
            email=email_l,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
        )
        db.session.add(u)
        db.session.commit()
        click.echo(f"Admin created: {u.username} ({u.email})")

    @app.cli.command("init-db")
    def init_db():
        """Create database tables."""
        db.create_all()
        click.echo("Tables created.")
