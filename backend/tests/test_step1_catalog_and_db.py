"""
NutriSphere 3D - Step 1 Automated Test Suite
Validates:
- Complete relational SQLite schema (users, reports, biomarkers, interpretations, medications, preferences, audit_events)
- Password security: Salted PBKDF2-HMAC-SHA256, zero plaintext password storage
- Test catalog breadth across 14+ panels (70+ analytes)
- Normalization engine: Synonyms, verified unit conversions (mmol/L, umol/L, g/L, nmol/L)
- Handling of unfamiliar test names, missing values, low-confidence OCR readings
- Foreign key cascading deletions
- Multiple negative tests: unfamiliar test, incompatible units, foreign key violation, 404 missing analyte
"""

import pytest
import sqlite3
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import get_db, init_db, hash_password, verify_password
from backend.services.normalizer import NormalizerService
from backend.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_database_seeded():
    """Ensure database is seeded before running tests."""
    seed_database()


def test_tables_exist_and_relational_schema():
    """Verify all 8 required tables exist with foreign keys enabled."""
    with get_db() as conn:
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        required_tables = [
            "users", "reports", "biomarkers", "interpretations",
            "medications", "nutrition_preferences", "audit_events", "test_catalog"
        ]
        for tbl in required_tables:
            assert tbl in tables, f"Table '{tbl}' is missing from database schema."

        # Verify foreign keys pragma is active
        fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_status == 1, "Foreign keys must be enabled (PRAGMA foreign_keys = 1)."


def test_user_password_security_zero_plaintext():
    """Verify local demo user password is saved only as salted PBKDF2 hash, never plaintext."""
    with get_db() as conn:
        user = conn.execute("SELECT username, password_hash, salt FROM users WHERE id = 'usr_demo_001';").fetchone()
        assert user is not None
        assert user["username"] == "demouser"
        
        # Verify password is not stored plaintext
        raw_password = "DemoPatient2026!"
        assert user["password_hash"] != raw_password
        assert len(user["salt"]) == 32  # 16-byte hex
        assert len(user["password_hash"]) == 64  # sha256 hex string

        # Verify correct verification logic
        assert verify_password(raw_password, user["salt"], user["password_hash"]) is True
        # Verify incorrect password rejected
        assert verify_password("WrongPassword123!", user["salt"], user["password_hash"]) is False


def test_user_api_endpoint_sanitization():
    """Verify GET /api/user/demo never exposes password_hash or salt in API responses."""
    response = client.get("/api/user/demo")
    assert response.status_code == 200
    data = response.json()
    assert "password_hash" not in data
    assert "salt" not in data
    assert data["username"] == "demouser"
    assert data["role"] == "demo_user"


def test_test_catalog_breadth_and_panels():
    """Verify extensive catalog coverage across 14+ clinical panels."""
    with get_db() as conn:
        panels = [r[0] for r in conn.execute("SELECT DISTINCT panel FROM test_catalog;").fetchall()]
        expected_panels = [
            "Hematology", "Liver", "Kidney", "Diabetes", "Lipid",
            "Thyroid", "Vitamins", "Minerals", "Iron", "Hormones",
            "Cardiac", "Inflammation", "Coagulation", "Urine"
        ]
        for ep in expected_panels:
            assert ep in panels, f"Panel '{ep}' must be present in the clinical catalog."

        count = conn.execute("SELECT COUNT(*) FROM test_catalog;").fetchone()[0]
        assert count >= 60, f"Expected at least 60 catalog analytes, found {count}."


def test_test_catalog_api_filtering():
    """Verify API queries by panel and text search."""
    # Filter by panel
    res_liver = client.get("/api/catalog?panel=Liver")
    assert res_liver.status_code == 200
    liver_data = res_liver.json()
    assert liver_data["total"] >= 5
    for item in liver_data["items"]:
        assert item["panel"].lower() == "liver"

    # Search by text
    res_search = client.get("/api/catalog?search=hemoglobin")
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["total"] >= 1
    codes = [item["analyte_code"] for item in search_data["items"]]
    assert "CBC_HGB" in codes


def test_normalizer_synonyms_resolution():
    """Verify flexible matching for aliases, clinical acronyms, and formatting."""
    norm = NormalizerService()
    assert norm.resolve_analyte("ALT") == "LIV_ALT"
    assert norm.resolve_analyte("SGPT") == "LIV_ALT"
    assert norm.resolve_analyte("Alanine Aminotransferase (ALT/SGPT)") == "LIV_ALT"
    assert norm.resolve_analyte("HbA1c") == "GLU_HBA1C"
    assert norm.resolve_analyte("Glycated Hemoglobin") == "GLU_HBA1C"
    assert norm.resolve_analyte("Fasting Blood Sugar") == "GLU_FASTING"
    assert norm.resolve_analyte("Serum Creatinine") == "KID_CREAT"
    assert norm.resolve_analyte("25-OH Vit D") == "VIT_D"
    assert norm.resolve_analyte("Platelet Count (PLT)") == "CBC_PLT"


