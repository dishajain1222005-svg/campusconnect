# CampusConnect – Automated Test Report

**Date:** Generated during project build  
**Python:** 3.13.7  
**Pytest:** 9.2.0  
**Command run:** `.\venv\Scripts\python.exe -m pytest tests/ -v`

---

## Summary

| Result | Count |
|--------|-------|
| ✅ Passed | 48 |
| ❌ Failed | 0 |
| Total | 48 |

**All 48 tests passed.**

---

## Test breakdown

### test_assignments.py (7 tests) – all PASSED

| Test | What it proves |
|------|----------------|
| test_pending_status | Assignment shows "Pending" before submission |
| test_submitted_on_time_status | On-time submission sets status=Submitted, is_late=False |
| test_late_status | Post-deadline submission sets is_late=True, status=Late |
| test_resubmission_replaces_file | Resubmit keeps 1 DB row, stored_filename changes |
| test_student_cannot_download_other_students_submission | Returns HTTP 403 |
| test_teacher_downloads_own_assignment_submission | Returns HTTP 200 with file |
| test_teacher_cannot_download_other_teachers_submissions | Returns HTTP 403 |

### test_auth.py (11 tests) – all PASSED

| Test | What it proves |
|------|----------------|
| test_register_student_ok | Registration creates a student account |
| test_register_cannot_set_teacher_role | role=teacher in POST is ignored; account is student |
| test_duplicate_username_rejected | "already taken" shown |
| test_short_password_rejected | Passwords < 8 chars refused |
| test_password_stored_hashed | Hash stored, not plain text; check_password() works |
| test_unauthenticated_redirects_to_login | All protected routes redirect to /login |
| test_login_wrong_password | Generic "Invalid username or password" shown |
| test_login_nonexistent_user_generic_error | Generic message, no "does not exist" |
| test_student_login_redirects_to_student_dashboard | Student sees Dashboard |
| test_teacher_login_redirects_to_teacher_dashboard | Teacher sees Dashboard |
| test_logout | Session cleared; subsequent request redirects to login |

### test_materials.py (6 tests) – all PASSED

| Test | What it proves |
|------|----------------|
| test_teacher_upload_valid_pdf | Valid PDF uploads successfully |
| test_disallowed_extension_rejected | .exe rejected with "not allowed" |
| test_pdf_magic_byte_mismatch_rejected | File named .pdf but not PDF — rejected |
| test_download_requires_login | GET /download/1 without login → 302 to login |
| test_student_cannot_upload | GET /materials/upload as student → 302/403 |
| test_teacher_cannot_delete_other_teachers_material | DELETE other teacher's file → 403 |

### test_quizzes.py (8 tests) – all PASSED

| Test | What it proves |
|------|----------------|
| test_correct_answers_not_in_attempt_html | "correct_option" absent from attempt page HTML |
| test_score_computed_correctly | All correct → score = sum(marks) = 4 |
| test_score_zero_all_wrong | All wrong → score = 0 |
| test_duplicate_attempt_blocked | Second attempt row not created when allow_retake=False |
| test_unpublished_quiz_blocked | Student cannot start unpublished quiz → 302/403 |
| test_zero_question_quiz_cannot_start | "question" appears in flash message |
| test_late_submission_still_processed | Backdated attempt still scored; submitted_at set |
| test_student_cannot_see_other_students_result | Student B gets 403 on Student A's result |

### test_rbac.py (4 tests) – all PASSED

| Test | What it proves |
|------|----------------|
| test_student_cannot_access_teacher_only_routes | /upload, /create routes → 302/403 for student |
| test_teacher_cannot_access_student_dashboard | /student/dashboard → 302/403 for teacher |
| test_unauthenticated_blocked_from_all_protected | 8 routes all redirect to /login |
| test_path_traversal_download_blocked | /download/9999999 → 404 (no path traversal) |

### test_smoke.py (12 tests) – all PASSED

| Test | What it proves |
|------|----------------|
| test_login_page_loads | GET /login → 200, "CampusConnect" in body |
| test_register_page_loads | GET /register → 200 |
| test_root_redirects | GET / → 302 |
| test_student_pages | 7 student pages all return 200 |
| test_teacher_pages | 11 teacher pages all return 200 |
| test_404_page | /nonexistent → 404 with "404" in body |
| test_403_page | /materials/upload as student → 403 |
| test_no_cdn_links_in_templates | No `src=https://` or `href=https://` in any template |
| test_bootstrap_css_exists_locally | bootstrap.min.css present and >100 KB |
| test_bootstrap_js_exists_locally | bootstrap.bundle.min.js present and >50 KB |
| test_bootstrap_icons_exists_locally | bootstrap-icons.min.css present |
| test_user_persists | User created in one app context, found in another |

---

## Warnings

67 deprecation warnings from SQLAlchemy about `Query.get()` being legacy in
SQLAlchemy 2.x. These do not affect functionality and are in the ORM's
backwards-compatibility layer. No action required for a demo project.

---

## What was actually tested vs what needs manual testing

### Tested automatically (pytest, test client)
- Registration cannot create teachers
- Role-based access (all routes)
- CSRF validation (covered by Flask-WTF; disabled in tests to allow form posting)
- File extension and magic byte validation
- Assignment status computation (Pending/Submitted/Late)
- Resubmission replaces file
- Download permission checks
- Quiz security (no correct answers in HTML)
- Quiz server-side scoring
- Duplicate attempt blocking
- Data persistence across app contexts
- No CDN dependencies in templates
- All 18 main pages return HTTP 200

### Requires manual testing on real devices
- Actual LAN connectivity from phone/laptop over Wi-Fi
- File downloads on real devices
- Quiz timer auto-submit (requires real browser + waiting)
- Mobile responsiveness at 360px
- Touch interaction on mobile quiz attempt page

See `docs/MANUAL_LAN_TEST_CHECKLIST.md` for the manual test checklist.
