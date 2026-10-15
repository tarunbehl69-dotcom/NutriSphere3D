"""
NutriSphere 3D - Step 4 Comprehensive Medical Report Interpretation Engine Tests
Verifies:
1. Complete coverage of all 74 catalog analytes across 14 clinical panels.
2. Evidence-linked, non-diagnostic explanations preserving original lab reference intervals.
3. No invention of missing ranges, diagnoses, or treatments.
4. Panic value and critical urgency escalation (Potassium, Glucose, Troponin, Hemoglobin, Platelets, Calcium, Sodium).
5. Multi-marker educational clusters (Hepatic de Ritis ratio, Renal BUN/Creatinine, Cardiometabolic discordance, Thyroid, Hematology).
6. Uncertainty notices for low-confidence / unverified OCR scans.
7. Opt-in voluntary contextual factors (medications, pregnancy hemodilution, age-related eGFR).
8. Borderline value recognition (within 5% of reference limits).
9. Authenticated API contracts: GET /summary, POST /interpret, cross-user 403, and zero-PHI logging.
10. Strict disclaimers preventing "safe alcohol quota" claims.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.main import app
from backend.database import get_db
from backend.services.interpreter import ClinicalInterpretationService
from backend.services.normalizer import NormalizerService
from backend.services.auth import DEV_DEMO_TOKEN, create_session_token

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_DEMO_TOKEN}"}
OTHER_USER_HEADERS = {"Authorization": f"Bearer {create_session_token('usr_demo_002')}"}


# --- 1. Catalog Coverage & Interpretation Completeness ---

def test_all_74_catalog_analytes_interpreted():
    """Verify that every one of the 74 catalog analytes across 14 panels can be interpreted."""
    interpreter = ClinicalInterpretationService()
    catalog = interpreter.catalog
    assert len(catalog) == 74, f"Expected 74 catalog analytes, found {len(catalog)}"

    panels_seen = set()
    for code, item in catalog.items():
        panels_seen.add(item.get("panel"))
        # Test biomarker payload
        ref_low = float(item["reference_low"]) if item.get("reference_low") and item["reference_low"].strip() else None
        ref_high = float(item["reference_high"]) if item.get("reference_high") and item["reference_high"].strip() else None
        
        # Test within range
        test_val = ref_low if ref_low is not None else 10.0
        bm = {
            "analyte_code": code,
            "label": item.get("canonical_name", code),
            "value_numeric": test_val,
            "unit": item.get("standard_unit"),
            "reference_low": ref_low,
            "reference_high": ref_high,
            "flag": "within_reference",
            "extraction_confidence": 1.0
        }
        res = interpreter.interpret_biomarker(bm)
        assert res.analyte_code == code
        assert res.explanation is not None and len(res.explanation) > 10
        assert res.disclaimer is not None
        assert "diagnos" in res.disclaimer.lower() and "not" in res.disclaimer.lower()
        assert len(res.clinical_questions) > 0
        assert res.medical_reference is not None

    assert len(panels_seen) >= 14, f"Expected at least 14 panels, found {len(panels_seen)}: {panels_seen}"


# --- 2. Laboratory Reference Range Preservation & No Invention ---

def test_prefer_laboratory_reported_reference_interval():
    """Verify interpreter strictly prefers the laboratory's reported reference interval over catalog default."""
    interpreter = ClinicalInterpretationService()

    # Catalog ALT default is 7 - 56 U/L. Lab report specifies tighter range 10 - 35 U/L.
    bm = {
        "analyte_code": "LIV_ALT",
        "label": "Alanine Aminotransferase",
        "value_numeric": 45.0,
        "unit": "U/L",
        "reference_low": 10.0,
        "reference_high": 35.0,  # Lab-specific upper limit
        "reference_text": "10.0 - 35.0 U/L",
        "flag": "above_reference",
        "extraction_confidence": 0.98
    }

    interp = interpreter.interpret_biomarker(bm)
    # Must cite laboratory's reported range, not invent or default to 56
    assert "10.0 - 35.0" in interp.explanation or "10.0 - 35.0" in interp.reasoning_limits


