from datetime import datetime, timezone

import bcrypt
from flask_login import UserMixin

from app import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    invite_token = db.Column(db.String(64), unique=True, nullable=True)
    invited_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reset_token = db.Column(db.String(64), unique=True, nullable=True)
    reset_token_expires_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash or self.password_hash == "pending":
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )


class SiteSetting(db.Model):
    """Key/value store for runtime-configurable site settings."""

    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
