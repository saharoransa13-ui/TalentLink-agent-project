"""Tests for the CV upload rules: English only, allowed types, size limit."""

import pytest
from fastapi.testclient import TestClient

from backend.cv_parser import MAX_FILE_BYTES, NotEnglishCVError, extract_text
from backend.main import app

ENGLISH_CV = (
    "Python developer. Built REST APIs with FastAPI and PostgreSQL. "
    "Deployed services with Docker and led a team of five engineers."
)
ARABIC_CV = (
    "مهندس برمجيات لديه خبرة ثلاث سنوات في تطوير الأنظمة باستخدام بايثون "
    "وقواعد البيانات، وعمل على مشاريع متعددة في شركات مختلفة."
)


def test_english_cv_is_accepted():
    assert "FastAPI" in extract_text("cv.txt", ENGLISH_CV.encode())


def test_english_cv_with_arabic_name_is_accepted():
    text = "أحمد علي محمد - بورسعيد\n" + ENGLISH_CV
    assert "Docker" in extract_text("cv.txt", text.encode())


def test_arabic_cv_is_rejected():
    with pytest.raises(NotEnglishCVError):
        extract_text("cv.txt", ARABIC_CV.encode())


def test_arabic_cv_with_some_english_terms_is_rejected():
    text = ARABIC_CV + " Python SQL Docker"
    with pytest.raises(NotEnglishCVError):
        extract_text("cv.txt", text.encode())


def test_unsupported_file_type_is_rejected():
    with pytest.raises(ValueError):
        extract_text("cv.jpg", b"fake image")


def test_too_large_file_is_rejected():
    with pytest.raises(ValueError):
        extract_text("cv.txt", b"a" * (MAX_FILE_BYTES + 1))


def test_analyze_endpoint_returns_cv_not_english_code():
    client = TestClient(app)
    response = client.post(
        "/analyze",
        files={"file": ("cv.txt", ARABIC_CV.encode(), "text/plain")},
        data={"role_id": "backend_developer"},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "cv_not_english"


def test_upload_errors_have_codes():
    client = TestClient(app)
    cases = [
        (("cv.jpg", b"fake", "image/jpeg"), "bad_file_type"),
        (("cv.pdf", b"not a real pdf", "application/pdf"), "pdf_unreadable"),
        (("cv.txt", b"   ", "text/plain"), "no_text"),
    ]
    for file_tuple, code in cases:
        response = client.post("/analyze", files={"file": file_tuple}, data={"role_id": "backend_developer"})
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == code


def test_report_includes_warning_codes(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(app)
    response = client.post(
        "/analyze",
        files={"file": ("cv.txt", b"Hello, I am a person who likes reading books.", "text/plain")},
        data={"role_id": "backend_developer"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "no_skills" in body["warning_codes"]
    assert len(body["warnings"]) >= len(body["warning_codes"])
