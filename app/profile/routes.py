"""Profile view and edit routes."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from .forms import ProfileForm, ChangePasswordForm

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def view():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data.strip()
        current_user.email = form.email.data.strip().lower()
        current_user.roll_no = form.roll_no.data.strip()
        current_user.department = form.department.data.strip()
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile.view"))
    return render_template("profile/view.html", form=form)


@profile_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
            return render_template("profile/change_password.html", form=form)
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Password changed successfully.", "success")
        return redirect(url_for("profile.view"))
    return render_template("profile/change_password.html", form=form)
