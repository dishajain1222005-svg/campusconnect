# Manual LAN Test Checklist

**Purpose:** To be completed on real devices with the internet switched OFF.
Do not fill in results you have not personally observed.

**Setup:**
- Server: Windows laptop running `python run.py`
- Client A: Second laptop on same Wi-Fi
- Client B: Android/iOS phone on same Wi-Fi
- Internet: **OFF** (disable on the router or disconnect WAN cable)
- Server LAN IP: _________________ (fill in from startup banner)

---

## Section 1 – Connectivity

| # | Test | Device | Expected | Result (Pass/Fail) | Notes |
|---|------|--------|----------|--------------------|-------|
| 1.1 | Open `http://SERVER_IP:5000` | Laptop | Login page loads | | |
| 1.2 | Open `http://SERVER_IP:5000` | Phone | Login page loads | | |
| 1.3 | Open `http://127.0.0.1:5000` | Server | Login page loads | | |
| 1.4 | Ping SERVER_IP from client | Laptop | Replies received | | |
| 1.5 | Internet is OFF | Both | App still works | | |

---

## Section 2 – Authentication

| # | Test | Device | Expected | Result | Notes |
|---|------|--------|----------|--------|-------|
| 2.1 | Register as student | Phone | Redirected to login | | |
| 2.2 | Log in as student | Phone | Student dashboard | | |
| 2.3 | Log in as teacher | Server | Teacher dashboard | | |
| 2.4 | Wrong password | Phone | "Invalid username or password" | | |
| 2.5 | Register with role=teacher in form | Phone | Account is student role | | |

---

## Section 3 – Study Materials

| # | Test | Device | Expected | Result | Notes |
|---|------|--------|----------|--------|-------|
| 3.1 | Teacher uploads a PDF | Server | "Uploaded successfully" | | |
| 3.2 | Student sees uploaded file | Phone | File listed | | |
| 3.3 | Student downloads PDF | Phone | File downloads | | |
| 3.4 | Upload .exe (teacher) | Server | "type not allowed" | | |
| 3.5 | Student tries to access /upload | Phone | 403 error page | | |

---

## Section 4 – Assignments

| # | Test | Device | Expected | Result | Notes |
|---|------|--------|----------|--------|-------|
| 4.1 | Teacher creates assignment | Server | Appears in list | | |
| 4.2 | Student sees "Pending" | Phone | Pending badge | | |
| 4.3 | Student submits file | Phone | "Submitted on time" | | |
| 4.4 | Teacher views submissions | Server | Student name, On Time | | |
| 4.5 | Teacher downloads submission | Server | File downloads | | |
| 4.6 | Student B cannot download Student A's submission | Laptop | 403 | | |

---

## Section 5 – Notice Board

| # | Test | Device | Expected | Result | Notes |
|---|------|--------|----------|--------|-------|
| 5.1 | Teacher posts important notice | Server | Pinned at top | | |
| 5.2 | Student sees pinned notice | Phone | Red border, top | | |
| 5.3 | Search notice | Phone | Filtered results | | |

---

## Section 6 – Quizzes

| # | Test | Device | Expected | Result | Notes |
|---|------|--------|----------|--------|-------|
| 6.1 | Teacher creates quiz + questions | Server | Questions saved | | |
| 6.2 | Teacher publishes quiz | Server | Published badge | | |
| 6.3 | Student sees quiz | Phone | "Not Attempted" | | |
| 6.4 | Student starts quiz | Phone | Questions displayed | | |
| 6.5 | Timer counts down | Phone | Timer visible | | |
| 6.6 | No correct answers in HTML | Phone | (check page source) | | |
| 6.7 | Student submits quiz | Phone | Score shown | | |
| 6.8 | Teacher sees results | Server | Score, avg, min, max | | |
| 6.9 | Second attempt blocked | Phone | Redirected to result | | |

---

## Section 7 – Network Status

| # | Test | Expected | Result | Notes |
|---|------|----------|--------|-------|
| 7.1 | Server LAN IP shown correctly | Matches `ipconfig` | | |
| 7.2 | "Open on other devices" URL works | Clients can connect | | |
| 7.3 | Active users count updates | Shows 1+ after login | | |

---

**Tested by:** _______________________  
**Date:** _______________________  
**Server IP:** _______________________  
**Wi-Fi setup (hotspot / router):** _______________________