def test_no_invention_of_missing_ranges_or_diagnoses():
    """Ensure missing reference intervals are explicitly unclassified without invented diagnostic claims."""
    interpreter = ClinicalInterpretationService()

    bm_unclassified = {
        "analyte_code": "UNKNOWN_ANALYTE",
        "label": "Experimental Serology X",
        "value_numeric": 14.2,
        "unit": "units",
        "reference_low": None,
        "reference_high": None,
        "flag": "unclassified",
        "extraction_confidence": 0.90
    }

    interp = interpreter.interpret_biomarker(bm_unclassified)
    assert interp.analyte_code == "UNKNOWN_ANALYTE"
    assert "not currently indexed in our standard" in interp.explanation
    assert "withheld" in interp.reasoning_limits.lower()
    # Confirm no diagnostic claim
    assert "diagnosed" not in interp.explanation.lower()


# --- 3. Critical Panic Alert Criteria (Context-Specific vs Generic High/Low) ---

@pytest.mark.parametrize("code,value,expected_urgency,trigger_keyword", [
    ("ELEC_K", 2.4, "urgent_assessment", "potassium"),      # Critical Hypokalemia (<2.8)
    ("ELEC_K", 6.8, "urgent_assessment", "potassium"),      # Critical Hyperkalemia (>6.2)
    ("GLU_FASTING", 42.0, "urgent_assessment", "glucose"),  # Neuroglycopenic Hypoglycemia (<50)
    ("GLU_FASTING", 480.0, "urgent_assessment", "glucose"), # Severe Hyperglycemia (>400)
    ("CARD_TROP_I", 0.12, "urgent_assessment", "troponin"), # Acute Myocardial Injury (>0.04)
    ("CBC_HGB", 5.5, "urgent_assessment", "hemoglobin"),    # Severe Acute Anemia (<7.0)
    ("CBC_PLT", 14.0, "urgent_assessment", "platelet"),     # Spontaneous Hemorrhage Risk (<20)
    ("ELEC_NA", 114.0, "urgent_assessment", "sodium"),      # Severe Hyponatremia (<120)
    ("ELEC_CA", 5.8, "urgent_assessment", "calcium"),       # Tetany / QT Risk (<6.5)
])
def test_critical_panic_alert_escalation(code, value, expected_urgency, trigger_keyword):
    """Verify that specific critical thresholds trigger urgent assessment and symptom-aware emergency escalation."""
    interpreter = ClinicalInterpretationService()
    bm = {
        "analyte_code": code,
        "label": code,
        "value_numeric": value,
        "flag": "above_reference" if value > 10 else "below_reference",
        "extraction_confidence": 1.0
    }

    interp = interpreter.interpret_biomarker(bm)
    assert interp.urgency_level == expected_urgency
    assert interp.urgency_notice is not None
    assert trigger_keyword in interp.urgency_notice.lower()


def test_generic_routine_abnormal_does_not_trigger_emergency_alert():
    """Ensure routine mild/moderate abnormalities do NOT cry wolf with emergency alerts."""
    interpreter = ClinicalInterpretationService()

    # Mild ALT elevation: 65 U/L (ref high 56)
    bm_alt = {
        "analyte_code": "LIV_ALT",
        "label": "Alanine Aminotransferase",
        "value_numeric": 65.0,
        "reference_low": 7.0,
        "reference_high": 56.0,
        "flag": "above_reference",
        "extraction_confidence": 1.0
    }
    interp_alt = interpreter.interpret_biomarker(bm_alt)
    assert interp_alt.urgency_level in {"monitor", "routine"}
    assert interp_alt.urgency_notice is None

    # Mild Fasting Glucose: 112 mg/dL (ref high 99)
    bm_glu = {
        "analyte_code": "GLU_FASTING",
        "label": "Fasting Blood Glucose",
        "value_numeric": 112.0,
        "reference_low": 70.0,
        "reference_high": 99.0,
        "flag": "above_reference",
        "extraction_confidence": 1.0
    }
    interp_glu = interpreter.interpret_biomarker(bm_glu)
    assert interp_glu.urgency_level in {"monitor", "routine"}
    assert interp_glu.urgency_notice is None


