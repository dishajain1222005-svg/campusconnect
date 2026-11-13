"""
teacher/routes.py – Teacher dashboard.
All statistics come from real DB queries.
"""
from datetime import datetime, timezone
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.decorators import teacher_required
from app.extensions import db
from app.models import (User, StudyMaterial, Assignment, AssignmentSubmission,
                        Quiz, Announcement, ActivityLog)

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@teacher_bp.route("/dashboard")
@login_required
@teacher_required
def dashboard():
    total_students = User.query.filter_by(role="student").count()
    my_materials = StudyMaterial.query.filter_by(uploaded_by=current_user.id).count()
    my_assignments = Assignment.query.filter_by(created_by=current_user.id).count()
    my_notices = Announcement.query.filter_by(author_id=current_user.id).count()
    my_quizzes = Quiz.query.filter_by(created_by=current_user.id).count()

    # Recent submissions across all my assignments
    my_assignment_ids = [a.id for a in
                         Assignment.query.filter_by(created_by=current_user.id).all()]
    recent_submissions = []
    if my_assignment_ids:
        recent_submissions = (AssignmentSubmission.query
                              .filter(AssignmentSubmission.assignment_id.in_(my_assignment_ids))
                              .order_by(AssignmentSubmission.submitted_at.desc())
                              .limit(10).all())

    recent_activity = (ActivityLog.query
                       .order_by(ActivityLog.created_at.desc())
                       .limit(15).all())

    return render_template("teacher/dashboard.html",
                           total_students=total_students,
                           my_materials=my_materials,
                           my_assignments=my_assignments,
                           my_notices=my_notices,
                           my_quizzes=my_quizzes,
                           recent_submissions=recent_submissions,
                           recent_activity=recent_activity)
