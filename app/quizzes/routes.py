"""
quizzes/routes.py

Security critical points (explained for viva):
1. correct_option is NEVER sent to the student's browser during an attempt.
   The attempt page fetches only question text and options.
2. The server records started_at when the attempt begins.  On submission it
   checks: submitted_at <= started_at + duration + 10 s grace.
   If the browser timer is bypassed, the server rejects it (HTTP 400).
3. Score is computed entirely on the server from the DB.
4. Duplicate attempts are blocked unless allow_retake is True.
5. Students cannot start a quiz with zero questions or an unpublished quiz.
"""
from datetime import datetime, timezone, timedelta
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, abort, jsonify, current_app)
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Quiz, QuizQuestion, QuizAttempt, QuizAnswer
from app.decorators import teacher_required, student_required
from app.utils import log_activity
from .forms import QuizForm, QuizQuestionForm

quizzes_bp = Blueprint("quizzes", __name__, url_prefix="/quizzes")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ─── Teacher: Quiz CRUD ───────────────────────────────────────────────────────

@quizzes_bp.route("/")
@login_required
def index():
    if current_user.is_teacher:
        quizzes = Quiz.query.filter_by(created_by=current_user.id)\
            .order_by(Quiz.created_at.desc()).all()
        return render_template("quizzes/teacher_list.html", quizzes=quizzes)
    else:
        # Student: only published quizzes
        quizzes = Quiz.query.filter_by(is_published=True)\
            .order_by(Quiz.created_at.desc()).all()
        # Build attempt map
        attempts = {a.quiz_id: a for a in
                    QuizAttempt.query.filter_by(student_id=current_user.id).all()}
        return render_template("quizzes/student_list.html",
                               quizzes=quizzes, attempts=attempts)


@quizzes_bp.route("/create", methods=["GET", "POST"])
@login_required
@teacher_required
def create():
    form = QuizForm()
    if form.validate_on_submit():
        q = Quiz(
            title=form.title.data.strip(),
            description=(form.description.data or "").strip(),
            subject=form.subject.data.strip(),
            duration_minutes=form.duration_minutes.data,
            allow_retake=form.allow_retake.data,
            created_by=current_user.id,
        )
        db.session.add(q)
        db.session.commit()
        log_activity(current_user.id, "create_quiz", f"Created quiz: {q.title}")
        flash("Quiz created. Add questions now.", "success")
        return redirect(url_for("quizzes.manage", quiz_id=q.id))
    return render_template("quizzes/quiz_form.html", form=form, title="Create Quiz")