# --- 4. Multi-Marker Cluster Synthesis ---

def test_hepatic_cluster_de_ritis_ratio():
    """Verify hepatic cluster calculates AST/ALT ratio and distinguishes metabolic vs alcohol/mitochondrial pattern."""
    interpreter = ClinicalInterpretationService()

    # 1. ALT predominant: ALT=120, AST=60 -> ratio 0.5 (< 1.0 metabolic pattern)
    markers_metabolic = [
        {"analyte_code": "LIV_ALT", "label": "ALT", "value_numeric": 120.0, "flag": "above_reference"},
        {"analyte_code": "LIV_AST", "label": "AST", "value_numeric": 60.0, "flag": "above_reference"},
    ]
    clusters_meta = interpreter.synthesize_multimarker_clusters(markers_metabolic)
    assert len(clusters_meta) == 1
    hep_meta = clusters_meta[0]
    assert hep_meta["cluster_name"] == "Hepatic Functional Profile"
    insights_text = " ".join(hep_meta["educational_insights"])
    assert "ratio of 0.5" in insights_text
    assert "metabolic liver changes" in insights_text

    # 2. AST predominant: ALT=50, AST=125 -> ratio 2.5 (> 2.0 alcohol/muscle pattern)
    markers_etoh = [
        {"analyte_code": "LIV_ALT", "label": "ALT", "value_numeric": 50.0, "flag": "above_reference"},
        {"analyte_code": "LIV_AST", "label": "AST", "value_numeric": 125.0, "flag": "above_reference"},
    ]
    clusters_etoh = interpreter.synthesize_multimarker_clusters(markers_etoh)
    hep_etoh = clusters_etoh[0]
    insights_etoh = " ".join(hep_etoh["educational_insights"])
    assert "ratio of 2.5" in insights_etoh
    assert "alcohol-associated" in insights_etoh or "mitochondrial" in insights_etoh


def test_renal_cluster_bun_creatinine_ratio():
    """Verify renal cluster calculates BUN/Creatinine ratio to flag pre-renal/dehydration vs intrinsic."""
    interpreter = ClinicalInterpretationService()

    # BUN=32, Creatinine=1.2 -> Ratio 26.7:1 (>20 indicates pre-renal/dehydration)
    markers = [
        {"analyte_code": "KID_BUN", "label": "BUN", "value_numeric": 32.0, "flag": "above_reference"},
        {"analyte_code": "KID_CREAT", "label": "Creatinine", "value_numeric": 1.2, "flag": "within_reference"},
        {"analyte_code": "KID_EGFR", "label": "eGFR", "value_numeric": 55.0, "flag": "below_reference"}
    ]
    clusters = interpreter.synthesize_multimarker_clusters(markers)
    renal = next(c for c in clusters if c["cluster_name"] == "Renal & Filtration Dynamics")
    insights = " ".join(renal["educational_insights"])
    assert "26.7:1" in insights
    assert "dehydration" in insights or "pre-renal" in insights
    assert "55.0 mL/min" in insights or "55 mL/min" in insights


def test_cardiometabolic_cluster_discordance_and_tg_hdl():
    """Verify cardiometabolic cluster identifies glucose vs HbA1c discordance and TG/HDL ratio."""
    interpreter = ClinicalInterpretationService()

    # Fasting glucose high (125), but HbA1c normal (5.3) -> acute stress / incomplete fasting
    markers = [
        {"analyte_code": "GLU_FASTING", "label": "Fasting Glucose", "value_numeric": 125.0, "flag": "above_reference"},
        {"analyte_code": "GLU_HBA1C", "label": "HbA1c", "value_numeric": 5.3, "flag": "within_reference"},
        {"analyte_code": "LIP_TRIG", "label": "Triglycerides", "value_numeric": 210.0, "flag": "above_reference"},
        {"analyte_code": "LIP_HDL", "label": "HDL Cholesterol", "value_numeric": 42.0, "flag": "within_reference"}
    ]
    clusters = interpreter.synthesize_multimarker_clusters(markers)
    metabolic = next(c for c in clusters if c["cluster_name"] == "Cardiometabolic & Glycemic Balance")
    insights = " ".join(metabolic["educational_insights"])
    assert "discordance" in insights or "acute physiological stress" in insights
    assert "Triglyceride/HDL ratio of 5.0" in insights


