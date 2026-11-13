# CampusConnect – Architecture

## Overview

CampusConnect uses a **client-server architecture** over a local area network (LAN).

```
┌─────────────────────────────────────────────────────────────┐
│                    LOCAL Wi-Fi NETWORK                       │
│  (router / Windows hotspot / phone hotspot, NO internet)    │
│                                                             │
│  ┌────────────┐    HTTP/TCP     ┌──────────────────────┐   │
│  │  Student   │ ◄────────────► │                      │   │
│  │  (Phone/   │                │   Server Laptop       │   │
│  │  Laptop)   │                │   Windows 11          │   │
│  └────────────┘                │                      │   │
│                                │   Python 3 + Flask   │   │
│  ┌────────────┐    HTTP/TCP    │   Port 5000           │   │
│  │  Teacher   │ ◄────────────► │   0.0.0.0 (all NICs) │   │
│  │  (Laptop)  │                │                      │   │
│  └────────────┘                │   SQLite DB          │   │
│                                │   File storage       │   │
│                                └──────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Technology stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| Web framework | Flask 3 (application factory + blueprints) |
| ORM | SQLAlchemy 2 via Flask-SQLAlchemy |
| Database | SQLite (WAL mode) |
| Auth | Flask-Login + Werkzeug password hashing |
| Forms | Flask-WTF + WTForms (CSRF protection) |
| Migrations | Flask-Migrate (Alembic) |
| WSGI (optional) | Waitress |
| Frontend | Bootstrap 5, Bootstrap Icons (both local), vanilla JS |

## Application structure

```
app/
├── __init__.py          ← create_app() factory
├── extensions.py        ← db, login_manager, migrate, csrf
├── models.py            ← all SQLAlchemy models
├── decorators.py        ← @teacher_required, @student_required
├── utils.py             ← file validation, LAN IP detection, logging
├── cli.py               ← flask create-teacher command
├── auth/                ← login, register, logout
├── student/             ← student dashboard
├── teacher/             ← teacher dashboard
├── materials/           ← upload, download, delete study files
├── assignments/         ← create, submit, review assignments
├── notices/             ← notice board CRUD
├── quizzes/             ← quiz builder + timed attempt engine
├── profile/             ← edit profile, change password
└── network/             ← server status page
```

## Request flow: File Upload

```
Browser                Flask                  Disk
───────                ─────                  ────
POST /materials/upload
  multipart/form-data
        │
        ▼
  CSRF token check (Flask-WTF)
        │
        ▼
  @teacher_required decorator
        │
        ▼
  validate_and_save()
  ├─ check extension
  ├─ check magic bytes
  ├─ generate UUID filename
  └─ save to storage/materials/   ──────────► UUID.pdf written
        │
        ▼
  DB row inserted (StudyMaterial)
  original_filename = "lecture.pdf"
  stored_filename   = "a3f9c2...pdf"
        │
        ▼
  flash("Uploaded") + redirect
```

## Request flow: File Download

```
Browser                Flask                  Disk
───────                ─────                  ────
GET /materials/download/42
        │
        ▼
  @login_required
        │
        ▼
  DB lookup: SELECT * FROM study_material WHERE id=42
        │
        ▼
  send_from_directory(
    storage/materials/,
    stored_filename,         ← from DB, never from URL
    download_name=original   ← shown to browser
  )                                            ──────► reads UUID.pdf
        │
        ▼
  HTTP 200 with Content-Disposition: attachment
```

## TCP/IP and HTTP

- HTTP runs on top of TCP/IP.
- TCP ensures reliable, ordered delivery of bytes.
- IP routes packets between devices using IP addresses.
- Flask binds a **listening socket** to `0.0.0.0:5000` — this means it
  accepts incoming TCP connections on port 5000 from any network interface.
- Each HTTP request is one TCP connection (HTTP/1.1 may keep-alive).
- The browser is the **client**, Flask is the **server**.

## SQLite WAL mode

Write-Ahead Logging (WAL) allows multiple readers to operate while a write
is in progress. This prevents "database is locked" errors when several
students load pages simultaneously.

```python
@event.listens_for(Engine, "connect")
def set_wal_mode(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
```