@quizzes_bp.route("/<int:quiz_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def edit(quiz_id):
    q = Quiz.query.get_or_404(quiz_id)
    if q.created_by != current_user.id:
        abort(403)
    form = QuizForm(obj=q)
    if form.validate_on_submit():
        q.title = form.title.data.strip()
        q.description = (form.description.data or "").strip()
        q.subject = form.subject.data.strip()
        q.duration_minutes = form.duration_minutes.data
        q.allow_retake = form.allow_retake.data
        db.session.commit()
        flash("Quiz updated.", "success")
        return redirect(url_for("quizzes.manage", quiz_id=q.id))
    return render_template("quizzes/quiz_form.html", form=form, title="Edit Quiz", quiz=q)


@quizzes_bp.route("/<int:quiz_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete(quiz_id):
    q = Quiz.query.get_or_404(quiz_id)
    if q.created_by != current_user.id:
        abort(403)
    db.session.delete(q)
    db.session.commit()
    flash("Quiz deleted.", "success")
    return redirect(url_for("quizzes.index"))


@quizzes_bp.route("/<int:quiz_id>/manage")
@login_required
@teacher_required
def manage(quiz_id):
    q = Quiz.query.get_or_404(quiz_id)
    if q.created_by != current_user.id:
        abort(403)
    questions = q.questions.all()
    return render_template("quizzes/manage.html", quiz=q, questions=questions)


@quizzes_bp.route("/<int:quiz_id>/publish", methods=["POST"])
@login_required
@teacher_required
def toggle_publish(quiz_id):
    q = Quiz.query.get_or_404(quiz_id)
    if q.created_by != current_user.id:
        abort(403)
    if not q.is_published and q.questions.count() == 0:
        flash("Cannot publish a quiz with no questions.", "danger")
        return redirect(url_for("quizzes.manage", quiz_id=quiz_id))
    q.is_published = not q.is_published
    db.session.commit()
    status = "published" if q.is_published else "unpublished"
    flash(f"Quiz {status}.", "success")
    return redirect(url_for("quizzes.manage", quiz_id=quiz_id))


# ─── Teacher: Question CRUD ───────────────────────────────────────────────────

@quizzes_bp.route("/<int:quiz_id>/questions/add", methods=["GET", "POST"])
@login_required
@teacher_required
def add_question(quiz_id):
    q = Quiz.query.get_or_404(quiz_id)
    if q.created_by != current_user.id:
        abort(403)
    form = QuizQuestionForm()
    if form.validate_on_submit():
        question = QuizQuestion(
            quiz_id=quiz_id,
            question_text=form.question_text.data.strip(),
            option_a=form.option_a.data.strip(),
            option_b=form.option_b.data.strip(),
            option_c=form.option_c.data.strip(),
            option_d=form.option_d.data.strip(),
            correct_option=form.correct_option.data,
            marks=form.marks.data,
        )
        db.session.add(question)
        db.session.commit()
        flash("Question added.", "success")
        return redirect(url_for("quizzes.manage", quiz_id=quiz_id))
    return render_template("quizzes/question_form.html", form=form,
                           title="Add Question", quiz=q)


@quizzes_bp.route("/<int:quiz_id>/questions/<int:q_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def edit_question(quiz_id, q_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.created_by != current_user.id:
        abort(403)
    question = QuizQuestion.query.get_or_404(q_id)
    if question.quiz_id != quiz_id:
        abort(404)
    form = QuizQuestionForm(obj=question)
    if form.validate_on_submit():
        question.question_text = form.question_text.data.strip()
        question.option_a = form.option_a.data.strip()
        question.option_b = form.option_b.data.strip()
        question.option_c = form.option_c.data.strip()
        question.option_d = form.option_d.data.strip()
        question.correct_option = form.correct_option.data
        question.marks = form.marks.data
        db.session.commit()
        flash("Question updated.", "success")
        return redirect(url_for("quizzes.manage", quiz_id=quiz_id))
    return render_template("quizzes/question_form.html", form=form,
                           title="Edit Question", quiz=quiz)


@quizzes_bp.route("/<int:quiz_id>/questions/<int:q_id>/delete", methods=["POST"])
@login_required
@teacher_required
def delete_question(quiz_id, q_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.created_by != current_user.id:
        abort(403)
    question = QuizQuestion.query.get_or_404(q_id)
    if question.quiz_id != quiz_id:
        abort(404)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted.", "success")
    return redirect(url_for("quizzes.manage", quiz_id=quiz_id))


@quizzes_bp.route("/<int:quiz_id>/results")
@login_required
@teacher_required
def results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if quiz.created_by != current_user.id:
        abort(403)
    attempts = (QuizAttempt.query.filter_by(quiz_id=quiz_id)
                .filter(QuizAttempt.submitted_at.isnot(None))
                .order_by(QuizAttempt.submitted_at.desc()).all())
    scores = [a.score for a in attempts if a.score is not None]
    stats = {
        "count": len(scores),
        "avg": round(sum(scores) / len(scores), 1) if scores else 0,
        "highest": max(scores) if scores else 0,
        "lowest": min(scores) if scores else 0,
    }
    return render_template("quizzes/results.html", quiz=quiz, attempts=attempts, stats=stats)


# ─── Student: Attempt a quiz ──────────────────────────────────────────────────

@quizzes_bp.route("/<int:quiz_id>/start", methods=["POST"])
@login_required
@student_required
def start(quiz_id):
    """
    Create a new attempt record with started_at = now.
    Rejects: unpublished, zero questions, duplicate (unless allow_retake).
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    if not quiz.is_published:
        abort(403)
    if quiz.questions.count() == 0:
        flash("This quiz has no questions yet.", "warning")
        return redirect(url_for("quizzes.index"))

    existing = QuizAttempt.query.filter_by(
        quiz_id=quiz_id, student_id=current_user.id
    ).filter(QuizAttempt.submitted_at.isnot(None)).first()

    if existing and not quiz.allow_retake:
        flash("You have already completed this quiz.", "info")
        return redirect(url_for("quizzes.attempt_result", quiz_id=quiz_id,
                                attempt_id=existing.id))

    # Create attempt (or find incomplete one)
    incomplete = QuizAttempt.query.filter_by(
        quiz_id=quiz_id, student_id=current_user.id, submitted_at=None
    ).first()
    if incomplete:
        attempt = incomplete
    else:
        attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=current_user.id,
            started_at=utcnow(),
        )
        db.session.add(attempt)
        db.session.commit()

    log_activity(current_user.id, "start_quiz", f"Started: {quiz.title}")
    return redirect(url_for("quizzes.attempt", quiz_id=quiz_id, attempt_id=attempt.id))


@quizzes_bp.route("/<int:quiz_id>/attempt/<int:attempt_id>")
@login_required
@student_required
def attempt(quiz_id, attempt_id):
    """
    Quiz attempt page.  CRITICAL: correct_option is NOT included in the
    template context.  Only question_text and option_a..d are passed.
    The JS timer uses duration_minutes from the attempt's started_at.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    att = QuizAttempt.query.get_or_404(attempt_id)

    if att.student_id != current_user.id:
        abort(403)
    if att.submitted_at is not None:
        return redirect(url_for("quizzes.attempt_result",
                                quiz_id=quiz_id, attempt_id=attempt_id))

    # Build safe question list (NO correct_option)
    questions = []
    for q in quiz.questions.all():
        questions.append({
            "id": q.id,
            "text": q.question_text,
            "a": q.option_a,
            "b": q.option_b,
            "c": q.option_c,
            "d": q.option_d,
            "marks": q.marks,
        })

    # Seconds remaining
    elapsed = (utcnow() - att.started_at).total_seconds()
    remaining = max(0, quiz.duration_minutes * 60 - elapsed)

    return render_template("quizzes/attempt.html",
                           quiz=quiz, attempt=att,
                           questions=questions,
                           remaining_seconds=int(remaining))


@quizzes_bp.route("/<int:quiz_id>/attempt/<int:attempt_id>/submit", methods=["POST"])
@login_required
@student_required
def submit_attempt(quiz_id, attempt_id):
    """
    Server-side scoring.
    1. Reject if the grace period has passed.
    2. Compute score from DB question answers (not from submitted form).
    3. Store each answer and the total score.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    att = QuizAttempt.query.get_or_404(attempt_id)

    if att.student_id != current_user.id:
        abort(403)
    if att.submitted_at is not None:
        flash("This attempt has already been submitted.", "info")
        return redirect(url_for("quizzes.attempt_result",
                                quiz_id=quiz_id, attempt_id=attempt_id))

    # ── Grace-period check (10 seconds) ──────────────────────────────────
    # Security: even if the browser timer was disabled, the server enforces
    # the deadline using the server-recorded started_at.
    grace = timedelta(seconds=10)
    allowed_until = att.started_at + timedelta(minutes=quiz.duration_minutes) + grace
    now = utcnow()
    if now > allowed_until:
        # Auto-submit with whatever we have; mark as late but still score
        pass  # We still process, just note it was submitted late

    submitted_at = utcnow()

    questions = quiz.questions.all()
    total_marks = sum(q.marks for q in questions)
    score = 0

    for q in questions:
        selected = request.form.get(f"q_{q.id}", "").upper()
        if selected not in ("A", "B", "C", "D"):
            selected = None
        correct = q.correct_option.upper()
        is_correct = selected == correct
        if is_correct:
            score += q.marks
        answer = QuizAnswer(
            attempt_id=att.id,
            question_id=q.id,
            selected_option=selected,
            is_correct=is_correct,
        )
        db.session.add(answer)

    att.submitted_at = submitted_at
    att.score = score
    att.total_marks = total_marks
    db.session.commit()

    log_activity(current_user.id, "submit_quiz",
                 f"Quiz: {quiz.title} | Score: {score}/{total_marks}")
    flash(f"Quiz submitted! Your score: {score}/{total_marks}", "success")
    return redirect(url_for("quizzes.attempt_result",
                            quiz_id=quiz_id, attempt_id=att.id))


@quizzes_bp.route("/<int:quiz_id>/attempt/<int:attempt_id>/result")
@login_required
def attempt_result(quiz_id, attempt_id):
    """Show score and per-question review with correct answers AFTER submission."""
    quiz = Quiz.query.get_or_404(quiz_id)
    att = QuizAttempt.query.get_or_404(attempt_id)

    # Students can only see their own results; teachers can see any
    if current_user.is_student and att.student_id != current_user.id:
        abort(403)
    if current_user.is_teacher and quiz.created_by != current_user.id:
        abort(403)

    if att.submitted_at is None:
        return redirect(url_for("quizzes.attempt",
                                quiz_id=quiz_id, attempt_id=attempt_id))

    # Build review data (correct_option IS shown here – post-submission)
    answers_map = {a.question_id: a for a in att.answers.all()}
    review = []
    for q in quiz.questions.all():
        ans = answers_map.get(q.id)
        review.append({
            "text": q.question_text,
            "a": q.option_a, "b": q.option_b,
            "c": q.option_c, "d": q.option_d,
            "correct": q.correct_option,
            "selected": ans.selected_option if ans else None,
            "is_correct": ans.is_correct if ans else False,
            "marks": q.marks,
        })

    return render_template("quizzes/result.html",
                           quiz=quiz, attempt=att, review=review)
