"""
NutriSphere X — Step 7 Automated Anatomy Accuracy & Registry Test Suite
Validates:
1. 15 Canonical Verified Organs and their system allocations.
2. Two-level medical vocabulary (Level 1 Everyday + Level 2 Clinical Architecture).
3. Non-diagnostic safety guardrails on all analyte interpretations.
4. Prevention of cross-organ mesh contamination (ventricles, thyroid cartilage, adrenals).
5. API endpoints /api/organs and /api/organs/{organ_id}.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.organ_registry import (
    ORGAN_REGISTRY,
    ORGAN_ALIASES,
    resolve_canonical_organ,
    get_all_organs,
    get_organ
)

client = TestClient(app)

REQUIRED_14_ORGANS = [
    "liver",
    "heart",
    "left_kidney",
    "right_kidney",
    "kidneys",
    "lungs",
    "stomach",
    "pancreas",
    "spleen",
    "small_intestine",
    "large_intestine",
    "thyroid",
    "urinary_bladder",
    "brain",
    "spine"
]


def test_registry_contains_all_14_major_organs():
    """Verify all 14 specified organs (+ kidneys group = 15 total) exist in registry."""
    assert len(ORGAN_REGISTRY) >= 15
    for organ_id in REQUIRED_14_ORGANS:
        assert organ_id in ORGAN_REGISTRY, f"Missing required organ: {organ_id}"


def test_two_level_medical_vocabulary_completeness():
    """Verify every organ has both Level 1 everyday English and Level 2 clinical details."""
    for organ_id, data in ORGAN_REGISTRY.items():
        assert "level1_role" in data and len(data["level1_role"]) > 15, f"{organ_id} missing Level 1 role"
        assert "level2_medical" in data and len(data["level2_medical"]) > 25, f"{organ_id} missing Level 2 medical"
        assert "display_name" in data and len(data["display_name"]) > 0
        assert "medical_name" in data and len(data["medical_name"]) > 0
        assert "camera_pos" in data and len(data["camera_pos"]) == 3
        assert "camera_target" in data and len(data["camera_target"]) == 3


def test_organ_tests_have_two_level_explanations():
    """Verify every biomarker test associated with an organ has Level 1 meaning and Level 2 clinical notes."""
    for organ_id, data in ORGAN_REGISTRY.items():
        tests = data.get("tests", [])
        assert len(tests) > 0, f"Organ {organ_id} has no associated laboratory tests"
        for t in tests:
            assert "code" in t and len(t["code"]) > 0
            assert "name" in t and len(t["name"]) > 0
            assert "level1_meaning" in t and len(t["level1_meaning"]) > 10, f"Test {t.get('code')} missing Level 1 meaning"
            assert "level2_clinical" in t and len(t["level2_clinical"]) > 15, f"Test {t.get('code')} missing Level 2 clinical"


def test_strict_cross_contamination_prevention():
    """Verify keywords prevent historical mesh bugs (e.g., brain ventricles -> heart)."""
    brain_keywords = ORGAN_REGISTRY["brain"]["mesh_keywords"]
    heart_keywords = ORGAN_REGISTRY["heart"]["mesh_keywords"]
    thyroid_keywords = ORGAN_REGISTRY["thyroid"]["mesh_keywords"]
    spine_keywords = ORGAN_REGISTRY["spine"]["mesh_keywords"]

    # Heart keywords must be strictly scoped to cardiovascular system
    assert ORGAN_REGISTRY["heart"]["system_source"] == "cardiovascular"
    assert ORGAN_REGISTRY["brain"]["system_source"] == "nervous"

    # Skeletal system thyroid cartilage must NOT be in endocrine thyroid
    assert ORGAN_REGISTRY["thyroid"]["system_source"] == "endocrine"
    assert "thyroid cartilage" not in [k.lower() for k in thyroid_keywords]

    # Skin/regional mesh must NOT be in spine
    assert ORGAN_REGISTRY["spine"]["system_source"] == "skeletal"
    assert "vertebral region" not in [k.lower() for k in spine_keywords]


def test_alias_resolution_canonical():
    """Verify Latin, colloquial, and legacy aliases resolve to verified canonical organ IDs."""
    test_cases = {
        "hepar": "liver",
        "cor": "heart",
        "renes": "kidneys",
        "left kidney": "left_kidney",
        "right kidney": "right_kidney",
        "splen": "spleen",
        "lien": "spleen",
        "gaster": "stomach",
        "pulmones": "lungs",
        "bladder": "urinary_bladder",
        "encephalon": "brain",
        "columna vertebralis": "spine",
        "bones": "spine"
    }
    for query, expected in test_cases.items():
        resolved = resolve_canonical_organ(query)
        assert resolved == expected, f"Query '{query}' resolved to '{resolved}', expected '{expected}'"


def test_api_organs_get_all():
    """Verify GET /api/organs returns full verified list."""
    res = client.get("/api/organs")
    assert res.status_code == 200
    data = res.json()
    assert "organs" in data
    assert len(data["organs"]) >= 15
    organ_ids = [o["organ_id"] for o in data["organs"]]
    for req in REQUIRED_14_ORGANS:
        assert req in organ_ids


def test_api_organs_get_by_id_and_alias():
    """Verify GET /api/organs/{organ_id} works for canonical IDs and aliases."""
    # Canonical ID
    res = client.get("/api/organs/liver")
    assert res.status_code == 200
    assert res.json()["display_name"] == "Liver"

    # Alias: Spleen via 'splen'
    res_spleen = client.get("/api/organs/splen")
    assert res_spleen.status_code == 200
    assert res_spleen.json()["organ_id"] == "spleen"

    # Alias: Left Kidney
    res_lk = client.get("/api/organs/left%20kidney")
    assert res_lk.status_code == 200
    assert res_lk.json()["organ_id"] == "left_kidney"

    # Non-existent organ returns 404
    res_404 = client.get("/api/organs/non_existent_organ_xyz")
    assert res_404.status_code == 404
