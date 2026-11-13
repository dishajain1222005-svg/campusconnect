# CampusConnect – Project Report

**Subject:** Computer Networks  
**Project Title:** CampusConnect – Offline LAN-Based Academic Platform  
**Team Members:** ___________________________  
**Date:** ___________________________  

---

## Abstract

CampusConnect is a web-based academic platform that operates entirely on a local
area network (LAN) without requiring internet access. Built with Python and the
Flask framework, it enables teachers to share study materials, create assignments,
post notices, and design auto-graded quizzes. Students connect from any device on
the same Wi-Fi network using a browser. The project demonstrates client-server
architecture, TCP/IP networking, HTTP, and application-layer security concepts in
a practical setting.

---

## 1. Introduction

Modern educational institutions increasingly rely on digital platforms for
content delivery and assessment. However, in areas with limited or no internet
connectivity, cloud-based platforms become unusable. CampusConnect solves this by
running a complete academic portal on a single Windows laptop, accessible to all
devices on the same local Wi-Fi network.

---

## 2. Problem Statement

Students and teachers in locations with unreliable internet cannot use cloud-based
academic tools such as Google Classroom or Moodle's hosted version. There is a
need for a self-contained, lightweight platform that:
- Requires no internet after initial setup
- Works on any browser-equipped device
- Supports material sharing, assignments, quizzes, and notices
- Provides role-based access for students and teachers

---

## 3. Objectives

1. Build a full-stack web application using Python and Flask
2. Demonstrate client-server communication over a LAN using HTTP/TCP/IP
3. Implement role-based access control (RBAC) for students and teachers
4. Enable secure file upload, storage, and authenticated download
5. Build a timed, auto-graded quiz engine with server-side security
6. Run the server on 0.0.0.0 so all LAN devices can connect
7. Work 100% offline after dependencies are installed

---

## 4. Existing vs Proposed System

| Aspect | Existing (Cloud-based) | Proposed (CampusConnect) |
|--------|------------------------|--------------------------|
| Internet required | Yes (always) | No (after install) |
| Setup complexity | High (cloud account) | Low (one command) |
| Data location | External servers | Local laptop |
| Cost | Subscription fee | Free (open source) |
| Works offline | No | Yes |
| Access from phone | Via internet | Via LAN only |

---

## 5. Hardware and Software Requirements

### Hardware
- Server: Windows 11 laptop (any modern CPU, 4 GB RAM, 10 GB storage)
- Clients: Any device with a browser (phone, tablet, laptop)
- Network: Wi-Fi router, Windows Mobile Hotspot, or phone hotspot

### Software
- Python 3.10+
- Flask 3.1 and extensions (see requirements.txt)
- SQLite (built into Python)
- Bootstrap 5 and Bootstrap Icons (stored locally)
- Windows 11 (server)

---

## 6. Modules

| Module | Description |
|--------|-------------|
| Authentication | Student self-registration, teacher CLI creation, login/logout |
| Study Materials | Upload, list, search, download PDFs and documents |
| Assignments | Create with deadline, submit files, resubmit, view status |
| Notice Board | Post, pin important notices, search |
| Quizzes | Build MCQs, timed attempts, auto-grade, results |
| Dashboards | Role-specific overview with real DB statistics |
| Profile | Edit personal info, change password |
| Network Status | Server IP, uptime, active users, activity log |

---

## 7. Implementation

### Technology Stack
- **Backend:** Python 3.13, Flask 3.1 (application factory + blueprints)
- **ORM:** SQLAlchemy 2 via Flask-SQLAlchemy
- **Database:** SQLite with WAL mode for concurrent access
- **Auth:** Flask-Login + Werkzeug password hashing (pbkdf2:sha256)
- **Forms:** Flask-WTF with CSRF protection
- **Migrations:** Flask-Migrate (Alembic)
- **Frontend:** Bootstrap 5, Bootstrap Icons, vanilla JavaScript
- **WSGI:** Waitress (optional, for stability)

### Key Security Features
- Passwords never stored in plain text
- CSRF tokens on every POST form
- Files stored under UUID names, never served by filename from URL
- Magic-byte validation on uploads
- Role enforced server-side, never from form data
- Quiz answers never sent to browser before submission

### Networking Implementation
- Flask binds to `0.0.0.0:5000` to listen on all interfaces
- LAN IP detected via UDP socket trick (no packets sent)
- SQLite WAL mode for concurrent LAN users
- Startup banner prints the URL for students to type

---

## 8. Testing

### Automated Tests (pytest)
- 48 test cases covering all major features
- All 48 tests pass
- Test categories: auth, RBAC, materials, assignments, quizzes, smoke, CDN check

### Manual Testing Required
- LAN access from real devices (see `docs/MANUAL_LAN_TEST_CHECKLIST.md`)
- Mobile responsiveness
- Quiz timer auto-submit

---

## 9. Advantages

1. Works completely offline — no internet dependency
2. Any browser-capable device can connect
3. No data leaves the local network — full privacy
4. Simple one-command setup
5. Auto-graded quizzes save teacher time
6. Secure: CSRF, hashed passwords, UUID filenames, role-based access

---

## 10. Limitations

1. Flask development server is not production-grade (use Waitress for demos)
2. SQLite is single-file — suitable for ~50 users, not 1000+
3. No HTTPS — data is unencrypted on the LAN
4. No email notifications
5. Server laptop must stay on while students use the platform
6. IP address changes on DHCP reassignment (need to update URL)

---

## 11. Future Scope

1. Add HTTPS using a self-signed certificate
2. Replace SQLite with PostgreSQL for larger deployments
3. Add real-time notifications using WebSockets
4. Add essay-type assignments with teacher grading
5. Build a mobile app for offline-first access
6. Add student progress analytics and grade book
7. Add video/audio lecture uploads

---

## 12. Conclusion

CampusConnect successfully demonstrates a complete offline LAN-based academic
platform. It implements core computer networking concepts — TCP/IP, HTTP, sockets,
LAN topology, client-server architecture — in a practical, working application.
All 48 automated tests pass, confirming the security, correctness, and
completeness of the implementation.

The project shows that a full-featured educational platform can run on commodity
hardware, serve an entire classroom over Wi-Fi, and work without any internet
connection after the initial setup.

---

## References

1. Flask Documentation – https://flask.palletsprojects.com/
2. Bootstrap 5 Documentation – https://getbootstrap.com/
3. SQLAlchemy Documentation – https://www.sqlalchemy.org/
4. Werkzeug Security – https://werkzeug.palletsprojects.com/
5. RFC 7230 – HTTP/1.1 Message Syntax and Routing
6. RFC 791 – Internet Protocol (IPv4)
