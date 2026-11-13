"""test_quizzes.py – Quiz security and scoring tests."""
import pytest
from datetime import datetime, timezone, timedelta
from tests.conftest import make_student, make_teacher, login, logout


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _make_quiz(teacher, published=True, allow_retake=False, duration=30):
    from app.models import Quiz, QuizQuestion
    from app.extensions import db
    q = Quiz(
        title="Test Quiz", subject="Networks",
        duration_minutes=duration,
        is_published=published,
        allow_retake=allow_retake,
        created_by=teacher.id,
    )
    db.session.add(q)
    db.session.flush()
    db.session.add_all([
        QuizQuestion(quiz_id=q.id, question_text="1+1=?",
                     option_a="1", option_b="2", option_c="3", option_d="4",
                     correct_option="B", marks=1),
        QuizQuestion(quiz_id=q.id, question_text="Capital of France?",
                     option_a="Berlin", option_b="London", option_c="Paris", option_d="Rome",
                     correct_option="C", marks=2),
        QuizQuestion(quiz_id=q.id, question_text="HTTP default port?",
                     option_a="21", option_b="22", option_c="80", option_d="443",
                     correct_option="C", marks=1),
    ])
    db.session.commit()
    return q


class TestQuizSecurity:

    def test_correct_answers_not_in_attempt_html(self, client, ctx):
        """CRITICAL: attempt page must not expose correct_option to the browser."""
        tea = make_teacher(username="qz_tea1", email="qz_tea1@test.com")
        make_student(username="qz_stu1", email="qz_stu1@test.com")
        q = _make_quiz(tea)
        login(client, "qz_stu1", "password123")
        resp = client.post(f"/quizzes/{q.id}/start", follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "correct_option" not in html, \
            "correct_option MUST NOT appear in attempt page HTML"
        assert 'name="correct"' not in html
        # Question text should be present
        assert "1+1=?" in html
        logout(client)

    def test_score_computed_correctly(self, client, ctx):
        from app.models import QuizAttempt, QuizQuestion
        tea = make_teacher(username="qz_tea2", email="qz_tea2@test.com")
        stu = make_student(username="qz_stu2", email="qz_stu2@test.com")
        quiz = _make_quiz(tea)
        questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        login(client, "qz_stu2", "password123")
        client.post(f"/quizzes/{quiz.id}/start", follow_redirects=True)
        att = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=stu.id).first()
        # Submit all correct
        data = {f"q_{q.id}": q.correct_option for q in questions}
        client.post(f"/quizzes/{quiz.id}/attempt/{att.id}/submit",
                    data=data, follow_redirects=True)
        from app.extensions import db
        db.session.expire(att)
        att = db.session.get(QuizAttempt, att.id)
        expected = sum(q.marks for q in questions)  # 1+2+1=4
        assert att.score == expected
        assert att.total_marks == expected
        logout(client)

    def test_score_zero_all_wrong(self, client, ctx):
        from app.models import QuizAttempt, QuizQuestion
        tea = make_teacher(username="qz_tea3", email="qz_tea3@test.com")
        stu = make_student(username="qz_stu3", email="qz_stu3@test.com")
        quiz = _make_quiz(tea)
        questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        login(client, "qz_stu3", "password123")
        client.post(f"/quizzes/{quiz.id}/start", follow_redirects=True)
        att = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=stu.id).first()
        # Option A is wrong for all three (correct: B, C, C)
        data = {f"q_{q.id}": "A" for q in questions}
        client.post(f"/quizzes/{quiz.id}/attempt/{att.id}/submit",
                    data=data, follow_redirects=True)
        from app.extensions import db
        db.session.expire(att)
        att = db.session.get(QuizAttempt, att.id)
        assert att.score == 0
        logout(client)

    def test_duplicate_attempt_blocked(self, client, ctx):
        from app.models import QuizAttempt, QuizQuestion
        tea = make_teacher(username="qz_tea4", email="qz_tea4@test.com")
        stu = make_student(username="qz_stu4", email="qz_stu4@test.com")
        quiz = _make_quiz(tea, allow_retake=False)
        questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        login(client, "qz_stu4", "password123")
        # First complete attempt
        client.post(f"/quizzes/{quiz.id}/start", follow_redirects=True)
        att = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=stu.id).first()
        data = {f"q_{q.id}": q.correct_option for q in questions}
        client.post(f"/quizzes/{quiz.id}/attempt/{att.id}/submit",
                    data=data, follow_redirects=True)
        # Try to start again
        client.post(f"/quizzes/{quiz.id}/start", follow_redirects=True)
        count = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=stu.id).count()
        assert count == 1, f"Expected 1 attempt row, got {count}"
        logout(client)

    def test_unpublished_quiz_blocked(self, client, ctx):
        tea = make_teacher(username="qz_tea5", email="qz_tea5@test.com")
        make_student(username="qz_stu5", email="qz_stu5@test.com")
        quiz = _make_quiz(tea, published=False)
        login(client, "qz_stu5", "password123")
        resp = client.post(f"/quizzes/{quiz.id}/start", follow_redirects=False)
        assert resp.status_code in (302, 403), \
            f"Unpublished quiz should be blocked, got {resp.status_code}"
        logout(client)

    def test_zero_question_quiz_cannot_start(self, client, ctx):
        from app.models import Quiz
        from app.extensions import db
        tea = make_teacher(username="qz_tea6", email="qz_tea6@test.com")
        make_student(username="qz_stu6", email="qz_stu6@test.com")
        q = Quiz(title="Empty Quiz", subject="Math",
                 duration_minutes=10, is_published=True,
                 created_by=tea.id)
        db.session.add(q)
        db.session.commit()
        login(client, "qz_stu6", "password123")
        resp = client.post(f"/quizzes/{q.id}/start", follow_redirects=True)
        assert resp.status_code == 200
        assert b"question" in resp.data.lower()
        logout(client)

    def test_late_submission_still_processed(self, client, ctx):
        """Server accepts a late submission but records it normally."""
        from app.models import QuizAttempt, QuizQuestion
        from app.extensions import db
        tea = make_teacher(username="qz_tea7", email="qz_tea7@test.com")
        stu = make_student(username="qz_stu7", email="qz_stu7@test.com")
        quiz = _make_quiz(tea, duration=30)
        questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        login(client, "qz_stu7", "password123")
        client.post(f"/quizzes/{quiz.id}/start", follow_redirects=True)
        att = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=stu.id).first()
        # Backdate started_at past the grace window
        att.started_at = utcnow() - timedelta(minutes=35)
        db.session.commit()
        data = {f"q_{q.id}": q.correct_option for q in questions}
        resp = client.post(f"/quizzes/{quiz.id}/attempt/{att.id}/submit",
                           data=data, follow_redirects=True)
        assert resp.status_code == 200
        db.session.expire(att)
        att = db.session.get(QuizAttempt, att.id)
        assert att.submitted_at is not None
        logout(client)

    def test_student_cannot_see_other_students_result(self, client, ctx):
        from app.models import QuizAttempt, QuizQuestion
        tea = make_teacher(username="qz_tea8", email="qz_tea8@test.com")
        stuA = make_student(username="qz_stuA", email="qz_stuA@test.com")
        make_student(username="qz_stuB", email="qz_stuB@test.com")
        quiz = _make_quiz(tea)
        questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
        login(client, "qz_stuA", "password123")
        client.post(f"/quizzes/{quiz.id}/start", follow_redirects=True)
        att = QuizAttempt.query.filter_by(quiz_id=quiz.id, student_id=stuA.id).first()
        data = {f"q_{q.id}": q.correct_option for q in questions}
        client.post(f"/quizzes/{quiz.id}/attempt/{att.id}/submit",
                    data=data, follow_redirects=True)
        logout(client)
        login(client, "qz_stuB", "password123")
        resp = client.get(f"/quizzes/{quiz.id}/attempt/{att.id}/result",
                          follow_redirects=False)
        assert resp.status_code == 403
        logout(client)
