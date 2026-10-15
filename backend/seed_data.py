"""
NutriSphere 3D - Seed Data Loader
Loads non-patient synthetic data from CSV and JSON into SQLite demo database,
and manages sample demonstration reports (PDF, PNG, JSON).
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.database import get_db, init_db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CATALOG_CSV_PATH = DATA_DIR / "test_catalog_seed.csv"
DEMO_REPORT_PATH = DATA_DIR / "demo_report.json"
HISTORICAL_REPORTS_PATH = DATA_DIR / "historical_reports.json"
SAMPLE_REPORTS_DIR = DATA_DIR / "sample_reports"


def load_test_catalog() -> List[Dict[str, Any]]:
    """Load test catalog seed definitions from CSV."""
    if not CATALOG_CSV_PATH.exists():
        return []
    records = []
    with open(CATALOG_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def load_demo_report() -> Dict[str, Any]:
    """Load synthetic demo report fixture."""
    if not DEMO_REPORT_PATH.exists():
        return {}
    with open(DEMO_REPORT_PATH, mode="r", encoding="utf-8") as f:
        return json.load(f)


def load_historical_reports() -> Dict[str, Any]:
    """Load longitudinal multi-year synthetic health records."""
    if not HISTORICAL_REPORTS_PATH.exists():
        return {}
    with open(HISTORICAL_REPORTS_PATH, mode="r", encoding="utf-8") as f:
        return json.load(f)


def list_sample_reports() -> List[Dict[str, Any]]:
    """List available sample demonstration reports with metadata."""
    if not SAMPLE_REPORTS_DIR.exists():
        return []
    
    samples = []
    file_metadata = {
        "synthetic_lab_report_2026.pdf": {
            "title": "Comprehensive Annual Health Panel (2026)",
            "description": "Multi-page PDF with selectable text (CBC, CMP, Lipids, Thyroid, Vitamins)",
            "type": "application/pdf",
            "pages": 3,
            "format": "Vector PDF (Selectable text)"
        },
        "synthetic_scanned_report.png": {
            "title": "Archival Scanned Lab Slip",
            "description": "High-contrast scanned pathology slip designed for OCR pipeline evaluation",
            "type": "image/png",
            "pages": 1,
            "format": "Scanned Image (OCR target)"
        },
        "synthetic_tricky_units_report.pdf": {
            "title": "International SI Units Panel (Tricky Conversions)",
            "description": "SI units test case (mmol/L, umol/L, g/L) for unit normalization verification",
            "type": "application/pdf",
            "pages": 1,
            "format": "Vector PDF (SI Units)"
        }
    }

    for file_path in sorted(SAMPLE_REPORTS_DIR.iterdir()):
        if file_path.is_file() and not file_path.name.startswith("."):
            info = file_metadata.get(file_path.name, {
                "title": file_path.name,
                "description": "Synthetic medical report sample",
                "type": "application/octet-stream",
                "pages": 1,
                "format": file_path.suffix.upper()
            })
            samples.append({
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "download_url": f"/api/sample-reports/{file_path.name}",
                **info
            })
    return samples


def get_sample_report_path(filename: str) -> Optional[Path]:
    """Retrieve absolute path to a sample report file safely."""
    safe_path = (SAMPLE_REPORTS_DIR / filename).resolve()
    if safe_path.exists() and safe_path.is_file() and safe_path.parent == SAMPLE_REPORTS_DIR.resolve():
        return safe_path
    return None


def seed_database():
    """Seed test_catalog, reports, biomarkers, interpretations, and medications into SQLite."""
    init_db()

    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Seed test catalog from CSV
        catalog_items = load_test_catalog()
        for item in catalog_items:
            ref_low = float(item["reference_low"]) if item.get("reference_low") and item["reference_low"].strip() else None
            ref_high = float(item["reference_high"]) if item.get("reference_high") and item["reference_high"].strip() else None

            cursor.execute("""
                INSERT OR REPLACE INTO test_catalog (
                    analyte_code, canonical_name, panel, aliases, standard_unit,
                    acceptable_units, unit_conversions, reference_low, reference_high,
                    reference_text, contextual_ranges, organ_system, educational_explanation,
                    clinical_questions, medical_references
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                item["analyte_code"],
                item["canonical_name"],
                item["panel"],
                item.get("aliases", ""),
                item["standard_unit"],
                item.get("acceptable_units", item["standard_unit"]),
                "{}",
                ref_low,
                ref_high,
                item.get("reference_text", ""),
                "{}",
                item["organ_system"],
                item.get("description", ""),
                item.get("clinical_questions", ""),
                item.get("medical_references", "")
            ))

        # 2. Seed demo report and biomarkers
        demo = load_demo_report()
        meta = demo.get("report_metadata", {})
        demo_report_id = meta.get("report_id", "rep_demo_2026_001")
        demo_user_id = "usr_demo_001"

        cursor.execute("""
            INSERT OR REPLACE INTO reports (
                id, user_id, file_name, mime_type, file_size_bytes, collection_date,
                laboratory_name, analysis_status, extraction_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            demo_report_id,
            demo_user_id,
            meta.get("file_name", "synthetic_annual_health_screen_2026.pdf"),
            "application/pdf",
            4229,
            meta.get("collection_date", "2026-09-15"),
            meta.get("laboratory", "Apex Metropolitan Diagnostics"),
            "verified",
            "Non-patient synthetic demo specimen."
        ))

        # Biomarkers & interpretations
        for idx, bm in enumerate(demo.get("biomarkers", [])):
            bm_id = f"bm_demo_{idx+1:03d}"
            cursor.execute("""
                INSERT OR REPLACE INTO biomarkers (
                    id, report_id, analyte_code, label, value_numeric, value_text,
                    unit, reference_low, reference_high, reference_text, flag,
                    collection_date, source_page, extraction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                bm_id,
                demo_report_id,
                bm["analyte_code"],
                bm["label"],
                bm.get("value_numeric"),
                bm.get("value_text"),
                bm.get("unit"),
                bm.get("reference_low"),
                bm.get("reference_high"),
                f"{bm.get('reference_low', '')} - {bm.get('reference_high', '')} {bm.get('unit', '')}",
                bm.get("flag", "unknown"),
                meta.get("collection_date", "2026-09-15"),
                bm.get("source_page", 1),
                bm.get("extraction_confidence", 1.0)
            ))

            # Interpretation for this biomarker
            interp_id = f"int_demo_{idx+1:03d}"
            explanation = (
                f"Reported value {bm.get('value_numeric')} {bm.get('unit')} is evaluated in relation "
                f"to the laboratory reference threshold [{bm.get('reference_low')} - {bm.get('reference_high')}]."
            )
            limits = "Values outside reference limits are not medical diagnoses. Physical examination and clinical context are essential."
            cursor.execute("""
                INSERT OR REPLACE INTO interpretations (
                    id, biomarker_id, explanation, reasoning_limits, followup, clinical_questions, medical_reference
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                interp_id,
                bm_id,
                explanation,
                limits,
                "Consult with treating physician for clinical correlation.",
                "How does this finding correlate with my personal symptoms and health history?",
                "Mayo Clinic Laboratories / AACC"
            ))

        # 3. Seed historical reports (2024, 2025)
        hist = load_historical_reports()
        for series_item in hist.get("series", []):
            rep_id = series_item["report_id"]
            if rep_id == demo_report_id:
                continue  # already inserted above
            cursor.execute("""
                INSERT OR REPLACE INTO reports (
                    id, user_id, file_name, mime_type, file_size_bytes, collection_date,
                    laboratory_name, analysis_status, extraction_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                rep_id,
                demo_user_id,
                f"{rep_id}.pdf",
                "application/pdf",
                3800,
                series_item["collection_date"],
                series_item.get("laboratory", "Apex Metropolitan Diagnostics"),
                "verified",
                "Historical longitudinal synthetic record."
            ))

            for m_code, m_val in series_item.get("markers", []).items():
                hist_bm_id = f"bm_{rep_id}_{m_code}"
                cursor.execute("""
                    INSERT OR REPLACE INTO biomarkers (
                        id, report_id, analyte_code, label, value_numeric, value_text,
                        unit, reference_low, reference_high, reference_text, flag,
                        collection_date, source_page, extraction_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    hist_bm_id,
                    rep_id,
                    m_code,
                    m_code,
                    m_val.get("value"),
                    None,
                    m_val.get("unit"),
                    None,
                    None,
                    None,
                    m_val.get("flag", "unknown"),
                    series_item["collection_date"],
                    1,
                    1.0
                ))

        # 4. Seed opt-in structured medications context for demo user
        meds = [
            ("med_demo_001", demo_user_id, demo_report_id, "Cholecalciferol (Vitamin D3)", "2000 IU", "Once daily with morning meal", "2026-01-15"),
            ("med_demo_002", demo_user_id, None, "Omega-3 Fatty Acids (Fish Oil)", "1000 mg", "Once daily", "2025-06-01")
        ]
        for m_id, u_id, r_id, drug, dose, freq, start in meds:
            cursor.execute("""
                INSERT OR REPLACE INTO medications (id, user_id, report_id, drug_name, dosage, frequency, started_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1);
            """, (m_id, u_id, r_id, drug, dose, freq, start))

        # 5. Audit event
        cursor.execute("""
            INSERT OR REPLACE INTO audit_events (id, user_id, event_type, resource_id, details)
            VALUES ('evt_seed_002', ?, 'SEED_DATA', 'DB_ALL', 'Seeded extensive test catalog, demo report, historical records, and medications.');
        """, (demo_user_id,))


if __name__ == "__main__":
    seed_database()
    catalog = load_test_catalog()
    print(f"Loaded {len(catalog)} test catalog items into SQLite.")
    demo = load_demo_report()
    print(f"Loaded demo report for: {demo.get('patient_context', {}).get('identifier', 'N/A')}")
    hist = load_historical_reports()
    print(f"Loaded {len(hist.get('series', []))} historical series records.")
    samples = list_sample_reports()
    print(f"Found {len(samples)} sample report files.")
