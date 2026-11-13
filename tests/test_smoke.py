"""
test_smoke.py – Smoke tests: every page returns 200 with no crashes.
Also: no CDN URLs in templates, data persists across contexts.
"""
import re
import pytest
from pathlib import Path
from tests.conftest import make_student, make_teacher, login, logout


class TestSmoke:
    def test_login_page_loads(self, client, ctx):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"CampusConnect" in resp.data

    def test_register_page_loads(self, client, ctx):
        resp = client.get("/register")
        assert resp.status_code == 200

    def test_root_redirects(self, client, ctx):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302

    def test_student_pages(self, client, ctx):
        make_student(username="smoke_stu", email="smoke_stu@test.com")
        login(client, "smoke_stu", "password123")
        pages = [
            "/student/dashboard",
            "/materials/",
            "/assignments/",
            "/notices/",
            "/quizzes/",
            "/profile/",
            "/network/",
        ]
        for p in pages:
            resp = client.get(p, follow_redirects=True)
            assert resp.status_code == 200, \
                f"Student page {p} returned {resp.status_code}"
        logout(client)

    def test_teacher_pages(self, client, ctx):
        make_teacher(username="smoke_tea", email="smoke_tea@test.com")
        login(client, "smoke_tea", "password123")
        pages = [
            "/teacher/dashboard",
            "/materials/",
            "/materials/upload",
            "/assignments/",
            "/assignments/create",
            "/notices/",
            "/notices/create",
            "/quizzes/",
            "/quizzes/create",
            "/profile/",
            "/network/",
        ]
        for p in pages:
            resp = client.get(p, follow_redirects=True)
            assert resp.status_code == 200, \
                f"Teacher page {p} returned {resp.status_code}"
        logout(client)

    def test_404_page(self, client, ctx):
        make_student(username="err_stu", email="err_stu@test.com")
        login(client, "err_stu", "password123")
        resp = client.get("/nonexistent-route-xyz-abc")
        assert resp.status_code == 404
        assert b"404" in resp.data
        logout(client)

    def test_403_page(self, client, ctx):
        make_student(username="err_stu2", email="err_stu2@test.com")
        login(client, "err_stu2", "password123")
        resp = client.get("/materials/upload")
        assert resp.status_code == 403
        logout(client)


class TestNoCDN:
    """Verify no external resource URLs in any template."""

    def test_no_cdn_links_in_templates(self):
        templates_dir = Path(__file__).parent.parent / "app" / "templates"
        # Match http(s):// URLs that point to known CDN domains
        # Exclude: xmlns declarations (SVG/XML namespaces, not network requests)
        cdn_pattern = re.compile(
            r'(?:src|href)\s*=\s*["\']https?://',
            re.IGNORECASE
        )
        violations = []
        for tmpl in templates_dir.rglob("*.html"):
            content = tmpl.read_text(encoding="utf-8")
            if cdn_pattern.search(content):
                violations.append(str(tmpl.name))

        assert not violations, \
            f"Templates with external src/href found (CDN dependency!):\n" + \
            "\n".join(violations)

    def test_bootstrap_css_exists_locally(self):
        p = Path(__file__).parent.parent / "app" / "static" / "vendor" / \
            "bootstrap" / "css" / "bootstrap.min.css"
        assert p.exists(), "Bootstrap CSS not found locally"
        assert p.stat().st_size > 100_000

    def test_bootstrap_js_exists_locally(self):
        p = Path(__file__).parent.parent / "app" / "static" / "vendor" / \
            "bootstrap" / "js" / "bootstrap.bundle.min.js"
        assert p.exists(), "Bootstrap JS not found locally"
        assert p.stat().st_size > 50_000

    def test_bootstrap_icons_exists_locally(self):
        p = Path(__file__).parent.parent / "app" / "static" / "vendor" / \
            "bootstrap-icons" / "css" / "bootstrap-icons.min.css"
        assert p.exists(), "Bootstrap Icons CSS not found locally"


class TestPersistence:
    """Data must survive across separate app contexts (simulates server restart)."""

    def test_user_persists(self, app, db):
        with app.app_context():
            from app.extensions import db as ext_db
            from app.models import User
            u = User(full_name="Persist Test", username="persist_u",
                     email="persist@test.com", role="student")
            u.set_password("persist123")
            ext_db.session.add(u)
            ext_db.session.commit()
            uid = u.id

        with app.app_context():
            from app.models import User
            from app.extensions import db as ext_db
            found = ext_db.session.get(User, uid)
            assert found is not None
            assert found.username == "persist_u"
            assert found.check_password("persist123")
