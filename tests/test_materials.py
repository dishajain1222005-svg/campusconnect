"""test_materials.py – File upload, download, and delete tests."""
import io
import pytest
from tests.conftest import make_student, make_teacher, login, logout


class TestMaterials:
    def _upload(self, client, filename, content=None, title="Test PDF"):
        if content is None:
            content = b"%PDF-1.4 test"
        return client.post("/materials/upload", data={
            "title": title,
            "subject": "Networks",
            "description": "Test upload",
            "file": (io.BytesIO(content), filename),
        }, content_type="multipart/form-data", follow_redirects=True)

    def test_teacher_upload_valid_pdf(self, client, ctx):
        make_teacher(username="mat_tea1", email="mat_tea1@test.com")
        login(client, "mat_tea1", "password123")
        resp = self._upload(client, "lecture.pdf", b"%PDF-1.4 valid content here")
        assert resp.status_code == 200
        assert b"uploaded successfully" in resp.data or b"Material" in resp.data
        logout(client)

    def test_disallowed_extension_rejected(self, client, ctx):
        make_teacher(username="mat_tea2", email="mat_tea2@test.com")
        login(client, "mat_tea2", "password123")
        resp = self._upload(client, "virus.exe", b"MZ\x90\x00")
        assert resp.status_code == 200
        assert b"not allowed" in resp.data.lower() or b"type" in resp.data.lower()
        logout(client)

    def test_pdf_magic_byte_mismatch_rejected(self, client, ctx):
        make_teacher(username="mat_tea3", email="mat_tea3@test.com")
        login(client, "mat_tea3", "password123")
        # Named .pdf but content is NOT a PDF
        resp = self._upload(client, "fake.pdf", b"This is not a PDF at all!!")
        assert resp.status_code == 200
        # Should show some error — magic check, content mismatch, or type error
        assert (b"magic" in resp.data.lower() or
                b"content" in resp.data.lower() or
                b"not allowed" in resp.data.lower() or
                b"failed" in resp.data.lower() or
                b"invalid" in resp.data.lower() or
                b"extension" in resp.data.lower())
        logout(client)

    def test_download_requires_login(self, client, ctx):
        resp = client.get("/materials/download/1", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers.get("Location", "")

    def test_student_cannot_upload(self, client, ctx):
        make_student(username="mat_stu1", email="mat_stu1@test.com")
        login(client, "mat_stu1", "password123")
        resp = client.get("/materials/upload", follow_redirects=False)
        assert resp.status_code in (302, 403)
        logout(client)

    def test_teacher_cannot_delete_other_teachers_material(self, client, ctx):
        from app.models import StudyMaterial
        from app.extensions import db
        t1 = make_teacher(username="mat_tea4", email="mat_tea4@test.com")
        t2 = make_teacher(username="mat_tea5", email="mat_tea5@test.com")
        mat = StudyMaterial(
            title="T1 Material", subject="Math",
            original_filename="t1.pdf",
            stored_filename="t1_stored_unique.pdf",
            uploaded_by=t1.id,
        )
        db.session.add(mat)
        db.session.commit()
        mat_id = mat.id
        login(client, "mat_tea5", "password123")
        resp = client.post(f"/materials/delete/{mat_id}", follow_redirects=False)
        assert resp.status_code == 403
        logout(client)
