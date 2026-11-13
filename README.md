# 🎓 CampusConnect

> An offline LAN-based academic platform — runs on one laptop, serves an entire classroom over Wi-Fi. Zero internet required after setup.

---

## ✨ Features

| Feature | Students | Teachers |
|---|---|---|
| 📚 Study Materials | Download PDFs, slides, docs | Upload, manage, delete |
| 📝 Assignments | View, submit, resubmit | Create, set deadlines, download submissions |
| 📢 Notice Board | Read, search notices | Post, pin important notices |
| 🧠 Quizzes | Timed MCQ attempts, instant results | Build questions, publish, view statistics |
| 👤 Profile | Edit info, change password | Same |
| 📡 Network Status | View server URL | Full activity log, active users |

---

## 🖥️ Screenshots

> **Login Page**

Split-screen design with campus illustration and feature list on the left, clean sign-in form on the right.

> **Teacher Dashboard**

Header with search bar, campus hero banner, stat cards (Students / Materials / Assignments / Notices / Quizzes), quick actions, recent submissions, and live activity log.

> **Study Materials**

Searchable, filterable table with file type icons, upload and delete for teachers, authenticated download for everyone.

---

## 🚀 Quick Start

### Requirements
- Windows 11
- Python 3.10+
- All other devices just need a browser

### Install

```bat
git clone https://github.com/YOUR_USERNAME/campusconnect.git
cd campusconnect

py -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

### First run

```bat
set FLASK_APP=run.py

rem Create a teacher account (CLI only — cannot be done via web form)
flask create-teacher

rem Start the server
python run.py
```

The startup banner prints your LAN URL:

```
Open on other devices:
→ http://192.168.x.x:5000
```

Students and teachers open that URL in any browser on the same Wi-Fi.

### More stable server (optional)

```bat
python run.py --waitress
```

---

## 🌐 LAN Setup

1. Connect all devices to the **same Wi-Fi** (router, Windows hotspot, or phone hotspot)
2. Run `scripts\show_ip.bat` to find the server's IP address
3. Add a Windows Firewall rule (run as Administrator):

```powershell
New-NetFirewallRule -DisplayName "CampusConnect-Port-5000" `
    -Direction Inbound -Protocol TCP -LocalPort 5000 `
    -Action Allow -Profile Private -RemoteAddress LocalSubnet
```

4. Students open `http://SERVER_IP:5000` in their browser

Full guide: [`docs/LAN_SETUP.md`](docs/LAN_SETUP.md)

---

## 🔐 Security Notes

- Passwords hashed with **pbkdf2:sha256** (Werkzeug)
- **CSRF protection** on every POST form
- Files stored under **random UUID names** — never served by filename from URL
- **Magic-byte validation** on uploads
- Teacher role can **only** be created via `flask create-teacher` CLI — never from the registration form
- Quiz correct answers are **never sent to the browser** before submission — scored entirely server-side

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Flask 3 (application factory + blueprints) |
| Database | SQLite (WAL mode) |
| ORM | SQLAlchemy 2 |
| Auth | Flask-Login + Werkzeug |
| Forms | Flask-WTF (CSRF) |
| Frontend | Bootstrap 5 + Bootstrap Icons (**fully local, no CDN**) |
| WSGI | Waitress (optional) |

---

## 📁 Project Structure

```
campusconnect/
├── app/
│   ├── __init__.py          ← Application factory
│   ├── models.py            ← All database models
│   ├── auth/                ← Login, register, logout
│   ├── student/             ← Student dashboard
│   ├── teacher/             ← Teacher dashboard
│   ├── materials/           ← File upload & download
│   ├── assignments/         ← Assignment lifecycle
│   ├── notices/             ← Notice board
│   ├── quizzes/             ← Quiz engine
│   ├── profile/             ← User profile
│   ├── network/             ← Server status
│   └── static/vendor/       ← Bootstrap 5 + Icons (local)
├── docs/                    ← Architecture, ER diagram, viva notes
├── scripts/                 ← Windows helper scripts (.bat, .ps1)
├── tests/                   ← 48 pytest tests (all passing)
├── config.py
├── run.py
└── requirements.txt
```

---

## 🧪 Tests

```bat
venv\Scripts\python.exe -m pytest tests/ -v
```

**48/48 tests pass** covering:
- Registration cannot create teachers
- Role-based access control
- File upload validation (extension + magic bytes)
- Assignment status (Pending / Submitted / Late)
- Resubmission replaces file
- Download permission checks
- Quiz security (correct answers never in browser HTML)
- Server-side scoring
- Duplicate attempt blocking
- Data persistence
- Zero CDN dependencies

---

## 📖 Documentation

| File | Contents |
|---|---|
| [`docs/LAN_SETUP.md`](docs/LAN_SETUP.md) | Full LAN setup, firewall, troubleshooting |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Client-server design, request flows, TCP/IP |
| [`docs/ER_DIAGRAM.md`](docs/ER_DIAGRAM.md) | Mermaid ER diagram of all tables |
| [`docs/VIVA_NOTES.md`](docs/VIVA_NOTES.md) | Q&A on networking concepts tied to this project |
| [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) | Step-by-step demo script |
| [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) | Full project report (abstract → conclusion) |

---

## ⚠️ Limitations

- Flask dev server is for **classroom demos only** — use `--waitress` for stability
- No HTTPS — plain HTTP on the LAN (do not expose to the internet)
- SQLite suits ~50 concurrent users; not for large-scale production
- File uploads limited to 25 MB

---

## 📄 License

MIT — free to use, modify, and distribute.