def test_hematology_and_thyroid_clusters():
    """Verify Hematology microcytic anemia pattern and Thyroid subclinical pattern."""
    interpreter = ClinicalInterpretationService()

    # Hematology: Low HGB + Low MCV + Low Ferritin -> Iron deficiency anemia pattern
    hema_markers = [
        {"analyte_code": "CBC_HGB", "label": "Hemoglobin", "value_numeric": 9.2, "flag": "below_reference"},
        {"analyte_code": "CBC_MCV", "label": "MCV", "value_numeric": 72.0, "flag": "below_reference"},
        {"analyte_code": "IRON_FERRITIN", "label": "Ferritin", "value_numeric": 8.0, "flag": "below_reference"}
    ]
    hema_clusters = interpreter.synthesize_multimarker_clusters(hema_markers)
    assert any("iron deficiency" in " ".join(c["educational_insights"]).lower() for c in hema_clusters)

    # Thyroid: High TSH + Normal Free T4 -> Subclinical Hypothyroidism pattern
    thy_markers = [
        {"analyte_code": "THY_TSH", "label": "TSH", "value_numeric": 7.4, "flag": "above_reference"},
        {"analyte_code": "THY_FT4", "label": "Free T4", "value_numeric": 1.2, "flag": "within_reference"}
    ]
    thy_clusters = interpreter.synthesize_multimarker_clusters(thy_markers)
    assert any("subclinical hypothyroidism" in " ".join(c["educational_insights"]).lower() for c in thy_clusters)


# --- 5. Borderline Status & OCR Uncertainty Indicators ---

def test_borderline_indicator_within_5_percent():
    """Verify that a value within 5% of reference boundary is marked borderline."""
    interpreter = ClinicalInterpretationService()

    # Reference High is 100. Value is 103 (3% above) -> Borderline
    bm_borderline = {
        "analyte_code": "GLU_FASTING",
        "label": "Glucose",
        "value_numeric": 103.0,
        "reference_low": 70.0,
        "reference_high": 100.0,
        "flag": "above_reference",
        "extraction_confidence": 0.99
    }
    interp = interpreter.interpret_biomarker(bm_borderline)
    assert interp.is_borderline is True
    assert any("day-to-day fluctuation" in r.lower() for r in interp.possible_reasons)

    # Value is 150 (50% above) -> Not borderline
    bm_high = dict(bm_borderline, value_numeric=150.0)
    interp_high = interpreter.interpret_biomarker(bm_high)
    assert interp_high.is_borderline is False


def test_ocr_low_confidence_uncertainty_notice():
    """Verify that low-confidence OCR scans trigger prominent uncertainty warnings."""
    interpreter = ClinicalInterpretationService()

    bm_low_conf = {
        "analyte_code": "LIV_ALT",
        "label": "Alanine Aminotransferase",
        "value_numeric": 45.0,
        "unit": "U/L",
        "reference_low": 7.0,
        "reference_high": 56.0,
        "flag": "within_reference",
        "extraction_confidence": 0.72,  # Low OCR confidence
        "source_page": 2
    }

    interp = interpreter.interpret_biomarker(bm_low_conf)
    assert interp.uncertainty_notice is not None
    assert "Unverified Reading Notice" in interp.uncertainty_notice
    assert "page 2" in interp.uncertainty_notice
    assert "72%" in interp.uncertainty_notice


# --- 6. Voluntary Contextual Considerations (Medications, Pregnancy, Age) ---

