"""
cli.py – Custom Flask CLI commands.

Run with:  flask create-teacher
Teachers can ONLY be created this way – the registration form is locked to
the 'student' role.  This prevents privilege escalation via form tampering.
"""
import click
import getpass
from flask import Blueprint
from app.extensions import db
from app.models import User

cli_bp = Blueprint("cli", __name__, cli_group=None)


@cli_bp.cli.command("create-teacher")
def create_teacher():
    """Interactively create a teacher account (CLI only)."""
    click.echo("=== CampusConnect – Create Teacher Account ===")
    full_name = click.prompt("Full name")
    username = click.prompt("Username")
    email = click.prompt("Email")

    # Check uniqueness before asking for a password
    if User.query.filter_by(username=username).first():
        click.echo(f"Error: username '{username}' already exists.", err=True)
        return
    if User.query.filter_by(email=email).first():
        click.echo(f"Error: email '{email}' already exists.", err=True)
        return

    # Use getpass so the password is not echoed to the terminal
    while True:
        password = getpass.getpass("Password (min 8 characters): ")
        if len(password) < 8:
            click.echo("Password must be at least 8 characters. Try again.")
            continue
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            click.echo("Passwords do not match. Try again.")
            continue
        break

    teacher = User(
        full_name=full_name,
        username=username,
        email=email,
        role="teacher",   # Hardcoded here, never read from user input
    )
    teacher.set_password(password)
    db.session.add(teacher)
    db.session.commit()
    click.echo(f"Teacher account '{username}' created successfully.")


@cli_bp.cli.command("init-db")
def init_db():
    """Create all tables (use flask db upgrade for migrations instead)."""
    db.create_all()
    click.echo("Database tables created.")
