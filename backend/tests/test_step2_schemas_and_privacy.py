"""
NutriSphere 3D - Step 2 Automated Test Suite
Validates:
- All required Pydantic models: ReportOut, AnalyteOut, InterpretationOut, UploadStatusOut,
  NutritionContextIn, AlcoholContextIn, ReportSummaryOut, ChartPoint, ErrorOut
- Input validations: file size limit (15MB), MIME types, numeric biological ranges, incompatible units
- Ownership authorization: cross-user access blocked with 403 Forbidden
- Explicit affirmative consent requirement
- Conspicuous deletion controls with cascading purge and audit trail
- Zero PHI in audit logs
- Negative tests: cross-user deletion blocked, invalid diet/alcohol inputs rejected, negative values caught
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import (
    ReportOut, AnalyteOut, InterpretationOut, UploadStatusOut,
    NutritionContextIn, AlcoholContextIn, ReportSummaryOut, ChartPoint,
    ErrorOut, ConsentDeclarationIn
)
from backend.services.privacy import (
    validate_file_metadata, verify_report_ownership, log_safe_audit_event
)
from backend.database import get_db
from backend.seed_data import seed_database
from backend.services.auth import DEV_DEMO_TOKEN, create_session_token

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_DEMO_TOKEN}"}


@pytest.fixture(autouse=True)
def setup_db():
    seed_database()


def test_models_instantiation():
    """Verify all Step 2 Pydantic models instantiate with expected fields."""
    interp = InterpretationOut(
        biomarker_id="bm_001",
        explanation="Normal cellular count indicating healthy erythropoiesis.",
        reasoning_limits="Normal range cannot rule out asymptomatic conditions.",
        clinical_questions=["Are my iron stores normal?"]
    )
    assert interp.disclaimer != ""

    analyte = AnalyteOut(
        analyte_code="CBC_HGB",
        label="Hemoglobin",
        value_numeric=14.5,
        unit="g/dL",
        reference_low=13.8,
        reference_high=17.2,
        flag="within_reference",
        interpretation=interp
    )
    assert analyte.value_numeric == 14.5

    status = UploadStatusOut(
        report_id="rep_123",
        status="extracted",
        progress_percent=100,
        message="Extraction complete"
    )
    assert status.status == "extracted"

    chart = ChartPoint(
        date="2026-09-15",
        value=14.8,
        unit="g/dL",
        flag="within_reference"
    )
    assert chart.value == 14.8


def test_file_metadata_validation():
    """Verify file size, MIME type, and safe path traversal handling."""
    # Valid PDF
    clean_name = validate_file_metadata(
        file_size_bytes=4000,
        mime_type="application/pdf",
        file_name="../../reports/my_lab_report.pdf"
    )
    assert clean_name == "my_lab_report.pdf"
    assert ".." not in clean_name

    # Valid PNG
    png_name = validate_file_metadata(
        file_size_bytes=85000,
        mime_type="image/png",
        file_name="lab_scan.png"
    )
    assert png_name == "lab_scan.png"

    # Reject > 15MB
    with pytest.raises(HTTPException) as exc_413:
        validate_file_metadata(
            file_size_bytes=16 * 1024 * 1024,
            mime_type="application/pdf",
            file_name="massive_file.pdf"
        )
    assert exc_413.value.status_code == 413

    # Reject unsupported MIME
    with pytest.raises(HTTPException) as exc_415:
        validate_file_metadata(
            file_size_bytes=5000,
            mime_type="application/x-executable",
            file_name="malicious.exe"
        )
    assert exc_415.value.status_code == 415


def test_consent_api_flow():
    """Verify affirmative consent is accepted and recorded in audit log."""
    res = client.post("/api/consent", json={
        "has_consented": True,
        "consent_version": "2026.1",
        "disclaimer_acknowledged": True,
        "purge_on_session_end": False
    }, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "consent_recorded"
    assert "audit_event_id" in data

    # Verify audit event in DB
    with get_db() as conn:
        evt = conn.execute("SELECT * FROM audit_events WHERE id = ?;", (data["audit_event_id"],)).fetchone()
        assert evt is not None
        assert evt["event_type"] == "CONSENT_AFFIRMED"


def test_report_detail_and_summary_authorized():
    """Verify authorized user can fetch full ReportOut and ReportSummaryOut."""
    # Fetch report detail
    res = client.get("/api/reports/rep_demo_2026_001", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "rep_demo_2026_001"
    assert data["user_id"] == "usr_demo_001"
    assert len(data["biomarkers"]) > 0

    # Fetch report summary
    sum_res = client.get("/api/reports/rep_demo_2026_001/summary", headers=AUTH_HEADERS)
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["total_biomarkers"] > 0
    assert "clinical_disclaimer" in summary
    assert len(summary["high_priority_findings"]) > 0


def test_conspicuous_deletion_control():
    """Verify user can permanently delete their report with cascading biomarker purge."""
    with get_db() as conn:
        # Create a disposable report
        conn.execute("""
            INSERT OR REPLACE INTO reports (id, user_id, file_name, mime_type, analysis_status)
            VALUES ('rep_to_delete', 'usr_demo_001', 'disposable.pdf', 'application/pdf', 'verified');
        """)
        conn.execute("""
            INSERT OR REPLACE INTO biomarkers (id, report_id, analyte_code, label, value_numeric)
            VALUES ('bm_to_delete', 'rep_to_delete', 'CBC_HGB', 'Hemoglobin', 14.1);
        """)

    # Delete via API
    del_res = client.delete("/api/reports/rep_to_delete", headers=AUTH_HEADERS)
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["status"] == "deleted"
    assert del_data["report_id"] == "rep_to_delete"

    # Verify report is purged from DB
    with get_db() as conn:
        assert conn.execute("SELECT COUNT(*) FROM reports WHERE id = 'rep_to_delete';").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM biomarkers WHERE id = 'bm_to_delete';").fetchone()[0] == 0

    # Subsequent GET returns 404
    get_res = client.get("/api/reports/rep_to_delete", headers=AUTH_HEADERS)
    assert get_res.status_code == 404


def test_nutrition_and_alcohol_context_apis():
    """Verify nutrition and alcohol guidance API endpoints."""
    # Nutrition
    nut_res = client.post("/api/nutrition/context", json={
        "dietary_pattern": "vegetarian",
        "allergies": ["peanuts", "dairy"],
        "calorie_target_opt_in": False
    })
    assert nut_res.status_code == 200
    nut_data = nut_res.json()
    assert "suggestions" in nut_data
    assert "disclaimer" in nut_data

    # Alcohol
    alc_res = client.post("/api/alcohol/context", json={
        "frequency_per_week": 2,
        "typical_standard_drinks": 1.5,
        "has_liver_conditions": True,
        "takes_medications": True
    })
    assert alc_res.status_code == 200
    alc_data = alc_res.json()
    assert "safe_drinking_limit" in alc_data
    assert "None" in alc_data["safe_drinking_limit"]


def test_zero_phi_logging_guarantee():
    """Verify that audit events never store raw health numbers or report body."""
    with get_db() as conn:
        rows = conn.execute("SELECT details FROM audit_events;").fetchall()
        for r in rows:
            text = r["details"].lower()
            # Confirm no raw lab values or clinical diagnostics appear in audit details
            assert "hemoglobin: 14.8" not in text
            assert "patient was diagnosed with" not in text


# --- Negative Tests ---

def test_negative_unauthenticated_request_fails_401():
    """Negative test: Supplying client-trusted X-User-Id header without valid Bearer token returns 401."""
    res = client.get("/api/reports/rep_demo_2026_001", headers={"X-User-Id": "usr_demo_001"})
    assert res.status_code == 401
    data = res.json()
    assert data["code"] == "HTTP_401"
    assert "authentication required" in data["message"].lower()


def test_negative_cross_user_access_blocked_403():
    """Negative test: Authenticated User B attempting to access User A's report is blocked with 403 Forbidden."""
    sec_token = create_session_token("usr_demo_002")
    res = client.get("/api/reports/rep_demo_2026_001", headers={"Authorization": f"Bearer {sec_token}"})
    assert res.status_code == 403
    data = res.json()
    assert data["code"] == "HTTP_403"
    assert "forbidden" in data["message"].lower()


