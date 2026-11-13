"""
assignments/routes.py

Teacher: create, edit, delete assignments; view & download submissions.
Student: list assignments with status, detail page with countdown, submit/resubmit.

Resubmission: when a student resubmits before the deadline, the old file is
deleted from disk and the DB row is updated in-place (not duplicated).
Assignment status is COMPUTED: Pending / Submitted / Late.
"""
import os
from datetime import datetime, timezone
from pathlib import Path
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, abort, send_from_directory, current_app)
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Assignment, AssignmentSubmission, User
from app.decorators import teacher_required, student_required
from app.utils import validate_and_save, allowed_material, allowed_submission, log_activity
from .forms import AssignmentForm, SubmissionForm

assignments_bp = Blueprint("assignments", __name__, url_prefix="/assignments")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ─── Teacher views ────────────────────────────────────────────────────────────

@assignments_bp.route("/")
@login_required
def index():
    if current_user.is_teacher:
        items = Assignment.query.filter_by(created_by=current_user.id)\
            .order_by(Assignment.deadline.asc()).all()
        return render_template("assignments/teacher_list.html", assignments=items)
    else:
        # Student view
        items = Assignment.query.order_by(Assignment.deadline.asc()).all()
        # Build a map of assignment_id -> submission for this student
        subs = {s.assignment_id: s for s in
                AssignmentSubmission.query.filter_by(student_id=current_user.id).all()}
        return render_template("assignments/student_list.html",
                               assignments=items, subs=subs, now=utcnow())


@assignments_bp.route("/create", methods=["GET", "POST"])
@login_required
@teacher_required
def create():
    form = AssignmentForm()
    if form.validate_on_submit():
        ref_original = ref_stored = None
        if form.reference_file.data and form.reference_file.data.filename:
            try:
                info = validate_and_save(
                    form.reference_file.data,
                    current_app.config["ASSIGNMENT_REF_DIR"],
                    allowed_material,
                )
                ref_original = info["original_filename"]
                ref_stored = info["stored_filename"]
            except ValueError as e:
                flash(str(e), "danger")
                return render_template("assignments/form.html", form=form, title="Create Assignment")

        a = Assignment(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            subject=form.subject.data.strip(),
            deadline=form.deadline.data,
            ref_original_filename=ref_original,
            ref_stored_filename=ref_stored,
            created_by=current_user.id,
        )
        db.session.add(a)
        db.session.commit()
        log_activity(current_user.id, "create_assignment", f"Created: {a.title}")
        flash("Assignment created.", "success")
        return redirect(url_for("assignments.index"))
    return render_template("assignments/form.html", form=form, title="Create Assignment")


