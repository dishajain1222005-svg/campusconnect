"""
decorators.py – Role-based access control decorators.

Security concept: These wrappers check the logged-in user's role BEFORE
the view function runs.  Returning HTTP 403 Forbidden means the server
understood the request but refuses to fulfil it.
"""
from functools import wraps
from flask import abort
from flask_login import current_user


def teacher_required(f):
    """Allow only authenticated teachers; return 403 for everyone else."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_teacher:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    """Allow only authenticated students; return 403 for everyone else."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_student:
            abort(403)
        return f(*args, **kwargs)
    return decorated