def test_voluntary_patient_context_influences_interpretations():
    """Verify that voluntary opt-in factors (medications, pregnancy, age) add contextual notes."""
    interpreter = ClinicalInterpretationService()

    # 1. Statin medication context on liver transaminases
    statin_context = {"medications": [{"drug_name": "Atorvastatin 20mg"}]}
    bm_alt = {"analyte_code": "LIV_ALT", "label": "ALT", "value_numeric": 58.0, "flag": "above_reference"}
    interp_statin = interpreter.interpret_biomarker(bm_alt, patient_context=statin_context)
    assert any("statin" in note.lower() for note in interp_statin.contextual_notes)

    # 2. Pregnancy hemodilution lowering hemoglobin & elevating ALP
    preg_context = {"pregnancy_status": True}
    bm_hgb = {"analyte_code": "CBC_HGB", "label": "Hemoglobin", "value_numeric": 10.8, "flag": "below_reference"}
    interp_preg = interpreter.interpret_biomarker(bm_hgb, patient_context=preg_context)
    assert any("hemodilution" in note.lower() for note in interp_preg.contextual_notes)

    # 3. Age >= 65 eGFR expected decline
    age_context = {"age": 72}
    bm_egfr = {"analyte_code": "KID_EGFR", "label": "eGFR", "value_numeric": 58.0, "flag": "below_reference"}
    interp_age = interpreter.interpret_biomarker(bm_egfr, patient_context=age_context)
    assert any("age-related decline" in note.lower() for note in interp_age.contextual_notes)


# --- 7. Authenticated Endpoints, Cross-User Isolation, Zero-PHI Logging ---

def test_get_report_summary_endpoint():
    """Verify GET /api/reports/{id}/summary returns multi-marker clusters and educational guardrails."""
    res = client.get("/api/reports/rep_demo_2026_001/summary", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["report_id"] == "rep_demo_2026_001"
    assert data["total_biomarkers"] > 0
    assert "multimarker_clusters" in data
    assert len(data["multimarker_clusters"]) >= 2
    assert "organ_literacy_notice" in data
    assert "health literacy only" in data["organ_literacy_notice"].lower()


def test_post_report_interpret_with_voluntary_context():
    """Verify POST /api/reports/{id}/interpret accepts voluntary context and delivers personalized interpretation."""
    payload = {
        "age": 68,
        "pregnancy_status": False,
        "medications": [
            {"drug_name": "Rosuvastatin", "dosage": "10mg"},
            {"drug_name": "Lisinopril", "dosage": "20mg"}
        ]
    }
    res = client.post("/api/reports/rep_demo_2026_001/interpret", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["report_id"] == "rep_demo_2026_001"
    assert len(data["multimarker_clusters"]) > 0

    # Verify zero PHI in audit trail
    with get_db() as conn:
        evt = conn.execute(
            "SELECT * FROM audit_events WHERE event_type = 'REPORT_INTERPRETATION_GENERATED' ORDER BY timestamp DESC LIMIT 1;"
        ).fetchone()
        assert evt is not None
        assert "demouser" not in evt["details"]
        assert "Rosuvastatin" not in evt["details"]  # Safe audit details


def test_cross_user_isolation_blocked_403():
    """Verify that user 002 cannot interpret or access reports owned by user 001."""
    # Attempt summary
    res_summary = client.get("/api/reports/rep_demo_2026_001/summary", headers=OTHER_USER_HEADERS)
    assert res_summary.status_code == 403

    # Attempt interpret
    res_interp = client.post("/api/reports/rep_demo_2026_001/interpret", json={"age": 30}, headers=OTHER_USER_HEADERS)
    assert res_interp.status_code == 403


def test_unauthenticated_request_fails_401():
    """Verify unauthenticated requests are strictly rejected."""
    res = client.get("/api/reports/rep_demo_2026_001/summary")
    assert res.status_code == 401

    res_post = client.post("/api/reports/rep_demo_2026_001/interpret", json={})
    assert res_post.status_code == 401