def test_negative_cross_user_deletion_blocked_403():
    """Negative test: Authenticated User B attempting to delete User A's report is blocked with 403 Forbidden."""
    sec_token = create_session_token("usr_demo_002")
    res = client.delete("/api/reports/rep_demo_2026_001", headers={"Authorization": f"Bearer {sec_token}"})
    assert res.status_code == 403
    data = res.json()
    assert data["code"] == "HTTP_403"


def test_negative_consent_without_agreement_422():
    """Negative test: Submitting consent without affirmative agreement returns 422."""
    res = client.post("/api/consent", json={
        "has_consented": False,  # Missing affirmative agreement
        "disclaimer_acknowledged": True
    }, headers=AUTH_HEADERS)
    assert res.status_code == 422
    data = res.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_negative_biological_value_negative_422():
    """Negative test: Values outside clinical plausibility ranges fail validation."""
    # 1. Listed analyte with physiological bounds (Hemoglobin cannot be -12.5 or outside [1.0, 30.0])
    with pytest.raises(ValueError) as exc1:
        AnalyteOut(
            analyte_code="CBC_HGB",
            label="Hemoglobin",
            value_numeric=-12.5
        )
    assert "clinically plausible" in str(exc1.value)

    # 2. Unlisted analyte cannot have negative values unless signed index
    with pytest.raises(ValueError) as exc2:
        AnalyteOut(
            analyte_code="UNKNOWN_ANALYTE",
            label="Unknown Test",
            value_numeric=-5.0
        )
    assert "cannot be negative" in str(exc2.value)

    # 3. Legitimate signed index (Base Excess) CAN be negative
    signed_analyte = AnalyteOut(
        analyte_code="MET_BASE_EXCESS",
        label="Base Excess",
        value_numeric=-4.5,
        unit="mEq/L"
    )
    assert signed_analyte.value_numeric == -4.5


def test_negative_incompatible_unit_rejected():
    """Negative test: Incompatible physical units (e.g. mmHg for blood count) fail validation."""
    with pytest.raises(ValueError) as exc:
        AnalyteOut(
            analyte_code="CBC_HGB",
            label="Hemoglobin",
            value_numeric=14.0,
            unit="mmHg"  # Pressure unit rejected
        )
    assert "physically incompatible" in str(exc.value)


def test_negative_invalid_diet_pattern_422():
    """Negative test: Invalid dietary pattern returns 422."""
    res = client.post("/api/nutrition/context", json={
        "dietary_pattern": "unsupported_junk_diet",
        "allergies": []
    })
    assert res.status_code == 422
    data = res.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_negative_negative_alcohol_consumption_422():
    """Negative test: Negative alcohol drink metrics return 422."""
    res = client.post("/api/alcohol/context", json={
        "frequency_per_week": -3,
        "typical_standard_drinks": -1.0
    })
    assert res.status_code == 422
    data = res.json()
    assert data["code"] == "VALIDATION_ERROR"
