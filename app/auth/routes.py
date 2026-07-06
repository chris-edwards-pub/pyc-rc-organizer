import logging
import secrets
from datetime import datetime, timedelta, timezone

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.auth import bp
from app.models import User
from app.permissions import require_admin

logger = logging.getLogger(__name__)


def _validate_password_strength(password: str) -> str | None:
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one number."
    return None


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user and user.invite_token is None and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@bp.route("/register/<token>", methods=["GET", "POST"])
def register(token: str):
    user = User.query.filter_by(invite_token=token).first_or_404()

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        strength_error = _validate_password_strength(password)
        if not display_name:
            flash("Name is required.", "error")
        elif strength_error:
            flash(strength_error, "error")
        elif password != password2:
            flash("Passwords do not match.", "error")
        else:
            user.display_name = display_name
            user.set_password(password)
            user.invite_token = None
            db.session.commit()

            login_user(user)
            flash("Welcome!", "success")
            return redirect(url_for("main.index"))

    return render_template("register.html", user=user)


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.invite_token is None:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expires_at = datetime.now(timezone.utc).replace(
                tzinfo=None
            ) + timedelta(hours=1)
            db.session.commit()

            reset_url = url_for("auth.reset_password", token=token, _external=True)
            # In a real deployment, hook up an email sender here (SES, etc.).
            # For now, log the URL — check server logs to complete the flow.
            logger.info("Password reset URL for %s: %s", email, reset_url)

        # Always show generic message to prevent email enumeration.
        flash(
            "If an account with that email exists, we've sent a password reset link.",
            "info",
        )
        return redirect(url_for("auth.forgot_password"))

    return render_template("forgot_password.html")


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    user = User.query.filter_by(reset_token=token).first_or_404()

    if user.reset_token_expires_at and user.reset_token_expires_at < datetime.now(
        timezone.utc
    ).replace(tzinfo=None):
        flash("This reset link has expired. Please request a new one.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        strength_error = _validate_password_strength(password)
        if strength_error:
            flash(strength_error, "error")
        elif password != password2:
            flash("Passwords do not match.", "error")
        else:
            user.set_password(password)
            user.reset_token = None
            user.reset_token_expires_at = None
            db.session.commit()
            flash("Your password has been reset. Please log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not display_name or not email:
            flash("Name and email are required.", "error")
        elif email != current_user.email and User.query.filter_by(email=email).first():
            flash("That email is already in use.", "error")
        elif password and _validate_password_strength(password):
            flash(_validate_password_strength(password), "error")
        elif password and password != password2:
            flash("Passwords do not match.", "error")
        else:
            current_user.display_name = display_name
            current_user.email = email
            if password:
                current_user.set_password(password)
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("auth.profile"))

    return render_template("profile.html")


# ---------------------------------------------------------------------------
# Admin: user management
# ---------------------------------------------------------------------------


@bp.route("/admin/users")
@login_required
@require_admin
def admin_users():
    users = User.query.order_by(User.display_name).all()
    return render_template("admin_users.html", users=users)


@bp.route("/admin/users/invite", methods=["POST"])
@login_required
@require_admin
def invite_user():
    email = request.form.get("email", "").strip().lower()
    if not email:
        flash("Email is required.", "error")
        return redirect(url_for("auth.admin_users"))

    if User.query.filter_by(email=email).first():
        flash("A user with that email already exists.", "error")
        return redirect(url_for("auth.admin_users"))

    is_admin = request.form.get("is_admin") == "on"
    token = secrets.token_urlsafe(32)
    user = User(
        email=email,
        password_hash="pending",
        display_name=email,
        invite_token=token,
        is_admin=is_admin,
        invited_by=current_user.id,
    )
    db.session.add(user)
    db.session.commit()

    invite_url = url_for("auth.register", token=token, _external=True)
    flash(f"Invite link: {invite_url}", "success")
    return redirect(url_for("auth.admin_users"))


@bp.route("/admin/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@require_admin
def edit_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.admin_users"))

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        is_admin = request.form.get("is_admin") == "on"
        password = request.form.get("password", "")

        if not display_name or not email:
            flash("Name and email are required.", "error")
        elif email != user.email and User.query.filter_by(email=email).first():
            flash("That email is already in use.", "error")
        elif password and _validate_password_strength(password):
            flash(_validate_password_strength(password), "error")
        else:
            user.display_name = display_name
            user.email = email
            user.is_admin = is_admin
            if password:
                user.set_password(password)
            db.session.commit()
            flash(f"User '{display_name}' updated.", "success")
            return redirect(url_for("auth.admin_users"))

    return render_template("edit_user.html", user=user)


@bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
@require_admin
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("User not found.", "error")
    elif user.id == current_user.id:
        flash("You cannot delete yourself.", "error")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.display_name} deleted.", "success")

    return redirect(url_for("auth.admin_users"))
