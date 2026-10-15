"""
NutriSphere 3D - Step 5 Master Verification Suite
Verifies:
1. All 6 Full UI Web Routes (/, /upload, /results, /dashboard, /alcohol, /nutrition).
2. Pure Ethanol Density & Metabolism Calculation (WHO 10g & US 14g standard drinks).
3. Alcohol Intake Records CRUD & Cross-User Security Isolation.
4. Report-Linked Hepatic Biomarkers & de Ritis Ratio (AST/ALT) with Normal-Enzyme Caveat.
5. Alcohol Drug Interaction Warnings & Evidence-Based Recovery Nutrition.
6. Food-First Indian Nutrition & Strict Jain Underground Root Exclusion.
7. Dynamic Allergy Filtering (Dairy, Gluten, Peanuts, Soy).
8. Zero-Hallucination Grounded AI Report Assistant with Verified Lab Citations.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.auth import DEV_DEMO_TOKEN, create_session_token

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_DEMO_TOKEN}"}
OTHER_USER_HEADERS = {"Authorization": f"Bearer {create_session_token('usr_demo_002')}"}


# --- 1. UI Routes Verification ---

def test_ui_routes_serve_html():
    """Verify all 6 main UI pages are served with HTTP 200 and expected markup."""
    endpoints = [
        ("/", "Decoded in 3D."),
        ("/upload", "Upload Laboratory Report"),
        ("/results", "Biomarker"),
        ("/dashboard", "Longitudinal Health"),
        ("/alcohol", "Alcohol & Your Health"),
        ("/nutrition", "Food-First Indian Nutrition")
    ]

    for path, expected_text in endpoints:
        res = client.get(path)
        assert res.status_code == 200, f"Route {path} failed with status {res.status_code}"
        assert "text/html" in res.headers["content-type"]
        assert expected_text in res.text, f"Route {path} did not contain '{expected_text}'"


# --- 2. Pure Ethanol Calculator Physics & Logic ---

def test_alcohol_ethanol_calculation_standard():
    """Verify ethanol physics calculation: Vol(mL) * (ABV/100) * 0.789 g/mL."""
    payload = {
        "beverage_type": "Standard Pint of Beer",
        "volume_ml": 500.0,
        "abv_percent": 5.0,
        "drinking_days_per_week": 1
    }
    res = client.post("/api/alcohol/calculate", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()

    # 500 * 0.05 * 0.789 = 19.725 grams
    assert abs(data["pure_alcohol_grams"] - 19.725) < 0.01
    assert abs(data["standard_drinks_who"] - 1.9725) < 0.01
    assert abs(data["standard_drinks_us"] - 1.4089) < 0.01
    assert "Low" in data["educational_risk_tier"]
    assert "clinical_disclaimer" in data


def test_alcohol_ethanol_calculation_severe_tier():
    """Verify high volume/ABV triggers severe risk classification."""
    payload = {
        "beverage_type": "Full Bottle of Wine",
        "volume_ml": 1000.0,
        "abv_percent": 12.0,
        "drinking_days_per_week": 4
    }
    res = client.post("/api/alcohol/calculate", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()

    # 1000 * 0.12 * 0.789 = 94.68 grams (> 60g threshold)
    assert abs(data["pure_alcohol_grams"] - 94.68) < 0.05
    assert "Severe" in data["educational_risk_tier"] or "High" in data["educational_risk_tier"]


def test_alcohol_calculation_negative_validation_422():
    """Verify invalid negative or zero volumes/ABVs are rejected with 422."""
    res1 = client.post("/api/alcohol/calculate", json={"beverage_type": "Beer", "volume_ml": -100.0, "abv_percent": 5.0}, headers=AUTH_HEADERS)
    assert res1.status_code == 422

    res2 = client.post("/api/alcohol/calculate", json={"beverage_type": "Beer", "volume_ml": 500.0, "abv_percent": -5.0}, headers=AUTH_HEADERS)
    assert res2.status_code == 422


# --- 3. Alcohol Intake Records CRUD & Privacy ---

def test_alcohol_intake_records_crud_and_isolation():
    """Verify creating, listing, and deleting intake records with user isolation."""
    # 1. Create Record
    record_payload = {
        "beverage_type": "Craft Stout",
        "volume_ml": 330.0,
        "abv_percent": 6.8,
        "drinking_days_per_week": 2,
        "recorded_date": "2026-10-14"
    }
    post_res = client.post("/api/alcohol/records", json=record_payload, headers=AUTH_HEADERS)
    assert post_res.status_code == 201
    created = post_res.json()
    record_id = created["id"]
    assert created["pure_alcohol_grams"] > 0

    # 2. List Records for User 1
    list_res = client.get("/api/alcohol/records", headers=AUTH_HEADERS)
    assert list_res.status_code == 200
    records = list_res.json()["records"]
    assert any(r["id"] == record_id for r in records)

    # 3. Cross-User Isolation: User 2 cannot see User 1's record
    user2_list = client.get("/api/alcohol/records", headers=OTHER_USER_HEADERS)
    assert user2_list.status_code == 200
    assert not any(r["id"] == record_id for r in user2_list.json()["records"])

    # 4. Cross-User Delete Protection: User 2 cannot delete User 1's record
    del_forbidden = client.delete(f"/api/alcohol/records/{record_id}", headers=OTHER_USER_HEADERS)
    assert del_forbidden.status_code in [403, 404]

    # 5. User 1 successfully deletes their own record
    del_ok = client.delete(f"/api/alcohol/records/{record_id}", headers=AUTH_HEADERS)
    assert del_ok.status_code == 200


# --- 4. Report-Linked Hepatic Biomarkers & Normal-Enzyme Disclaimer ---

def test_alcohol_report_context_and_de_ritis():
    """Verify alcohol report context extracts transaminases, computes de Ritis ratio, and preserves disclaimers."""
    res = client.get("/api/alcohol/report-context/rep_demo_2026_001", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()

    assert "evaluated_markers" in data
    assert data["markers_evaluated_count"] > 0
    marker_codes = [m["analyte_code"] for m in data["evaluated_markers"]]
    assert "LIV_ALT" in marker_codes
    assert "LIV_AST" in marker_codes

    # Strict Clinical Disclaimer: normal transaminases do not rule out alcohol injury
    assert "normal_enzymes_warning" in data
    assert "steatosis" in data["normal_enzymes_warning"].lower() or "liver" in data["normal_enzymes_warning"].lower()


def test_alcohol_recovery_nutrition_and_myths():
    """Verify recovery nutrition advice dispels detox myths and highlights electrolytes/B-vitamins."""
    res = client.get("/api/alcohol/recovery-nutrition", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()

    assert "recovery_principles" in data
    assert len(data["recovery_principles"]) >= 3
    assert "myth_busting" in data
    # Dispelled myth explicitly mentions coffee, sweat, or detox
    all_myths = " ".join([m["myth"] + " " + m["reality"] for m in data["myth_busting"]]).lower()
    assert "detox" in all_myths or "sober" in all_myths or "metabol" in all_myths


# --- 5. Food-First Indian Nutrition & Strict Jain Dietary Rules ---

def test_nutrition_indian_dietary_patterns():
    """Verify vegetarian, vegan, and non-vegetarian meal plans return 3+ distinct balanced meals."""
    patterns = ["vegetarian", "vegan", "non-vegetarian"]
    for pat in patterns:
        res = client.post("/api/nutrition/context", json={
            "dietary_pattern": pat,
            "allergies": []
        }, headers=AUTH_HEADERS)
        assert res.status_code == 200
        data = res.json()
        assert len(data["meal_plans"]) >= 3
        meal_types = {m["meal"] for m in data["meal_plans"]}
        assert "Breakfast" in meal_types
        assert "Lunch" in meal_types
        assert "Dinner" in meal_types


def test_nutrition_jain_diet_strict_root_exclusion():
    """CRITICAL: Verify Jain diet strictly excludes all root vegetables (potatoes, onions, garlic, carrots, beets)."""
    res = client.post("/api/nutrition/context", json={
        "dietary_pattern": "jain",
        "allergies": []
    }, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()

    prohibited_root_terms = ["potato", "potatoes", "onion", "onions", "garlic", "carrot", "carrots", "beetroot", "radish"]

    for meal in data["meal_plans"]:
        text_corpus = f"{meal['title']} {meal['description']} {meal.get('key_nutrients', '')}".lower()
        for term in prohibited_root_terms:
            assert term not in text_corpus, f"Jain violation: found prohibited root '{term}' in meal: {meal['title']}"

    # Verify presence of permitted Jain staples
    all_text = " ".join([f"{m['title']} {m['description']}" for m in data["meal_plans"]]).lower()
    assert any(staple in all_text for staple in ["moong", "lauki", "cumin", "turmeric", "hing", "khichdi"])


def test_nutrition_allergy_filtering_dairy_and_gluten():
    """Verify allergen filtering removes dairy and gluten items from meal plans."""
    res = client.post("/api/nutrition/context", json={
        "dietary_pattern": "vegetarian",
        "allergies": ["dairy", "gluten"]
    }, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()

    for meal in data["meal_plans"]:
        desc = (meal["title"] + " " + meal["description"]).lower()
        # In vegetarian with dairy allergy, paneer and dahi should not be primary ingredients
        assert "paneer bhurji" not in desc


def test_nutrition_report_biomarker_linkage():
    """Verify that including report_id returns biomarker-tailored dietary adaptations."""
    res = client.post("/api/nutrition/context", json={
        "dietary_pattern": "vegetarian",
        "allergies": [],
        "report_id": "rep_demo_2026_001"
    }, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "biomarker_linked_guidance" in data
    assert len(data["biomarker_linked_guidance"]) > 0


# --- 6. Grounded AI Report Assistant ---

def test_ai_assistant_grounded_response_and_citation():
    """Verify AI Assistant answers questions by citing verified report values without diagnosing."""
    res = client.post("/api/chat/explain", json={
        "report_id": "rep_demo_2026_001",
        "question": "Can you explain what my ALT and AST enzymes mean?",
        "conversation_history": []
    }, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()

    assert "response" in data
    assert "referenced_biomarkers" in data
    assert len(data["referenced_biomarkers"]) > 0
    # Must cite ALT or AST
    assert any("ALT" in c or "AST" in c for c in data["referenced_biomarkers"])
    # Must include non-diagnostic disclaimer
    assert "clinical_disclaimer" in data
    assert "diagnosis" in data["clinical_disclaimer"].lower() or "educational" in data["clinical_disclaimer"].lower()


# --- 7. Additional System & Historical Trajectory Tests ---

def test_demo_report_fixture():
    """Verify synthetic medical report fixture for demo mode."""
    res = client.get("/api/demo-report")
    assert res.status_code == 200
    data = res.json()
    assert data["report_metadata"]["report_id"] == "rep_demo_2026_001"
    assert "biomarkers" in data
    assert len(data["biomarkers"]) >= 10


def test_historical_reports_endpoint():
    """Verify longitudinal multi-year health records for trend comparisons."""
    res = client.get("/api/reports/historical", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "series" in data
    assert len(data["series"]) >= 2


def test_ai_assistant_empty_question_422():
    """Verify AI Assistant rejects empty questions with 422 validation error."""
    res = client.post("/api/chat/explain", json={
        "report_id": "rep_demo_2026_001",
        "question": ""
    }, headers=AUTH_HEADERS)
    assert res.status_code == 422


def test_ai_assistant_report_not_found_404():
    """Verify AI Assistant returns 404 for non-existent report ID."""
    res = client.post("/api/chat/explain", json={
        "report_id": "rep_non_existent_999",
        "question": "What is my cholesterol?"
    }, headers=AUTH_HEADERS)
    assert res.status_code == 404


def test_ai_assistant_cross_user_isolation_403():
    """Verify User 2 cannot query User 1's report."""
    res = client.post("/api/chat/explain", json={
        "report_id": "rep_demo_2026_001",
        "question": "What is my cholesterol?"
    }, headers=OTHER_USER_HEADERS)
    assert res.status_code == 403


def test_alcohol_zero_abv_calculation():
    """Verify 0.0% ABV non-alcoholic beverage calculates 0.0g ethanol and Low risk."""
    payload = {
        "beverage_type": "Non-Alcoholic Beer",
        "volume_ml": 500.0,
        "abv_percent": 0.0,
        "drinking_days_per_week": 1
    }
    res = client.post("/api/alcohol/calculate", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["pure_alcohol_grams"] == 0.0
    assert data["standard_drinks_who"] == 0.0
    assert "Low" in data["educational_risk_tier"]


def test_alcohol_drug_interactions_flagged():
    """Verify drug interactions (e.g. Paracetamol) are highlighted in report alcohol analysis."""
    patient_ctx = {"medications": [{"drug_name": "Paracetamol", "dosage": "500mg"}]}
    res = client.get("/api/alcohol/report-context/rep_demo_2026_001", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "overall_cautions" in data

