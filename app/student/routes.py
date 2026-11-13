"""
student/routes.py – Student dashboard.
All statistics come from real DB queries.
"""
from datetime import datetime, timezone
from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import student_required
from app.extensions import db
from app.models import (StudyMaterial, Assignment, AssignmentSubmission,
                        Quiz, QuizAttempt, Announcement, ActivityLog)

student_bp = Blueprint("student", __name__, url_prefix="/student")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    from flask_login import current_user

    # Counts
    total_materials = StudyMaterial.query.count()
    total_quizzes = Quiz.query.filter_by(is_published=True).count()

    # Pending assignments (not yet submitted by this student)
    all_assignment_ids = {a.id for a in Assignment.query.all()}
    submitted_ids = {s.assignment_id for s in
                     AssignmentSubmission.query.filter_by(student_id=current_user.id).all()}
    pending_count = len(all_assignment_ids - submitted_ids)

    # Upcoming deadlines (next 5 not yet submitted, deadline in future)
    if submitted_ids:
        upcoming = (Assignment.query
                    .filter(Assignment.id.notin_(submitted_ids))
                    .filter(Assignment.deadline > utcnow())
                    .order_by(Assignment.deadline.asc())
                    .limit(5).all())
    else:
        upcoming = (Assignment.query
                    .filter(Assignment.deadline > utcnow())
                    .order_by(Assignment.deadline.asc())
                    .limit(5).all())

    # Recent announcements
    recent_notices = (Announcement.query
                      .order_by(Announcement.is_important.desc(),
                                Announcement.publish_date.desc())
                      .limit(5).all())

    # Recent activity for this student
    recent_activity = (ActivityLog.query
                       .filter_by(user_id=current_user.id)
                       .order_by(ActivityLog.created_at.desc())
                       .limit(10).all())

    return render_template("student/dashboard.html",
                           total_materials=total_materials,
                           total_quizzes=total_quizzes,
                           pending_count=pending_count,
                           upcoming=upcoming,
                           recent_notices=recent_notices,
                           recent_activity=recent_activity,
                           now=utcnow())
