# CampusConnect – Progress Checklist

## ✅ Completed

### Stage 1 – Skeleton, config, models, CLI
- [x] Project folder structure
- [x] config.py (env-based secret key, storage paths, session settings)
- [x] app/extensions.py (db, login_manager, migrate, csrf)
- [x] app/models.py (User, StudyMaterial, Assignment, AssignmentSubmission,
      Announcement, Quiz, QuizQuestion, QuizAttempt, QuizAnswer, ActivityLog)
- [x] app/decorators.py (@teacher_required, @student_required)
- [x] app/utils.py (file validation, LAN IP detection, activity logging,
      open-redirect guard)
- [x] app/cli.py (flask create-teacher, flask init-db)
- [x] app/__init__.py (create_app factory, blueprints, WAL mode, security headers,
      last_seen update, error handlers, template globals)
- [x] Flask-Migrate initialised (flask db init, tables auto-created)
- [x] requirements.txt

### Stage 2 – Auth, RBAC, base layout
- [x] auth/routes.py (login, register, logout) — role hardcoded to 'student'
- [x] auth/forms.py (LoginForm, RegistrationForm with username/email validation)
- [x] base.html (sidebar, offcanvas mobile menu, flash messages)
- [x] partials/flashes.html
- [x] templates/auth/login.html (split-screen layout)
- [x] templates/auth/register.html
- [x] app/decorators.py (403 for wrong role)

### Stage 3 – Study Materials
- [x] materials/routes.py (upload, list, download, delete)
- [x] materials/forms.py
- [x] templates/materials/index.html (search, filter, pagination, icons)
- [x] templates/materials/upload.html
- [x] File validation: extension + magic bytes
- [x] UUID stored filenames, send_from_directory download
- [x] Ownership check on delete (403 if not owner)

### Stage 4 – Notices
- [x] notices/routes.py (create, edit, delete, index with search)
- [x] notices/forms.py
- [x] templates/notices/index.html (important pinned, feed layout)
- [x] templates/notices/form.html

### Stage 5 – Assignments
- [x] assignments/routes.py (teacher CRUD, student submit/resubmit, downloads)
- [x] assignments/forms.py
- [x] templates/assignments/teacher_list.html
- [x] templates/assignments/student_list.html
- [x] templates/assignments/form.html
- [x] templates/assignments/detail.html (countdown timer)
- [x] templates/assignments/submissions.html
- [x] Resubmission replaces old file on disk
- [x] Status computed from submitted_at vs deadline
- [x] Permission checks on submission downloads

### Stage 6 – Quizzes
- [x] quizzes/routes.py (teacher: create/edit/delete quiz, questions, publish,
      results; student: start, attempt, submit, result)
- [x] quizzes/forms.py
- [x] templates/quizzes/teacher_list.html
- [x] templates/quizzes/student_list.html
- [x] templates/quizzes/quiz_form.html
- [x] templates/quizzes/manage.html
- [x] templates/quizzes/question_form.html
- [x] templates/quizzes/attempt.html (JS timer, palette, NO correct_option)
- [x] templates/quizzes/result.html (per-question review)
- [x] templates/quizzes/results.html (teacher: all attempts, stats)
- [x] Server-side timing check (started_at + duration + 10s grace)
- [x] Server-side scoring (correct_option never in browser before submit)
- [x] Duplicate attempt blocking
- [x] Zero-question quiz cannot be started

### Stage 7 – Dashboards, profile, network status, activity logging
- [x] student/routes.py (dashboard with real DB queries)
- [x] teacher/routes.py (dashboard with real DB queries)
- [x] profile/routes.py (view/edit, change password)
- [x] profile/forms.py
- [x] network/routes.py (LAN IP, uptime, active users, activity log)
- [x] templates/student/dashboard.html (stat cards, deadlines, notices, activity)
- [x] templates/teacher/dashboard.html (stat cards, quick actions, submissions)
- [x] templates/profile/view.html
- [x] templates/profile/change_password.html
- [x] templates/network/status.html
- [x] Activity logging for all key actions

### Stage 8 – UI polish, responsive, error pages
- [x] app/static/css/main.css (Navy/Blue palette, sidebar, cards, responsive)
- [x] app/static/js/main.js (submit loading state, countdown badges, alert dismiss)
- [x] templates/errors/403.html, 404.html, 413.html, 500.html
- [x] Bootstrap 5 + Bootstrap Icons stored locally (no CDN)
- [x] Mobile offcanvas menu
- [x] Submit button loading/spinner state

### Stage 9 – Tests, scripts, documentation
- [x] tests/conftest.py (fixtures: app, db, ctx, client, helpers)
- [x] tests/test_auth.py (11 tests)
- [x] tests/test_rbac.py (4 tests)
- [x] tests/test_materials.py (6 tests)
- [x] tests/test_assignments.py (7 tests)
- [x] tests/test_quizzes.py (8 tests)
- [x] tests/test_smoke.py (12 tests)
- [x] **48/48 tests passing**
- [x] scripts/start_server.bat
- [x] scripts/start_server_waitress.bat
- [x] scripts/show_ip.bat
- [x] scripts/add_firewall_rule.ps1
- [x] scripts/remove_firewall_rule.ps1
- [x] run.py (startup banner with LAN URL)
- [x] README.md
- [x] docs/LAN_SETUP.md
- [x] docs/ARCHITECTURE.md
- [x] docs/ER_DIAGRAM.md
- [x] docs/VIVA_NOTES.md
- [x] docs/DEMO_SCRIPT.md
- [x] docs/TEST_REPORT.md
- [x] docs/MANUAL_LAN_TEST_CHECKLIST.md
- [x] .gitignore

## ⏳ Pending (manual only)
- [ ] Manual LAN test from second device (phone/laptop)
- [ ] Manual quiz timer auto-submit test
- [ ] Manual mobile layout review at 360px
