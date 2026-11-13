"""
conftest.py – pytest fixtures shared across all test modules.

We use Flask's test client with a temporary in-memory SQLite DB.
CSRF is disabled in TestingConfig so forms can be POST-ed without tokens.

Context management: Flask 3.x's test client pushes its own app context.
We must NOT nest a second `with app.app_context()` inside tests that
already use the client fixture — that causes "Popped wrong app context".
Instead, the `ctx` fixture provides one per-test context, and all DB
operations use that same context.
"""
import io
import pytest
from pathlib import Path
from app import create_app
from app.extensions import db as _db
from config import TestingConfig


@pytest.fixture(scope="session")
def app():
    application = create_app(TestingConfig)
    for d in (application.config["MATERIAL_UPLOAD_DIR"],
              application.config["ASSIGNMENT_REF_DIR"],
              application.config["SUBMISSION_DIR"]):
        Path(d).mkdir(parents=True, exist_ok=True)
    yield application
    import shutil
    for d in (application.config["MATERIAL_UPLOAD_DIR"],
              application.config["ASSIGNMENT_REF_DIR"],
              application.config["SUBMISSION_DIR"]):
        if Path(d).exists():
            shutil.rmtree(str(d))


@pytest.fixture(scope="session")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def ctx(app, db):
    """Push a single app context for the whole test function.
    The test client will reuse this context instead of creating a new one."""
    with app.app_context():
        yield


@pytest.fixture(scope="function")
def client(app, ctx):
    """Test client that shares the ctx fixture's app context."""
    with app.test_client() as c:
        yield c


# ── User helpers (call inside a ctx/app_context) ──────────────────────────────

def make_student(username="stu1", password="password123",
                 email=None, full_name="Student One"):
    from app.extensions import db
    from app.models import User
    u = User(full_name=full_name, username=username,
             email=email or f"{username}@test.com", role="student")
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u


def make_teacher(username="tea1", password="password123",
                 email=None, full_name="Teacher One"):
    from app.extensions import db
    from app.models import User
    u = User(full_name=full_name, username=username,
             email=email or f"{username}@test.com", role="teacher")
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u


def login(client, username, password):
    return client.post("/login", data={"username": username, "password": password},
                       follow_redirects=True)


def logout(client):
    return client.get("/logout", follow_redirects=True)


def fake_pdf(name="test.pdf"):
    content = b"%PDF-1.4 1 0 obj<</Type /Catalog>>endobj\n%%EOF"
    return (io.BytesIO(content), name)


def fake_txt(name="test.txt"):
    return (io.BytesIO(b"This is a test submission."), name)
