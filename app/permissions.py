"""Role-based permission decorators."""

from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def require_admin(f):
    """Decorator: deny access unless current_user is admin."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Access denied.", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated
