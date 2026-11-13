"""test_auth.py – Authentication and registration tests."""
import pytest
from app.models import User
from tests.conftest import make_student, make_teacher, login, logout


class TestRegistration:
    def test_register_student_ok(self, client, ctx):
        resp = client.post("/register", data={
            "full_name": "Alice Smith",
            "username": "alice",
            "email": "alice@test.com",
            "roll_no": "21CS001",
            "department": "CS",
            "password": "securepass1",
            "password2": "securepass1",
        }, follow_redirects=True)
        assert resp.status_code == 200
        u = User.query.filter_by(username="alice").first()
        assert u is not None
        assert u.role == "student"

    def test_register_cannot_set_teacher_role(self, client, ctx):
        """Even if role=teacher injected into POST, role must remain student."""
        resp = client.post("/register", data={
            "full_name": "Evil Teacher",
            "username": "evil_tea",
            "email": "evil@test.com",
            "password": "securepass1",
            "password2": "securepass1",
            "role": "teacher",   # injected – must be ignored
        }, follow_redirects=True)
        assert resp.status_code == 200
        u = User.query.filter_by(username="evil_tea").first()
        if u:
            assert u.role == "student", "Role must always be student from registration"

    def test_duplicate_username_rejected(self, client, ctx):
        make_student(username="dupuser", email="dup@test.com")
        resp = client.post("/register", data={
            "full_name": "Dup User",
            "username": "dupuser",
            "email": "dup2@test.com",
            "password": "securepass1",
            "password2": "securepass1",
        })
        assert resp.status_code == 200
        assert b"already taken" in resp.data

    def test_short_password_rejected(self, client, ctx):
        resp = client.post("/register", data={
            "full_name": "Short Pass",
            "username": "shortpass",
            "email": "short@test.com",
            "password": "abc",
            "password2": "abc",
        })
        assert resp.status_code == 200
        assert User.query.filter_by(username="shortpass").first() is None

    def test_password_stored_hashed(self, client, ctx):
        resp = client.post("/register", data={
            "full_name": "Hash Test",
            "username": "hashtest",
            "email": "hash@test.com",
            "password": "mypassword1",
            "password2": "mypassword1",
        }, follow_redirects=True)
        u = User.query.filter_by(username="hashtest").first()
        assert u is not None
        assert u.password_hash != "mypassword1"
        assert len(u.password_hash) > 20
        assert u.check_password("mypassword1") is True


class TestLogin:
    def test_unauthenticated_redirects_to_login(self, client, ctx):
        for path in ["/materials/", "/assignments/", "/notices/", "/quizzes/"]:
            resp = client.get(path, follow_redirects=False)
            assert resp.status_code == 302
            assert "/login" in resp.headers["Location"]

    def test_login_wrong_password(self, client, ctx):
        make_student(username="logintest", email="logintest@test.com")
        resp = client.post("/login", data={
            "username": "logintest", "password": "wrongpass"
        }, follow_redirects=True)
        assert b"Invalid username or password" in resp.data

    def test_login_nonexistent_user_generic_error(self, client, ctx):
        resp = client.post("/login", data={
            "username": "nosuchuser99999", "password": "whatever"
        }, follow_redirects=True)
        assert b"Invalid username or password" in resp.data
        # The form re-fills the username field – that's acceptable behaviour;
        # what matters is no message reveals whether the account exists
        assert b"does not exist" not in resp.data
        assert b"not found" not in resp.data

    def test_student_login_redirects_to_student_dashboard(self, client, ctx):
        make_student(username="stu_login", email="stulogin@test.com")
        resp = login(client, "stu_login", "password123")
        assert resp.status_code == 200
        assert b"Dashboard" in resp.data
        logout(client)

    def test_teacher_login_redirects_to_teacher_dashboard(self, client, ctx):
        make_teacher(username="tea_login", email="tealogin@test.com")
        resp = login(client, "tea_login", "password123")
        assert resp.status_code == 200
        assert b"Dashboard" in resp.data
        logout(client)

    def test_logout(self, client, ctx):
        make_student(username="stu_logout", email="stulogout@test.com")
        login(client, "stu_logout", "password123")
        resp = logout(client)
        assert resp.status_code == 200
        resp2 = client.get("/student/dashboard", follow_redirects=False)
        assert resp2.status_code == 302
