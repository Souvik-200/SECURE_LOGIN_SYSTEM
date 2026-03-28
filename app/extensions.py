"""Shared Flask extensions (initialized in app factory)."""
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
jwt = JWTManager()
csrf = CSRFProtect()