@assignments_bp.route("/<int:assignment_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def edit(assignment_id):
    a = Assignment.query.get_or_404(assignment_id)
    if a.created_by != current_user.id:
        abort(403)
    form = AssignmentForm(obj=a)
    if form.validate_on_submit():
        a.title = form.title.data.strip()
        a.description = form.description.data.strip()
        a.subject = form.subject.data.strip()
        a.deadline = form.deadline.data
        # Replace reference file if a new one is uploaded
        if form.reference_file.data and form.reference_file.data.filename:
            try:
                info = validate_and_save(
                    form.reference_file.data,
                    current_app.config["ASSIGNMENT_REF_DIR"],
                    allowed_material,
                )
                # Delete old ref file
                if a.ref_stored_filename:
                    old = current_app.config["ASSIGNMENT_REF_DIR"] / a.ref_stored_filename
                    if old.exists():
                        old.unlink()
                a.ref_original_filename = info["original_filename"]
                a.ref_stored_filename = info["stored_filename"]
            except ValueError as e:
                flash(str(e), "danger")
                return render_template("assignments/form.html", form=form, title="Edit Assignment", assignment=a)
        db.session.commit()
        flash("Assignment updated.", "success")
        return redirect(url_for("assignments.index"))
    return render_template("assignments/form.html", form=form, title="Edit Assignment", assignment=a)


@assignments_bp.route("/<int:assignment_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete(assignment_id):
    a = Assignment.query.get_or_404(assignment_id)
    if a.created_by != current_user.id:
        abort(403)
    # Remove reference file
    if a.ref_stored_filename:
        p = current_app.config["ASSIGNMENT_REF_DIR"] / a.ref_stored_filename
        if p.exists():
            p.unlink()
    # Remove all submission files
    for sub in a.submissions:
        sp = current_app.config["SUBMISSION_DIR"] / sub.stored_filename
        if sp.exists():
            sp.unlink()
    db.session.delete(a)
    db.session.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("assignments.index"))


@assignments_bp.route("/<int:assignment_id>/submissions")
@login_required
@teacher_required
def submissions(assignment_id):
    a = Assignment.query.get_or_404(assignment_id)
    if a.created_by != current_user.id:
        abort(403)
    subs = (AssignmentSubmission.query
            .filter_by(assignment_id=assignment_id)
            .join(User, AssignmentSubmission.student_id == User.id)
            .order_by(AssignmentSubmission.submitted_at.desc())
            .all())
    return render_template("assignments/submissions.html", assignment=a, subs=subs)


@assignments_bp.route("/download/ref/<int:assignment_id>")
@login_required
def download_ref(assignment_id):
    """Download the teacher's reference file for an assignment."""
    a = Assignment.query.get_or_404(assignment_id)
    if not a.ref_stored_filename:
        abort(404)
    return send_from_directory(
        str(current_app.config["ASSIGNMENT_REF_DIR"]),
        a.ref_stored_filename,
        as_attachment=True,
        download_name=a.ref_original_filename,
    )


@assignments_bp.route("/download/submission/<int:submission_id>")
@login_required
def download_submission(submission_id):
    """
    Authenticated submission download.
    Students can download only their own submission.
    Teachers can download submissions for assignments they created.
    """
    sub = AssignmentSubmission.query.get_or_404(submission_id)
    if current_user.is_student and sub.student_id != current_user.id:
        abort(403)
    if current_user.is_teacher and sub.assignment.created_by != current_user.id:
        abort(403)
    return send_from_directory(
        str(current_app.config["SUBMISSION_DIR"]),
        sub.stored_filename,
        as_attachment=True,
        download_name=sub.original_filename,
    )


# ─── Student views ────────────────────────────────────────────────────────────

@assignments_bp.route("/<int:assignment_id>")
@login_required
def detail(assignment_id):
    a = Assignment.query.get_or_404(assignment_id)
    sub = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id, student_id=current_user.id
    ).first() if current_user.is_student else None
    form = SubmissionForm() if current_user.is_student else None
    return render_template("assignments/detail.html",
                           assignment=a, submission=sub, form=form, now=utcnow())


@assignments_bp.route("/<int:assignment_id>/submit", methods=["POST"])
@login_required
@student_required
def submit(assignment_id):
    a = Assignment.query.get_or_404(assignment_id)
    form = SubmissionForm()
    if not form.validate_on_submit():
        flash("Form validation failed. Try again.", "danger")
        return redirect(url_for("assignments.detail", assignment_id=assignment_id))

    if not form.file.data or not form.file.data.filename:
        flash("Please select a file to submit.", "danger")
        return redirect(url_for("assignments.detail", assignment_id=assignment_id))

    try:
        info = validate_and_save(
            form.file.data,
            current_app.config["SUBMISSION_DIR"],
            allowed_submission,
        )
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("assignments.detail", assignment_id=assignment_id))

    existing = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id, student_id=current_user.id
    ).first()

    if existing:
        # Resubmission: delete old file, update record
        old_path = current_app.config["SUBMISSION_DIR"] / existing.stored_filename
        if old_path.exists():
            old_path.unlink()
        existing.original_filename = info["original_filename"]
        existing.stored_filename = info["stored_filename"]
        existing.submitted_at = utcnow()
        db.session.commit()
        log_activity(current_user.id, "resubmit_assignment",
                     f"Resubmitted: {a.title}")
        flash("Assignment resubmitted successfully.", "success")
    else:
        sub = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            original_filename=info["original_filename"],
            stored_filename=info["stored_filename"],
        )
        db.session.add(sub)
        db.session.commit()
        log_activity(current_user.id, "submit_assignment", f"Submitted: {a.title}")
        status = "late" if utcnow() > a.deadline else "on time"
        flash(f"Assignment submitted ({status}).", "success")

    return redirect(url_for("assignments.detail", assignment_id=assignment_id))