def test_normalizer_unit_conversions():
    """Verify verified clinical unit conversions for SI and traditional units."""
    norm = NormalizerService()

    # 1. Glucose: 5.8 mmol/L -> 104.5 mg/dL
    glu = norm.normalize_biomarker({
        "label": "Fasting Plasma Glucose",
        "value_numeric": 5.8,
        "unit": "mmol/L",
        "extraction_confidence": 0.99
    })
    assert glu["analyte_code"] == "GLU_FASTING"
    assert glu["normalized_value"] == pytest.approx(104.5, abs=0.2)
    assert glu["standard_unit"] == "mg/dL"
    assert "Converted" in glu["unit_conversion_audit"]

    # 2. Total Cholesterol: 5.5 mmol/L -> 212.7 mg/dL
    chol = norm.normalize_biomarker({
        "label": "Total Cholesterol",
        "value_numeric": 5.5,
        "unit": "mmol/L"
    })
    assert chol["analyte_code"] == "LIP_CHOL"
    assert chol["normalized_value"] == pytest.approx(212.7, abs=0.5)

    # 3. Serum Creatinine: 88.4 umol/L -> 1.0 mg/dL
    creat = norm.normalize_biomarker({
        "label": "Creatinine",
        "value_numeric": 88.4,
        "unit": "umol/L"
    })
    assert creat["analyte_code"] == "KID_CREAT"
    assert creat["normalized_value"] == pytest.approx(1.0, abs=0.05)

    # 4. Hemoglobin: 140 g/L -> 14.0 g/dL
    hgb = norm.normalize_biomarker({
        "label": "Hemoglobin",
        "value_numeric": 140.0,
        "unit": "g/L"
    })
    assert hgb["analyte_code"] == "CBC_HGB"
    assert hgb["normalized_value"] == pytest.approx(14.0, abs=0.1)

    # 5. Vitamin D: 56.0 nmol/L -> 22.4 ng/mL
    vitd = norm.normalize_biomarker({
        "label": "25-OH Vitamin D",
        "value_numeric": 56.0,
        "unit": "nmol/L"
    })
    assert vitd["analyte_code"] == "VIT_D"
    assert vitd["normalized_value"] == pytest.approx(22.4, abs=0.2)


def test_normalizer_missing_values_and_low_confidence():
    """Verify missing test handling and human review prompt for ambiguous readings."""
    norm = NormalizerService()

    # Missing / QNS value
    res_qns = norm.normalize_biomarker({
        "label": "Serum Ferritin",
        "value_numeric": None,
        "value_text": "QNS (Quantity Not Sufficient)",
        "unit": "ng/mL"
    })
    assert res_qns["is_missing"] is True
    assert res_qns["flag"] == "not_tested"

    # Ambiguous / Low confidence OCR reading (< 0.85)
    res_ocr = norm.normalize_biomarker({
        "label": "ALT",
        "value_numeric": 45.0,
        "unit": "U/L",
        "extraction_confidence": 0.65
    })
    assert res_ocr["needs_human_verification"] is True


def test_cascade_deletion_foreign_keys():
    """Verify that deleting a report cleanly cascades to deleting its biomarkers."""
    with get_db() as conn:
        cursor = conn.cursor()
        # Create a test report
        test_rep_id = "rep_test_cascade_99"
        cursor.execute("""
            INSERT INTO reports (id, user_id, file_name, mime_type, analysis_status)
            VALUES (?, 'usr_demo_001', 'temp_cascade_test.pdf', 'application/pdf', 'verified');
        """, (test_rep_id,))
        # Insert a biomarker under this report
        cursor.execute("""
            INSERT INTO biomarkers (id, report_id, analyte_code, label, value_numeric, unit)
            VALUES ('bm_cascade_01', ?, 'CBC_HGB', 'Hemoglobin', 14.2, 'g/dL');
        """, (test_rep_id,))

        # Verify biomarker exists
        assert cursor.execute("SELECT COUNT(*) FROM biomarkers WHERE id = 'bm_cascade_01';").fetchone()[0] == 1

        # Delete the report
        cursor.execute("DELETE FROM reports WHERE id = ?;", (test_rep_id,))

        # Verify child biomarker was automatically deleted via CASCADE
        assert cursor.execute("SELECT COUNT(*) FROM biomarkers WHERE id = 'bm_cascade_01';").fetchone()[0] == 0


# --- Negative Tests ---

def test_negative_unfamiliar_test_name():
    """Negative test: An uncataloged test is preserved as UNKNOWN_ANALYTE, not silently dropped."""
    norm = NormalizerService()
    res = norm.normalize_biomarker({
        "label": "Experimental Biomarker Z-449",
        "value_numeric": 12.5,
        "unit": "ug/mL"
    })
    assert res["analyte_code"] == "UNKNOWN_ANALYTE"
    assert res["is_recognized"] is False
    assert res["flag"] == "unclassified"
    assert res["label"] == "Experimental Biomarker Z-449"
    assert res["raw_value_numeric"] == 12.5


def test_negative_incompatible_units():
    """Negative test: Physically incompatible units are detected and rejected from conversion."""
    norm = NormalizerService()
    res = norm.normalize_biomarker({
        "label": "Hemoglobin",
        "value_numeric": 120.0,
        "unit": "mmHg"  # Incompatible pressure unit for hemoglobin
    })
    assert res["is_compatible_units"] is False
    assert res["flag"] == "incompatible_units"
    assert res["normalized_value"] is None


def test_negative_foreign_key_violation():
    """Negative test: Inserting a biomarker with a nonexistent report_id fails with IntegrityError."""
    with get_db() as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO biomarkers (id, report_id, analyte_code, label, value_numeric)
                VALUES ('bm_invalid_fk', 'nonexistent_rep_9999', 'CBC_HGB', 'Hemoglobin', 15.0);
            """)


def test_negative_missing_catalog_analyte_404():
    """Negative test: Requesting an uncataloged analyte code returns HTTP 404."""
    res = client.get("/api/catalog/NONEXISTENT_CODE_XYZ")
    assert res.status_code == 404
    data = res.json()
    assert data["code"] == "ANALYTE_NOT_FOUND"
