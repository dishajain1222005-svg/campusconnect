"""test_rbac.py – Role-based access control tests."""
import pytest
from tests.conftest import make_student, make_teacher, login, logout

# Network is accessible to both roles (login_required only)
TEACHER_ONLY_ROUTES = [
    "/materials/upload",
    "/assignments/create",
    "/notices/create",
    "/quizzes/create",
]

STUDENT_ONLY_ROUTES = [
    "/student/dashboard",
]


class TestRBAC:
    def test_student_cannot_access_teacher_only_routes(self, client, ctx):
        make_student(username="rbac_stu", email="rbac_stu@test.com")
        login(client, "rbac_stu", "password123")
        for route in TEACHER_ONLY_ROUTES:
            resp = client.get(route, follow_redirects=False)
            assert resp.status_code in (302, 403), \
                f"Expected 302 or 403 for {route}, got {resp.status_code}"
        logout(client)

    def test_teacher_cannot_access_student_dashboard(self, client, ctx):
        make_teacher(username="rbac_tea", email="rbac_tea@test.com")
        login(client, "rbac_tea", "password123")
        resp = client.get("/student/dashboard", follow_redirects=False)
        assert resp.status_code in (302, 403)
        logout(client)

    def test_unauthenticated_blocked_from_all_protected(self, client, ctx):
        protected = [
            "/student/dashboard",
            "/teacher/dashboard",
            "/materials/",
            "/assignments/",
            "/notices/",
            "/quizzes/",
            "/profile/",
            "/network/",
        ]
        for route in protected:
            resp = client.get(route, follow_redirects=False)
            assert resp.status_code == 302, \
                f"Expected redirect for {route}, got {resp.status_code}"
            assert "/login" in resp.headers.get("Location", ""), \
                f"Expected redirect to login for {route}"

    def test_path_traversal_download_blocked(self, client, ctx):
        make_student(username="traversal_stu", email="traversal@test.com")
        login(client, "traversal_stu", "password123")
        resp = client.get("/materials/download/9999999")
        assert resp.status_code == 404
        logout(client)
