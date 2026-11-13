"""
auth/routes.py – Login, registration, and logout.

Security: The registration form never reads 'role' from the POST data.
Role is hardcoded to 'student' on line 42.  Even if an attacker injects
role=teacher in the request body, it is ignored.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models import User
from app.utils import log_activity, is_safe_url
from .forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _role_redirect(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        # Generic error message – do not reveal whether the username exists
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", "danger")
            return render_template("auth/login.html", form=form)

        login_user(user, remember=form.remember.data)
        log_activity(user.id, "login", f"Logged in from {request.remote_addr}")

        # Safe next-URL validation prevents open-redirect attacks
        next_page = request.args.get("next")
        if next_page and is_safe_url(next_page):
            return redirect(next_page)
        return _role_redirect(user)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _role_redirect(current_user)

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            role="student",   # ← ALWAYS 'student'; never read from form
            roll_no=(form.roll_no.data or "").strip() or None,
            department=(form.department.data or "").strip() or None,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_activity(user.id, "register", "New student registration")
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    log_activity(current_user.id, "logout", "")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def _role_redirect(user):
    if user.is_teacher:
        return redirect(url_for("teacher.dashboard"))
    return redirect(url_for("student.dashboard"))
