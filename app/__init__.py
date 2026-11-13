"""
app/__init__.py – Application factory.

The factory pattern lets us create multiple app instances (e.g., for testing
with a separate DB) without module-level side effects.

Networking concept: Flask's development server is a single-threaded HTTP
server by default.  We enable threaded=True in run.py so multiple students
can connect simultaneously without waiting in a queue.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template, g, request
from flask_login import current_user
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.extensions import db, login_manager, migrate, csrf
from config import Config
from datetime import datetime, timezone


def create_app(config_object=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=False)

    # ── Load config ──────────────────────────────────────────────────────
    if config_object is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config_object)

    # Expose PORT to the network blueprint
    app.config.setdefault("PORT", Config.PORT)

    # ── Create storage directories ───────────────────────────────────────
    for d in (app.config["MATERIAL_UPLOAD_DIR"],
              app.config["ASSIGNMENT_REF_DIR"],
              app.config["SUBMISSION_DIR"]):
        Path(d).mkdir(parents=True, exist_ok=True)

    # ── Initialise extensions ────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # ── Enable SQLite WAL mode (better concurrent read performance) ──────
    @event.listens_for(Engine, "connect")
    def set_wal_mode(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    # ── Security headers on every response ──────────────────────────────
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    # ── Update last_seen (at most once per minute) ───────────────────────
    @app.before_request
    def update_last_seen():
        if current_user.is_authenticated:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            if (current_user.last_seen is None or
                    (now - current_user.last_seen).total_seconds() > 60):
                current_user.last_seen = now
                db.session.commit()

    # ── Register blueprints ──────────────────────────────────────────────
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.teacher.routes import teacher_bp
    from app.materials.routes import materials_bp
    from app.assignments.routes import assignments_bp
    from app.notices.routes import notices_bp
    from app.quizzes.routes import quizzes_bp
    from app.profile.routes import profile_bp
    from app.network.routes import network_bp
    from app.cli import cli_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(notices_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(cli_bp)

    # ── Template globals ─────────────────────────────────────────────────
    from flask_wtf.csrf import generate_csrf
    from markupsafe import Markup

    @app.template_global()
    def csrf_token_input():
        return Markup(f'<input type="hidden" name="csrf_token" value="{generate_csrf()}">')

    @app.template_global()
    def now_utc():
        return datetime.now(timezone.utc).replace(tzinfo=None)

    # ── Root redirect ────────────────────────────────────────────────────
    @app.route("/")
    def index():
        from flask_login import current_user
        from flask import redirect, url_for
        if current_user.is_authenticated:
            if current_user.is_teacher:
                return redirect(url_for("teacher.dashboard"))
            return redirect(url_for("student.dashboard"))
        return redirect(url_for("auth.login"))

    # ── Error handlers ───────────────────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template("errors/413.html"), 413

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # ── Auto-create tables on first run ──────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── File logging ─────────────────────────────────────────────────────
    if not app.testing:
        log_file = app.config.get("LOG_FILE")
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(str(log_file), maxBytes=1_000_000, backupCount=3)
            handler.setLevel(logging.WARNING)
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            )
            handler.setFormatter(formatter)
            app.logger.addHandler(handler)

    return app
