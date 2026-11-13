"""
config.py – CampusConnect application configuration.

Networking concept: The HOST/PORT settings control which network interface
Flask binds to. 0.0.0.0 means "listen on ALL interfaces" (including the LAN
adapter), so other devices on the same Wi-Fi can reach the server.
"""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

STORAGE_DIR = BASE_DIR / "storage"


def _get_or_create_secret_key() -> str:
    """
    Read the secret key from instance/secret_key, creating it on first run.
    This persists the key across restarts so existing sessions remain valid.
    Never hardcode a secret key in source code.
    """
    key_file = INSTANCE_DIR / "secret_key"
    if key_file.exists():
        return key_file.read_text().strip()
    key = secrets.token_hex(32)
    key_file.write_text(key)
    return key


class Config:
    # ── Security ──────────────────────────────────────────────────────────
    SECRET_KEY: str = os.environ.get("CAMPUS_SECRET_KEY") or _get_or_create_secret_key()

    # ── Database ──────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI: str = (
        f"sqlite:///{INSTANCE_DIR / 'campusconnect.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ── File uploads ──────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH: int = 25 * 1024 * 1024  # 25 MB

    MATERIAL_EXTENSIONS: set = {"pdf", "ppt", "pptx", "doc", "docx"}
    SUBMISSION_EXTENSIONS: set = {"pdf", "doc", "docx", "zip", "txt"}

    STORAGE_DIR: Path = STORAGE_DIR
    MATERIAL_UPLOAD_DIR: Path = STORAGE_DIR / "materials"
    ASSIGNMENT_REF_DIR: Path = STORAGE_DIR / "assignments"
    SUBMISSION_DIR: Path = STORAGE_DIR / "submissions"

    # ── Session / Cookie ──────────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    SESSION_COOKIE_SECURE: bool = False  # Plain HTTP on LAN; never set True here

    # ── Network ───────────────────────────────────────────────────────────
    HOST: str = os.environ.get("CAMPUS_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("CAMPUS_PORT", 5000))

    # ── Logging ───────────────────────────────────────────────────────────
    LOG_FILE: Path = INSTANCE_DIR / "campusconnect.log"


class TestingConfig(Config):
    TESTING: bool = True
    WTF_CSRF_ENABLED: bool = False
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SECRET_KEY: str = "test-secret-key-not-for-production"
    MATERIAL_UPLOAD_DIR: Path = STORAGE_DIR / "test_materials"
    ASSIGNMENT_REF_DIR: Path = STORAGE_DIR / "test_assignments"
    SUBMISSION_DIR: Path = STORAGE_DIR / "test_submissions"
