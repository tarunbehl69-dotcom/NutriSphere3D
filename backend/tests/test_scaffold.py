"""
NutriSphere 3D - Automated Scaffold & Health Test Suite
Tests API endpoints, HTML page rendering, seed data integrity,
database initialization, service stubs, and negative error scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from backend.main import app
from backend.database import get_db, init_db
from backend.services.parser import ReportParserService
from backend.services.normalizer import NormalizerService
from backend.services.interpreter import ClinicalInterpretationService
from backend.services.nutrition import NutritionGuidanceService
from backend.services.alcohol import AlcoholEducationService

client = TestClient(app)


def test_health_check_endpoint():
    """Verify health endpoint returns 200, healthy status, and clinical disclaimer."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "educational" in data["clinical_notice"].lower()


def test_landing_page_serving():
    """Verify root route serves index.html with Three.js and branding."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "NutriSphere 3D" in response.text
    assert "three.min.js" in response.text


def test_all_frontend_pages_served():
    """Verify all four application pages are served successfully."""
    for path in ["/upload", "/results", "/dashboard"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "NutriSphere 3D" in response.text


def test_catalog_seed_endpoint():
    """Verify seed catalog returns loaded items with broad clinical coverage."""
    response = client.get("/api/catalog/seed")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 25
    
    # Check that diverse panels are represented
    analyte_codes = [item["analyte_code"] for item in data["items"]]
    assert "CBC_HGB" in analyte_codes
    assert "LIV_ALT" in analyte_codes
    assert "KID_CREAT" in analyte_codes
    assert "GLU_HBA1C" in analyte_codes
    assert "THY_TSH" in analyte_codes
    assert "VIT_D" in analyte_codes


def test_demo_report_fixture():
    """Verify demo report returns structured synthetic patient data."""
    response = client.get("/api/demo-report")
    assert response.status_code == 200
    data = response.json()
    assert data["report_metadata"]["is_synthetic"] is True
    assert len(data["biomarkers"]) > 0
    # Confirm confidence and page citations are present
    first_marker = data["biomarkers"][0]
    assert "source_page" in first_marker
    assert "extraction_confidence" in first_marker


def test_database_and_metadata():
    """Verify SQLite initialization, WAL mode, and system metadata record."""
    init_db()
    with get_db() as conn:
        row = conn.execute("SELECT value FROM system_metadata WHERE key = 'version';").fetchone()
        assert row is not None
        assert row["value"] == "0.1.0-scaffold"

        # Check PRAGMA settings
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        assert journal_mode.lower() == "wal"


def test_core_services():
    """Verify service class instantiation and baseline educational responses."""
    normalizer = NormalizerService()
    assert normalizer.resolve_analyte("hemoglobin") == "CBC_HGB"
    assert normalizer.resolve_analyte("sgpt") == "LIV_ALT"

    interpreter = ClinicalInterpretationService()
    res = interpreter.interpret_marker("LIV_ALT", 75.0, 7.0, 56.0, "U/L")
    assert res["flag"] == "above_reference"
    assert "disclaimer" in res

    nutrition = NutritionGuidanceService()
    nut_res = nutrition.get_suggestions(dietary_preference="vegetarian")
    assert len(nut_res["suggestions"]) > 0

    alcohol = AlcoholEducationService()
    alc_res = alcohol.get_risk_education(has_liver_flags=True)
    assert "safe_drinking_limit" in alc_res
    assert "None" in alc_res["safe_drinking_limit"]


def test_sample_reports_endpoints():
    """Verify sample reports listing and direct file downloads."""
    list_res = client.get("/api/sample-reports")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 3
    filenames = [s["filename"] for s in data["samples"]]
    assert "synthetic_lab_report_2026.pdf" in filenames
    assert "synthetic_scanned_report.png" in filenames
    assert "synthetic_tricky_units_report.pdf" in filenames

    # Verify download of synthetic PDF
    dl_res = client.get("/api/sample-reports/synthetic_lab_report_2026.pdf")
    assert dl_res.status_code == 200
    assert dl_res.headers["content-type"] == "application/pdf"
    assert dl_res.content.startswith(b"%PDF")


def test_historical_longitudinal_reports():
    """Verify multi-year longitudinal synthetic reports for trend analysis."""
    res = client.get("/api/reports/historical")
    assert res.status_code == 200
    data = res.json()
    assert "series" in data
    assert len(data["series"]) >= 3
    # Check that 2024, 2025, and 2026 are present
    years = [s["collection_date"][:4] for s in data["series"]]
    assert "2024" in years and "2025" in years and "2026" in years


def test_sample_reports_parser_compatibility():
    """Verify PyMuPDF and Pillow parser extract text from all synthetic fixtures."""
    parser = ReportParserService()

    # 1. Multi-page PDF
    pdf_path = Path("data/sample_reports/synthetic_lab_report_2026.pdf")
    pages = parser.extract_text_from_pdf(str(pdf_path))
    assert len(pages) == 3
    assert "Hemoglobin" in pages[0]["text"]
    assert "Alanine Aminotransferase" in pages[1]["text"]
    assert "Cholesterol" in pages[2]["text"]

    # 2. Scanned Image
    img_path = Path("data/sample_reports/synthetic_scanned_report.png")
    img_pages = parser.extract_text_from_image(str(img_path))
    assert len(img_pages) == 1
    assert img_pages[0]["is_ocr"] is True


def test_negative_invalid_endpoint_404():
    """Negative test: Requesting an invalid endpoint returns structured 404 ErrorOut."""
    response = client.get("/api/nonexistent-route-for-testing")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "NOT_FOUND"
    assert "not found" in data["message"].lower()


def test_negative_sample_report_not_found():
    """Negative test: Requesting a missing sample report returns 404 with SAMPLE_NOT_FOUND code."""
    response = client.get("/api/sample-reports/nonexistent_fake_report.pdf")
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "SAMPLE_NOT_FOUND"


def test_negative_missing_file_parsing():
    """Negative test: Parser raises FileNotFoundError when given a nonexistent file."""
    parser = ReportParserService()
    with pytest.raises(FileNotFoundError):
        parser.extract_text_from_pdf("nonexistent_path_report_123.pdf")
