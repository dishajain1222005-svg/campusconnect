"""test_assignments.py – Assignment lifecycle tests."""
import io
import pytest
from datetime import datetime, timezone, timedelta
from tests.conftest import make_student, make_teacher, login, logout


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TestAssignments:
    def _create_assignment(self, teacher, days=7):
        from app.models import Assignment
        from app.extensions import db
        a = Assignment(
            title="Test Assignment",
            description="Submit your work",
            subject="Networks",
            deadline=utcnow() + timedelta(days=days),
            created_by=teacher.id,
        )
        db.session.add(a)
        db.session.commit()
        return a

    def _create_past_assignment(self, teacher):
        from app.models import Assignment
        from app.extensions import db
        a = Assignment(
            title="Past Assignment",
            description="Overdue",
            subject="Networks",
            deadline=utcnow() - timedelta(days=1),
            created_by=teacher.id,
        )
        db.session.add(a)
        db.session.commit()
        return a

    def _submit(self, client, assignment_id, filename="sub.txt", content=b"my work"):
        return client.post(f"/assignments/{assignment_id}/submit", data={
            "file": (io.BytesIO(content), filename),
        }, content_type="multipart/form-data", follow_redirects=True)

    def test_pending_status(self, client, ctx):
        tea = make_teacher(username="asn_tea1", email="asn_tea1@test.com")
        make_student(username="asn_stu1", email="asn_stu1@test.com")
        self._create_assignment(tea)
        login(client, "asn_stu1", "password123")
        resp = client.get("/assignments/", follow_redirects=True)
        assert resp.status_code == 200
        assert b"Pending" in resp.data
        logout(client)

    def test_submitted_on_time_status(self, client, ctx):
        from app.models import AssignmentSubmission
        tea = make_teacher(username="asn_tea2", email="asn_tea2@test.com")
        stu = make_student(username="asn_stu2", email="asn_stu2@test.com")
        a = self._create_assignment(tea)
        login(client, "asn_stu2", "password123")
        self._submit(client, a.id)
        sub = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stu.id).first()
        assert sub is not None
        assert sub.status == "Submitted"
        assert sub.is_late is False
        logout(client)

    def test_late_status(self, client, ctx):
        from app.models import AssignmentSubmission
        tea = make_teacher(username="asn_tea3", email="asn_tea3@test.com")
        stu = make_student(username="asn_stu3", email="asn_stu3@test.com")
        a = self._create_past_assignment(tea)
        login(client, "asn_stu3", "password123")
        self._submit(client, a.id)
        sub = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stu.id).first()
        assert sub is not None
        assert sub.is_late is True
        assert sub.status == "Late"
        logout(client)

    def test_resubmission_replaces_file(self, client, ctx):
        from app.models import AssignmentSubmission
        tea = make_teacher(username="asn_tea4", email="asn_tea4@test.com")
        stu = make_student(username="asn_stu4", email="asn_stu4@test.com")
        a = self._create_assignment(tea)
        login(client, "asn_stu4", "password123")
        self._submit(client, a.id, "first.txt", b"first attempt")
        sub1 = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stu.id).first()
        first_stored = sub1.stored_filename
        self._submit(client, a.id, "second.txt", b"second attempt")
        # Must still be exactly one submission row
        count = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stu.id).count()
        assert count == 1
        sub2 = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stu.id).first()
        assert sub2.stored_filename != first_stored
        logout(client)

    def test_student_cannot_download_other_students_submission(self, client, ctx):
        from app.models import AssignmentSubmission
        tea = make_teacher(username="asn_tea5", email="asn_tea5@test.com")
        stuA = make_student(username="asn_stuA", email="asn_stuA@test.com")
        make_student(username="asn_stuB", email="asn_stuB@test.com")
        a = self._create_assignment(tea)
        login(client, "asn_stuA", "password123")
        self._submit(client, a.id)
        sub = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stuA.id).first()
        logout(client)
        login(client, "asn_stuB", "password123")
        resp = client.get(f"/assignments/download/submission/{sub.id}",
                          follow_redirects=False)
        assert resp.status_code == 403
        logout(client)

    def test_teacher_downloads_own_assignment_submission(self, client, ctx):
        from app.models import AssignmentSubmission
        tea = make_teacher(username="asn_tea6", email="asn_tea6@test.com")
        stu = make_student(username="asn_stu6", email="asn_stu6@test.com")
        a = self._create_assignment(tea)
        login(client, "asn_stu6", "password123")
        self._submit(client, a.id, "work.txt", b"my actual work here submitted")
        sub = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stu.id).first()
        logout(client)
        login(client, "asn_tea6", "password123")
        resp = client.get(f"/assignments/download/submission/{sub.id}")
        assert resp.status_code == 200
        logout(client)

    def test_teacher_cannot_download_other_teachers_submissions(self, client, ctx):
        from app.models import AssignmentSubmission
        tea1 = make_teacher(username="asn_tea7", email="asn_tea7@test.com")
        make_teacher(username="asn_tea8", email="asn_tea8@test.com")
        stu = make_student(username="asn_stu7", email="asn_stu7@test.com")
        a = self._create_assignment(tea1)
        login(client, "asn_stu7", "password123")
        self._submit(client, a.id)
        sub = AssignmentSubmission.query.filter_by(
            assignment_id=a.id, student_id=stu.id).first()
        logout(client)
        login(client, "asn_tea8", "password123")
        resp = client.get(f"/assignments/download/submission/{sub.id}",
                          follow_redirects=False)
        assert resp.status_code == 403
        logout(client)
