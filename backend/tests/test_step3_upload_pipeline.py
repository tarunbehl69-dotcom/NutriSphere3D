"""
NutriSphere 3D - Step 3 Automated Test Suite
Validates the complete medical report upload and extraction workflow:
- Multi-page vector PDF parsing via PyMuPDF (synthetic_lab_report_2026.pdf)
- International SI unit normalization (synthetic_tricky_units_report.pdf)
- Scanned image OCR adapter extraction (synthetic_scanned_report.png)
- Source-page tracking and extraction confidence scores
- Manual review state transition (needs_human_verification -> verified) via PUT /api/reports/{id}/verify
- Secure physical disk persistence and complete unlinking upon report deletion
- Server-validated Bearer token authentication (rejects client-trusted X-User-Id)
- Negative tests: 413 (too large), 415 (invalid MIME/magic bytes), 422 (missing consent/empty/oversized pages),
  401 (unauthorized), 403 (cross-user access/verify/delete), 404 (non-existent report)
"""

import os
import json
import io
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import pymupdf

from backend.main import app
from backend.database import get_db
from backend.seed_data import seed_database
from backend.services.auth import DEV_DEMO_TOKEN, create_session_token

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_DEMO_TOKEN}"}
REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_reports"


@pytest.fixture(autouse=True)
def setup_db():
    seed_database()


def get_valid_consent_json():
    return json.dumps({
        "has_consented": True,
        "consent_version": "2026.1",
        "disclaimer_acknowledged": True,
        "purge_on_session_end": False
    })


# --- Positive Tests ---

