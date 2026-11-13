"""
models.py – All SQLAlchemy ORM models for CampusConnect.

Each model maps to a table in SQLite.  Relationships let us navigate
between rows (e.g. assignment.submissions gives every submission for that
assignment) without writing raw SQL.
"""
from datetime import datetime, timezone
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# ─────────────────────────────────────────────
#  Helper: UTC now
# ─────────────────────────────────────────────
def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ─────────────────────────────────────────────
#  User
# ─────────────────────────────────────────────
class User(UserMixin, db.Model):
    """
    Represents both students and teachers.
    role is enforced at the application layer – the registration form
    hardcodes 'student'; teachers are created only via the CLI.
    """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")  # 'student' | 'teacher'
    roll_no = db.Column(db.String(40))
    department = db.Column(db.String(80))
    last_seen = db.Column(db.DateTime, default=utcnow)
    created_at = db.Column(db.DateTime, default=utcnow)

    # ── Relationships ────────────────────────────────────────────────────
    materials = db.relationship("StudyMaterial", backref="uploader", lazy="dynamic",
                                foreign_keys="StudyMaterial.uploaded_by",
                                cascade="all, delete-orphan")
    assignments = db.relationship("Assignment", backref="creator", lazy="dynamic",
                                  foreign_keys="Assignment.created_by",
                                  cascade="all, delete-orphan")
    submissions = db.relationship("AssignmentSubmission", backref="student", lazy="dynamic",
                                  foreign_keys="AssignmentSubmission.student_id",
                                  cascade="all, delete-orphan")
    announcements = db.relationship("Announcement", backref="author", lazy="dynamic",
                                    foreign_keys="Announcement.author_id",
                                    cascade="all, delete-orphan")
    quizzes = db.relationship("Quiz", backref="creator", lazy="dynamic",
                               foreign_keys="Quiz.created_by",
                               cascade="all, delete-orphan")
    quiz_attempts = db.relationship("QuizAttempt", backref="student", lazy="dynamic",
                                    foreign_keys="QuizAttempt.student_id",
                                    cascade="all, delete-orphan")
    activity_logs = db.relationship("ActivityLog", backref="user", lazy="dynamic",
                                    foreign_keys="ActivityLog.user_id",
                                    cascade="all, delete-orphan")

    # ── Password helpers ─────────────────────────────────────────────────
    def set_password(self, password: str):
        """Hash the password with werkzeug.security (pbkdf2:sha256)."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_teacher(self) -> bool:
        return self.role == "teacher"

    @property
    def is_student(self) -> bool:
        return self.role == "student"

    def __repr__(self):
        return f"<User {self.username} [{self.role}]>"


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to reload the user object from the user ID stored in the session."""
    return db.session.get(User, int(user_id))


# ─────────────────────────────────────────────
#  Study Material
# ─────────────────────────────────────────────
class StudyMaterial(db.Model):
    """Files (PDFs, slides, docs) shared by teachers for students to download."""
    __tablename__ = "study_material"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False)
    original_filename = db.Column(db.String(260), nullable=False)
    stored_filename = db.Column(db.String(260), nullable=False, unique=True)
    file_size = db.Column(db.Integer)  # bytes
    uploaded_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def size_human(self) -> str:
        """Return human-readable file size (does NOT mutate self.file_size)."""
        if not self.file_size:
            return "—"
        size = float(self.file_size)
        for unit in ("B", "KB", "MB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} GB"


# ─────────────────────────────────────────────
#  Assignment
# ─────────────────────────────────────────────
class Assignment(db.Model):
    """An assignment posted by a teacher, optionally with a reference file."""
    __tablename__ = "assignment"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    ref_original_filename = db.Column(db.String(260))
    ref_stored_filename = db.Column(db.String(260))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    submissions = db.relationship("AssignmentSubmission", backref="assignment",
                                  lazy="dynamic", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
#  Assignment Submission
# ─────────────────────────────────────────────
class AssignmentSubmission(db.Model):
    """
    One submission per student per assignment.
    Status is COMPUTED from submitted_at vs assignment.deadline – not stored.
    """
    __tablename__ = "assignment_submission"
    __table_args__ = (
        db.UniqueConstraint("assignment_id", "student_id", name="uq_submission"),
    )

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignment.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    original_filename = db.Column(db.String(260), nullable=False)
    stored_filename = db.Column(db.String(260), nullable=False, unique=True)
    submitted_at = db.Column(db.DateTime, default=utcnow)

    @property
    def is_late(self) -> bool:
        """Return True if submitted after the assignment deadline."""
        return self.submitted_at > self.assignment.deadline

    @property
    def status(self) -> str:
        return "Late" if self.is_late else "Submitted"


# ─────────────────────────────────────────────
#  Announcement
# ─────────────────────────────────────────────
class Announcement(db.Model):
    """Notice board posts created by teachers."""
    __tablename__ = "announcement"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_important = db.Column(db.Boolean, default=False, nullable=False)
    publish_date = db.Column(db.DateTime, default=utcnow, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)


# ─────────────────────────────────────────────
#  Quiz
# ─────────────────────────────────────────────
class Quiz(db.Model):
    """A timed multiple-choice quiz created by a teacher."""
    __tablename__ = "quiz"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    allow_retake = db.Column(db.Boolean, default=False, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    questions = db.relationship("QuizQuestion", backref="quiz",
                                lazy="dynamic", cascade="all, delete-orphan",
                                order_by="QuizQuestion.id")
    attempts = db.relationship("QuizAttempt", backref="quiz",
                               lazy="dynamic", cascade="all, delete-orphan")


class QuizQuestion(db.Model):
    """One MCQ question belonging to a quiz."""
    __tablename__ = "quiz_question"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    # IMPORTANT: correct_option is NEVER sent to the student's browser before submission
    correct_option = db.Column(db.String(1), nullable=False)  # 'A'|'B'|'C'|'D'
    marks = db.Column(db.Integer, default=1, nullable=False)

    answers = db.relationship("QuizAnswer", backref="question",
                               lazy="dynamic", cascade="all, delete-orphan")


class QuizAttempt(db.Model):
    """One student's attempt at a quiz."""
    __tablename__ = "quiz_attempt"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    started_at = db.Column(db.DateTime, default=utcnow)
    submitted_at = db.Column(db.DateTime)
    score = db.Column(db.Integer)       # filled on submission
    total_marks = db.Column(db.Integer) # filled on submission

    answers = db.relationship("QuizAnswer", backref="attempt",
                               lazy="dynamic", cascade="all, delete-orphan")

    @property
    def is_complete(self) -> bool:
        return self.submitted_at is not None

    @property
    def percentage(self):
        if self.total_marks and self.total_marks > 0:
            return round((self.score / self.total_marks) * 100, 1)
        return 0


class QuizAnswer(db.Model):
    """The option a student selected for one question in one attempt."""
    __tablename__ = "quiz_answer"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempt.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("quiz_question.id"), nullable=False)
    selected_option = db.Column(db.String(1))  # 'A'|'B'|'C'|'D' or None if skipped
    is_correct = db.Column(db.Boolean, default=False)


# ─────────────────────────────────────────────
#  Activity Log
# ─────────────────────────────────────────────
class ActivityLog(db.Model):
    """
    Audit trail of user actions.  Used by the network status page to show
    who is active and what has been done recently.
    """
    __tablename__ = "activity_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
