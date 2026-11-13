"""
notices/routes.py – Notice board (announcements).
Important notices are pinned to the top.
Teachers: full CRUD on their own notices.
Students: read-only with search.
"""
from datetime import datetime, timezone
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort)
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Announcement
from app.decorators import teacher_required
from app.utils import log_activity
from .forms import AnnouncementForm

notices_bp = Blueprint("notices", __name__, url_prefix="/notices")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@notices_bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    query = Announcement.query
    if q:
        query = query.filter(
            (Announcement.title.ilike(f"%{q}%")) |
            (Announcement.body.ilike(f"%{q}%"))
        )
    # Important pinned first, then newest
    notices = query.order_by(
        Announcement.is_important.desc(),
        Announcement.publish_date.desc()
    ).all()
    return render_template("notices/index.html", notices=notices, q=q)


@notices_bp.route("/create", methods=["GET", "POST"])
@login_required
@teacher_required
def create():
    form = AnnouncementForm()
    if form.validate_on_submit():
        pub_date = form.publish_date.data or utcnow()
        notice = Announcement(
            title=form.title.data.strip(),
            body=form.body.data.strip(),
            is_important=form.is_important.data,
            publish_date=pub_date,
            author_id=current_user.id,
        )
        db.session.add(notice)
        db.session.commit()
        log_activity(current_user.id, "create_notice", f"Published: {notice.title}")
        flash("Notice published.", "success")
        return redirect(url_for("notices.index"))
    return render_template("notices/form.html", form=form, title="Create Notice")


@notices_bp.route("/<int:notice_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def edit(notice_id):
    notice = Announcement.query.get_or_404(notice_id)
    if notice.author_id != current_user.id:
        abort(403)
    form = AnnouncementForm(obj=notice)
    if form.validate_on_submit():
        notice.title = form.title.data.strip()
        notice.body = form.body.data.strip()
        notice.is_important = form.is_important.data
        if form.publish_date.data:
            notice.publish_date = form.publish_date.data
        notice.updated_at = utcnow()
        db.session.commit()
        flash("Notice updated.", "success")
        return redirect(url_for("notices.index"))
    return render_template("notices/form.html", form=form, title="Edit Notice", notice=notice)


@notices_bp.route("/<int:notice_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete(notice_id):
    notice = Announcement.query.get_or_404(notice_id)
    if notice.author_id != current_user.id:
        abort(403)
    db.session.delete(notice)
    db.session.commit()
    flash("Notice deleted.", "success")
    return redirect(url_for("notices.index"))