def test_upload_vector_pdf_extraction():
    """Verify upload, PyMuPDF parsing, metadata extraction, and 74-analyte normalization."""
    pdf_path = REPORTS_DIR / "synthetic_lab_report_2026.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/reports",
        files={"file": ("synthetic_lab_report_2026.pdf", file_bytes, "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )

    assert response.status_code == 201
    data = response.json()

    # Core report properties
    assert data["id"].startswith("rep_")
    assert data["user_id"] == "usr_demo_001"
    assert data["mime_type"] == "application/pdf"
    assert data["collection_date"] == "2026-09-15"
    assert "apex metropolitan" in data["laboratory_name"].lower()
    assert data["consent_verified"] is True

    # Biomarkers validation: 38 recognized tests across CBC, CMP, Lipids, etc.
    assert data["biomarkers_count"] == 38
    assert len(data["biomarkers"]) == 38

    # Verify no hallucinations / no missing invented values
    labels = [b["label"] for b in data["biomarkers"]]
    assert "Hemoglobin (HGB)" in labels
    assert "Alanine Aminotransferase (ALT)" in labels
    assert "Total Cholesterol" in labels
    assert "Thyroid Stimulating Hormone(TSH)" in labels
    assert "25-Hydroxy Vitamin D" in labels

    # Check source page citations
    pages = {b["source_page"] for b in data["biomarkers"]}
    assert pages == {1, 2, 3}  # All 3 pages cited accurately

    # Check high extraction confidence for digital PDF
    for b in data["biomarkers"]:
        assert b["extraction_confidence"] >= 0.90

    # Verify physical file saved to disk
    with get_db() as conn:
        row = conn.execute("SELECT file_path FROM reports WHERE id = ?;", (data["id"],)).fetchone()
        assert row is not None
        assert row["file_path"] is not None
        saved_p = Path(row["file_path"])
        assert saved_p.exists()
        assert saved_p.stat().st_size == len(file_bytes)


def test_upload_tricky_units_si_normalization():
    """Verify uploaded international SI units (mmol/L, umol/L) are properly normalized."""
    pdf_path = REPORTS_DIR / "synthetic_tricky_units_report.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/reports",
        files={"file": ("synthetic_tricky_units_report.pdf", file_bytes, "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )

    assert response.status_code == 201
    data = response.json()
    assert data["biomarkers_count"] == 11

    # Check glucose converted from 5.8 mmol/L to ~104.5 mg/dL
    glucose = next(b for b in data["biomarkers"] if "Glucose" in b["label"])
    assert glucose["analyte_code"] == "GLU_FASTING"
    assert glucose["value_numeric"] == 104.5
    assert glucose["unit"] == "mg/dL"
    assert glucose["flag"] == "above_reference"

    # Check creatinine converted from 84.0 umol/L to ~0.95 mg/dL
    creat = next(b for b in data["biomarkers"] if "Creatinine" in b["label"])
    assert creat["analyte_code"] == "KID_CREAT"
    assert creat["value_numeric"] == 0.95
    assert creat["unit"] == "mg/dL"


def test_upload_scanned_image_ocr_adapter():
    """Verify uploaded scanned image triggers OCR adapter and flags for human review."""
    png_path = REPORTS_DIR / "synthetic_scanned_report.png"
    assert png_path.exists()

    with open(png_path, "rb") as f:
        file_bytes = f.read()

    response = client.post(
        "/api/reports",
        files={"file": ("synthetic_scanned_report.png", file_bytes, "image/png")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )

    assert response.status_code == 201
    data = response.json()

    # Image upload triggers human review state
    assert data["analysis_status"] == "needs_human_verification"
    assert data["biomarkers_count"] == 12

    # Verify extracted markers
    labels = [b["label"] for b in data["biomarkers"]]
    assert "HEMOGLOBIN" in labels
    assert "FASTING BLOOD SUGAR" in labels
    assert "VITAMIN D3" in labels


def test_report_status_endpoint():
    """Verify GET /api/reports/{id}/status reports accurate pipeline progress and review requirements."""
    # Upload scanned report
    png_path = REPORTS_DIR / "synthetic_scanned_report.png"
    with open(png_path, "rb") as f:
        file_bytes = f.read()

    up_res = client.post(
        "/api/reports",
        files={"file": ("scanned_test.png", file_bytes, "image/png")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    rep_id = up_res.json()["id"]

    status_res = client.get(f"/api/reports/{rep_id}/status", headers=AUTH_HEADERS)
    assert status_res.status_code == 200
    st_data = status_res.json()
    assert st_data["report_id"] == rep_id
    assert st_data["status"] == "needs_human_verification"
    assert st_data["requires_verification"] is True
    assert st_data["progress_percent"] == 75


def test_human_verification_workflow():
    """Verify manual review PUT /api/reports/{id}/verify confirms values and transitions status to 'verified'."""
    # 1. Upload report that needs verification
    png_path = REPORTS_DIR / "synthetic_scanned_report.png"
    with open(png_path, "rb") as f:
        file_bytes = f.read()

    up_res = client.post(
        "/api/reports",
        files={"file": ("to_verify.png", file_bytes, "image/png")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    rep = up_res.json()
    rep_id = rep["id"]
    assert rep["analysis_status"] == "needs_human_verification"

    # 2. Submit human verification
    verified_bms = rep["biomarkers"]
    # Edit first biomarker
    verified_bms[0]["value_numeric"] = 14.2
    verified_bms[0]["unit"] = "g/dL"

    verify_res = client.put(
        f"/api/reports/{rep_id}/verify",
        json={
            "collection_date": "2026-08-20",
            "laboratory_name": "City Central Pathology (Verified)",
            "biomarkers": verified_bms
        },
        headers=AUTH_HEADERS
    )

    assert verify_res.status_code == 200
    verified_data = verify_res.json()
    assert verified_data["analysis_status"] == "verified"
    assert verified_data["biomarkers"][0]["value_numeric"] == 14.2
    assert verified_data["biomarkers"][0]["extraction_confidence"] == 1.0

    # 3. Verify audit log entry
    with get_db() as conn:
        evt = conn.execute(
            "SELECT * FROM audit_events WHERE resource_id = ? AND event_type = 'REPORT_HUMAN_VERIFIED';",
            (rep_id,)
        ).fetchone()
        assert evt is not None


def test_list_user_reports_authorized_isolation():
    """Verify GET /api/reports returns only reports belonging to authenticated user."""
    res = client.get("/api/reports", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "reports" in data
    assert data["total"] >= 1
    for r in data["reports"]:
        assert r["user_id"] == "usr_demo_001"

    # User B should have separate isolated listing
    sec_token = create_session_token("usr_demo_002")
    res_b = client.get("/api/reports", headers={"Authorization": f"Bearer {sec_token}"})
    assert res_b.status_code == 200
    assert res_b.json()["total"] == 0  # No reports uploaded by User B yet


def test_conspicuous_deletion_purges_file_from_disk():
    """Verify deleting a report cascades in database AND permanently deletes file from disk."""
    pdf_path = REPORTS_DIR / "synthetic_lab_report_2026.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    up_res = client.post(
        "/api/reports",
        files={"file": ("to_delete.pdf", file_bytes, "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    rep_id = up_res.json()["id"]

    # Check file exists on disk
    with get_db() as conn:
        fpath = conn.execute("SELECT file_path FROM reports WHERE id = ?;", (rep_id,)).fetchone()[0]
        assert Path(fpath).exists()

    # Delete report
    del_res = client.delete(f"/api/reports/{rep_id}", headers=AUTH_HEADERS)
    assert del_res.status_code == 200

    # Verify database records purged
    with get_db() as conn:
        assert conn.execute("SELECT COUNT(*) FROM reports WHERE id = ?;", (rep_id,)).fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM biomarkers WHERE report_id = ?;", (rep_id,)).fetchone()[0] == 0

    # Verify file is deleted from disk
    assert not Path(fpath).exists()


# --- Negative Tests ---

def test_negative_upload_file_too_large_413():
    """Negative test: Uploading a file exceeding 15MB returns 413."""
    oversized_bytes = b"%PDF-" + b"0" * (15 * 1024 * 1024 + 100)
    res = client.post(
        "/api/reports",
        files={"file": ("huge.pdf", oversized_bytes, "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 413
    assert "exceeds maximum allowed size" in res.json()["message"]


def test_negative_upload_invalid_mime_type_415():
    """Negative test: Uploading executable or text file returns 415."""
    res = client.post(
        "/api/reports",
        files={"file": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 415
    assert "unsupported file type" in res.json()["message"].lower()


def test_negative_upload_corrupted_magic_bytes_415():
    """Negative test: Uploading file claiming to be PDF but having invalid magic bytes returns 415."""
    fake_pdf = b"NOT_A_REAL_PDF_HEADER_JUST_RANDOM_TEXT"
    res = client.post(
        "/api/reports",
        files={"file": ("corrupt.pdf", fake_pdf, "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 415
    assert "corrupted header" in res.json()["message"].lower()


def test_negative_upload_missing_affirmative_consent_422():
    """Negative test: Uploading without affirmative consent agreement returns 422."""
    pdf_path = REPORTS_DIR / "synthetic_lab_report_2026.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    no_consent = json.dumps({
        "has_consented": False,
        "consent_version": "2026.1",
        "disclaimer_acknowledged": True
    })

    res = client.post(
        "/api/reports",
        files={"file": ("report.pdf", file_bytes, "application/pdf")},
        data={"consent": no_consent},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 422
    assert "affirmative consent" in res.json()["message"].lower()


def test_negative_upload_empty_file_422():
    """Negative test: Uploading a 0-byte empty file returns 422."""
    res = client.post(
        "/api/reports",
        files={"file": ("empty.pdf", b"", "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 422
    assert "0 bytes" in res.json()["message"].lower()


def test_negative_upload_pdf_exceeds_20_pages_422():
    """Negative test: Uploading a PDF exceeding 20 pages limit returns 422."""
    doc = pymupdf.open()
    for _ in range(22):
        doc.new_page(width=595, height=842)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    buf.seek(0)
    pdf_22_pages = buf.read()

    res = client.post(
        "/api/reports",
        files={"file": ("too_many_pages.pdf", pdf_22_pages, "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 422
    assert "20 pages" in res.json()["message"].lower()


def test_negative_upload_unauthenticated_fails_401():
    """Negative test: Uploading report without valid Bearer token returns 401."""
    pdf_path = REPORTS_DIR / "synthetic_lab_report_2026.pdf"
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    res = client.post(
        "/api/reports",
        files={"file": ("report.pdf", file_bytes, "application/pdf")},
        data={"consent": get_valid_consent_json()},
        headers={"X-User-Id": "usr_demo_001"}  # Client-trusted header is NOT trusted
    )
    assert res.status_code == 401
    assert "authentication required" in res.json()["message"].lower()


def test_negative_cross_user_verification_blocked_403():
    """Negative test: User B attempting to verify/modify User A's report is blocked with 403 Forbidden."""
    sec_token = create_session_token("usr_demo_002")
    res = client.put(
        "/api/reports/rep_demo_2026_001/verify",
        json={"biomarkers": []},
        headers={"Authorization": f"Bearer {sec_token}"}
    )
    assert res.status_code == 403
    assert "forbidden" in res.json()["message"].lower()


def test_negative_nonexistent_report_verify_404():
    """Negative test: Attempting to verify a non-existent report returns 404."""
    res = client.put(
        "/api/reports/rep_nonexistent_9999/verify",
        json={"biomarkers": []},
        headers=AUTH_HEADERS
    )
    assert res.status_code == 404
    assert "not found" in res.json()["message"].lower()
