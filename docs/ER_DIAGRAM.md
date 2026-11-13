# CampusConnect – Entity-Relationship Diagram

```mermaid
erDiagram
    USER {
        int id PK
        string full_name
        string username UK
        string email UK
        string password_hash
        string role
        string roll_no
        string department
        datetime last_seen
        datetime created_at
    }

    STUDY_MATERIAL {
        int id PK
        string title
        string description
        string subject
        string original_filename
        string stored_filename UK
        int file_size
        int uploaded_by FK
        datetime created_at
    }

    ASSIGNMENT {
        int id PK
        string title
        string description
        string subject
        datetime deadline
        string ref_original_filename
        string ref_stored_filename
        int created_by FK
        datetime created_at
    }

    ASSIGNMENT_SUBMISSION {
        int id PK
        int assignment_id FK
        int student_id FK
        string original_filename
        string stored_filename UK
        datetime submitted_at
    }

    ANNOUNCEMENT {
        int id PK
        string title
        string body
        bool is_important
        datetime publish_date
        int author_id FK
        datetime created_at
        datetime updated_at
    }

    QUIZ {
        int id PK
        string title
        string description
        string subject
        int duration_minutes
        bool is_published
        bool allow_retake
        int created_by FK
        datetime created_at
    }

    QUIZ_QUESTION {
        int id PK
        int quiz_id FK
        string question_text
        string option_a
        string option_b
        string option_c
        string option_d
        string correct_option
        int marks
    }

    QUIZ_ATTEMPT {
        int id PK
        int quiz_id FK
        int student_id FK
        datetime started_at
        datetime submitted_at
        int score
        int total_marks
    }

    QUIZ_ANSWER {
        int id PK
        int attempt_id FK
        int question_id FK
        string selected_option
        bool is_correct
    }

    ACTIVITY_LOG {
        int id PK
        int user_id FK
        string action
        string details
        datetime created_at
    }

    USER ||--o{ STUDY_MATERIAL : "uploads"
    USER ||--o{ ASSIGNMENT : "creates"
    USER ||--o{ ASSIGNMENT_SUBMISSION : "submits"
    USER ||--o{ ANNOUNCEMENT : "authors"
    USER ||--o{ QUIZ : "creates"
    USER ||--o{ QUIZ_ATTEMPT : "attempts"
    USER ||--o{ ACTIVITY_LOG : "generates"

    ASSIGNMENT ||--o{ ASSIGNMENT_SUBMISSION : "has"
    QUIZ ||--o{ QUIZ_QUESTION : "contains"
    QUIZ ||--o{ QUIZ_ATTEMPT : "has"
    QUIZ_ATTEMPT ||--o{ QUIZ_ANSWER : "records"
    QUIZ_QUESTION ||--o{ QUIZ_ANSWER : "answered by"
```

## Table purposes

| Table | Purpose |
|-------|---------|
| `user` | All accounts (students and teachers). Role field enforces RBAC. |
| `study_material` | Metadata for uploaded files. Actual files are on disk under UUID names. |
| `assignment` | Homework posted by teachers with a deadline. |
| `assignment_submission` | One row per student per assignment. Unique constraint prevents duplicates. |
| `announcement` | Notice board posts. `is_important` pins them to the top. |
| `quiz` | Quiz metadata. `is_published` controls student visibility. |
| `quiz_question` | MCQ questions. `correct_option` is NEVER sent to student browsers before submission. |
| `quiz_attempt` | Records when a student started and submitted a quiz, plus their computed score. |
| `quiz_answer` | The option a student chose for each question in an attempt. |
| `activity_log` | Audit trail for logins, uploads, submissions, etc. Used by Network Status page. |
