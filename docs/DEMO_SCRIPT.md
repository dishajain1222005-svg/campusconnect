# CampusConnect – Demo Script

This script demonstrates the full flow for an examiner or audience.
Run steps on the **server laptop** unless stated otherwise.

---

## Setup (before the demo)

1. `cd "cn project"`
2. `venv\Scripts\activate`
3. `python run.py` — note the printed LAN URL, e.g. `http://192.168.1.42:5000`
4. If not done: `flask create-teacher` (create one teacher account)
5. Have at least one student device (phone or second laptop) on the same Wi-Fi

---

## Part 1 – Teacher uploads a study material

**On the server laptop:**

1. Open `http://127.0.0.1:5000` in a browser
2. Log in as the teacher
3. Sidebar → Study Materials → Upload Material
4. Fill in: Title, Subject, Description, attach a PDF
5. Click Upload — confirm "uploaded successfully"

**On the student device:**

6. Open `http://192.168.x.x:5000`
7. Register as a student (or log in)
8. Sidebar → Study Materials
9. Find the material just uploaded → click Download
10. ✅ **File downloads on the student device — internet is OFF**

---

## Part 2 – Assignment lifecycle

**Teacher (server laptop):**
1. Sidebar → Assignments → New Assignment
2. Fill in title, subject, deadline (5 minutes from now for demo)
3. Optionally attach a reference file → Save

**Student (other device):**
4. Sidebar → Assignments → see the new assignment with "Pending" badge
5. Click View Details → see the countdown timer
6. Upload a submission file → Submit
7. Badge changes to "Submitted (on time)"

**Teacher:**
8. Sidebar → Assignments → Submissions (count = 1)
9. See student name, timestamp, "On Time" badge
10. Click Download to retrieve the student's file

---

## Part 3 – Notice board

**Teacher:**
1. Sidebar → Notice Board → Post Notice
2. Title: "Exam Next Week", body: details, check "Important" → Publish
3. The notice appears pinned at the top with a red border

**Student:**
4. Sidebar → Notice Board
5. The important notice is pinned at the top
6. Search for "exam" — notice filters correctly

---

## Part 4 – Quiz

**Teacher:**
1. Sidebar → Quizzes → New Quiz → "CN Concepts", 5 min, CS
2. Manage → Add Question (3 MCQ questions)
3. Click Publish

**Student:**
4. Sidebar → Quizzes → "CN Concepts" — Start Quiz
5. Answer questions, use the question palette to jump between them
6. Watch the countdown timer
7. Submit
8. See score and per-question review with correct answers highlighted

**Teacher:**
9. Quizzes → Results — see the student's score, average, highest, lowest

---

## Part 5 – Network Status page

**Teacher:**
1. Sidebar → Network Status
2. Show: LAN IP, port, uptime, active users, activity log
3. Copy the URL and paste into the student's browser address bar
4. ✅ Demonstrates that the app is accessible over LAN with zero internet

---

## ✅ Verification checklist (manual, fill in during demo)

| Test | Expected | Result |
|------|----------|--------|
| Student registers | Redirected to login | |
| Student cannot access /materials/upload | 403 Forbidden | |
| PDF uploads from teacher | "Uploaded successfully" | |
| .exe file rejected | "not allowed" message | |
| Download from student device | File received | |
| Assignment submitted | "Submitted on time" | |
| Late submission | "Late" badge | |
| Quiz answers not visible during attempt | Confirmed | |
| Quiz score correct | Matches manual count | |
| Second attempt blocked | Redirect to result | |
| Internet turned OFF | App still works | |
