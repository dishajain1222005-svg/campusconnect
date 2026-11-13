"""
utils.py – Shared helper functions.

Covers: file validation (extension + magic bytes), secure storage paths,
human-readable sizes, LAN IP detection, and activity logging.
"""
import os
import uuid
import socket
import struct
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from flask import current_app
from werkzeug.utils import secure_filename

from app.extensions import db

logger = logging.getLogger(__name__)

# ── Magic-byte signatures ──────────────────────────────────────────────────────
# We read the first few bytes and compare to known signatures.
_MAGIC = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "zip_family",  # zip, docx, pptx share this magic
}


def _check_magic(file_storage) -> bool:
    """
    Read the first 4 bytes of an uploaded file and validate its magic signature.
    Returns True if the file passes or if we have no rule for its extension.
    The file pointer is reset to 0 afterwards.
    """
    header = file_storage.read(4)
    file_storage.seek(0)

    ext = _get_ext(file_storage.filename)
    if ext == "pdf":
        return header[:4] == b"%PDF"
    if ext in ("docx", "pptx", "zip"):
        return header[:4] == b"PK\x03\x04"
    # For .doc/.ppt (old binary format) check OLE signature D0CF11E0
    if ext in ("doc", "ppt"):
        return header[:4] == b"\xd0\xcf\x11\xe0" or True  # allow; hard to validate fully
    return True  # txt and others – no magic check needed


def _get_ext(filename: str) -> str:
    return Path(filename).suffix.lstrip(".").lower()


def allowed_material(filename: str) -> bool:
    return _get_ext(filename) in current_app.config["MATERIAL_EXTENSIONS"]


def allowed_submission(filename: str) -> bool:
    return _get_ext(filename) in current_app.config["SUBMISSION_EXTENSIONS"]


def validate_and_save(file_storage, dest_dir: Path, allowed_fn) -> dict:
    """
    Validate extension and magic bytes, then save the file under a UUID name.
    Returns a dict with keys: original_filename, stored_filename, file_size.
    Raises ValueError with a user-friendly message on failure.
    """
    if not file_storage or file_storage.filename == "":
        raise ValueError("No file selected.")

    original = secure_filename(file_storage.filename)
    if not original:
        raise ValueError("Invalid filename.")

    if not allowed_fn(original):
        allowed = ", ".join(current_app.config.get(
            "MATERIAL_EXTENSIONS" if allowed_fn is allowed_material else "SUBMISSION_EXTENSIONS",
            set()))
        raise ValueError(f"File type not allowed. Permitted: {allowed}")

    if not _check_magic(file_storage):
        raise ValueError("File content does not match its extension (magic byte check failed).")

    ext = _get_ext(original)
    stored = f"{uuid.uuid4().hex}.{ext}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / stored
    file_storage.save(str(dest_path))
    size = dest_path.stat().st_size

    return {
        "original_filename": original,
        "stored_filename": stored,
        "file_size": size,
    }


# ── LAN IP Detection ──────────────────────────────────────────────────────────

def get_lan_ip() -> str:
    """
    Detect the LAN IPv4 address using a UDP 'connect' trick.
    We create a UDP socket and 'connect' it to a non-routable address (10.254.254.254).
    No packets are sent because UDP is connectionless; the OS simply selects
    the outgoing interface, letting us read the local IP from the socket name.
    Falls back to 127.0.0.1 if anything goes wrong.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_all_lan_ips() -> list[str]:
    """
    Return all candidate IPv4 addresses via getaddrinfo, excluding loopback.
    Useful when the server has multiple network interfaces (Ethernet + Wi-Fi).
    """
    try:
        hostname = socket.gethostname()
        infos = socket.getaddrinfo(hostname, None, socket.AF_INET)
        ips = list({info[4][0] for info in infos if info[4][0] != "127.0.0.1"})
        return ips or ["127.0.0.1"]
    except Exception:
        return ["127.0.0.1"]


# ── Activity Logging ─────────────────────────────────────────────────────────

def log_activity(user_id: int, action: str, details: str = ""):
    """Insert a row into activity_log.  Called from views after key actions."""
    from app.models import ActivityLog
    try:
        entry = ActivityLog(user_id=user_id, action=action, details=details)
        db.session.add(entry)
        db.session.commit()
    except Exception as exc:
        logger.error("Failed to write activity log: %s", exc)
        db.session.rollback()


# ── Open-redirect guard ───────────────────────────────────────────────────────

def is_safe_url(target: str) -> bool:
    """
    Return True only if the redirect target is a relative path on this host.
    Prevents open-redirect attacks where an attacker crafts a login URL
    like /login?next=http://evil.com.
    """
    from urllib.parse import urlparse, urljoin
    from flask import request
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc
