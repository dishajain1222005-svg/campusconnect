"""
materials/routes.py – Study material upload, listing, download, delete.

File security: Files are stored under random UUID names on disk.  Downloads
go through an authenticated route that looks up the file by DB id; the real
filename is never in the URL.  send_from_directory prevents path traversal.
"""
import os
from pathlib import Path
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, abort, send_from_directory, current_app)
from flask_login import login_required, current_user
from app.extensions import db
from app.models import StudyMaterial
from app.decorators import teacher_required
from app.utils import validate_and_save, allowed_material, log_activity
from .forms import MaterialUploadForm

materials_bp = Blueprint("materials", __name__, url_prefix="/materials")

ICONS = {
    "pdf": "bi-file-earmark-pdf-fill text-danger",
    "ppt": "bi-file-earmark-slides-fill text-warning",
    "pptx": "bi-file-earmark-slides-fill text-warning",
    "doc": "bi-file-earmark-word-fill text-primary",
    "docx": "bi-file-earmark-word-fill text-primary",
}


@materials_bp.route("/")
@login_required
def index():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    subject = request.args.get("subject", "").strip()

    query = StudyMaterial.query.order_by(StudyMaterial.created_at.desc())
    if q:
        query = query.filter(StudyMaterial.title.ilike(f"%{q}%"))
    if subject:
        query = query.filter(StudyMaterial.subject.ilike(f"%{subject}%"))

    materials = query.paginate(page=page, per_page=15, error_out=False)
    subjects = db.session.query(StudyMaterial.subject).distinct().order_by(StudyMaterial.subject).all()
    subjects = [s[0] for s in subjects]

    return render_template("materials/index.html",
                           materials=materials, q=q, subject=subject,
                           subjects=subjects, icons=ICONS)


@materials_bp.route("/upload", methods=["GET", "POST"])
@login_required
@teacher_required
def upload():
    form = MaterialUploadForm()
    if form.validate_on_submit():
        try:
            info = validate_and_save(
                form.file.data,
                current_app.config["MATERIAL_UPLOAD_DIR"],
                allowed_material,
            )
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("materials/upload.html", form=form)

        mat = StudyMaterial(
            title=form.title.data.strip(),
            description=(form.description.data or "").strip(),
            subject=form.subject.data.strip(),
            original_filename=info["original_filename"],
            stored_filename=info["stored_filename"],
            file_size=info["file_size"],
            uploaded_by=current_user.id,
        )
        db.session.add(mat)
        db.session.commit()
        log_activity(current_user.id, "upload_material",
                     f"Uploaded: {info['original_filename']}")
        flash("Material uploaded successfully.", "success")
        return redirect(url_for("materials.index"))

    return render_template("materials/upload.html", form=form)


@materials_bp.route("/download/<int:material_id>")
@login_required
def download(material_id):
    """
    Authenticated download route.  Looks up the file by DB id only;
    no filename is taken from the URL (prevents path traversal).
    """
    mat = StudyMaterial.query.get_or_404(material_id)
    upload_dir = current_app.config["MATERIAL_UPLOAD_DIR"]
    return send_from_directory(
        str(upload_dir),
        mat.stored_filename,
        as_attachment=True,
        download_name=mat.original_filename,
    )


@materials_bp.route("/delete/<int:material_id>", methods=["POST"])
@login_required
@teacher_required
def delete(material_id):
    mat = StudyMaterial.query.get_or_404(material_id)
    # Ownership check: teachers can only delete their own materials
    if mat.uploaded_by != current_user.id:
        abort(403)

    # Delete the file from disk first
    file_path = current_app.config["MATERIAL_UPLOAD_DIR"] / mat.stored_filename
    if file_path.exists():
        file_path.unlink()

    db.session.delete(mat)
    db.session.commit()
    log_activity(current_user.id, "delete_material",
                 f"Deleted: {mat.original_filename}")
    flash("Material deleted.", "success")
    return redirect(url_for("materials.index"))
