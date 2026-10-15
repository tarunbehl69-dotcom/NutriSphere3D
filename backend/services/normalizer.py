"""
NutriSphere 3D - Clinical Analyte & Unit Normalization Engine
Accurately maps lab test names, synonyms, and international units while preserving
all original raw readings, lab reference ranges, and source page citations.
Strictly flags unfamiliar tests as unclassified (never silently drops),
detects incompatible units, handles missing values, and highlights low-confidence extractions.
"""

import re
import csv
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
CATALOG_CSV_PATH = DATA_DIR / "test_catalog_seed.csv"


class NormalizerService:
    """Clinical normalization engine for laboratory tests and units."""

    def __init__(self, catalog_csv: Optional[Path] = None):
        self.csv_path = catalog_csv or CATALOG_CSV_PATH
        self.catalog: Dict[str, Dict[str, Any]] = {}
        self.synonym_map: Dict[str, str] = {}
        self._load_catalog()

    def _clean_token(self, text: str) -> str:
        """Clean and normalize a text token for flexible matching."""
        if not text:
            return ""
        # Lowercase, strip punctuation and extra spaces
        text = text.lower().strip()
        text = re.sub(r"[\(\)\[\],;:\-_/]", " ", text)
        return " ".join(text.split())

    def _load_catalog(self):
        """Load test catalog and build alias lookup table."""
        if not self.csv_path.exists():
            return

        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["analyte_code"]
                self.catalog[code] = row

                # Map canonical name
                canonical_clean = self._clean_token(row["canonical_name"])
                if canonical_clean:
                    self.synonym_map[canonical_clean] = code

                # Map analyte code itself
                self.synonym_map[code.lower()] = code

                # Map all comma-separated aliases
                raw_aliases = row.get("aliases", "")
                if raw_aliases:
                    for alias in raw_aliases.split(","):
                        cleaned_alias = self._clean_token(alias)
                        if cleaned_alias:
                            self.synonym_map[cleaned_alias] = code

    def resolve_analyte(self, raw_label: str) -> Optional[str]:
        """
        Resolve a recognized analyte code from raw text label using exact and fuzzy alias matching.
        Returns None if unfamiliar (never guesses or invents test codes).
        """
        if not raw_label:
            return None

        cleaned = self._clean_token(raw_label)
        if cleaned in self.synonym_map:
            return self.synonym_map[cleaned]

        # Check sub-phrase matches (e.g. "Alanine Aminotransferase (ALT/SGPT)")
        for synonym, code in sorted(self.synonym_map.items(), key=lambda x: len(x[0]), reverse=True):
            if len(synonym) >= 3:
                # Word boundary check
                pattern = r"\b" + re.escape(synonym) + r"\b"
                if re.search(pattern, cleaned):
                    return code

        # Also check with "sugar" -> "glucose" equivalence
        if "sugar" in cleaned:
            sugar_variant = cleaned.replace("sugar", "glucose")
            if sugar_variant in self.synonym_map:
                return self.synonym_map[sugar_variant]
            for synonym, code in sorted(self.synonym_map.items(), key=lambda x: len(x[0]), reverse=True):
                if len(synonym) >= 3 and re.search(r"\b" + re.escape(synonym) + r"\b", sugar_variant):
                    return code

        return None

    def convert_unit(
        self,
        analyte_code: str,
        value: Optional[float],
        from_unit: Optional[str],
        target_unit: Optional[str]
    ) -> Tuple[Optional[float], bool, str]:
        """
        Convert between verified lab measurement units.
        Returns: (converted_value, is_compatible, audit_note)
        """
        if value is None:
            return None, True, "No numeric value provided"

        if not from_unit or not target_unit:
            return value, True, "Unit unchanged (missing unit specifier)"

        u_from = from_unit.strip().lower()
        u_target = target_unit.strip().lower()

        # Same unit
        if u_from == u_target:
            return value, True, "Identical units"

        # Incompatible units whitelist check (e.g. pressure/heart-rate/distance)
        physically_incompatible = {"mmhg", "bpm", "beats/min", "l", "liters", "cm", "kg", "celsius", "fahrenheit"}
        if u_from in physically_incompatible:
            return None, False, f"Unit '{from_unit}' is physically incompatible with analyte {analyte_code}"

        # 1. Glucose: mmol/L <-> mg/dL (Factor 18.0182)
        if analyte_code in {"GLU_FASTING", "GLU_PP"}:
            if u_from == "mmol/l" and u_target == "mg/dl":
                return round(value * 18.0182, 1), True, "Converted from mmol/L to mg/dL (x18.0182)"
            if u_from == "mg/dl" and u_target == "mmol/l":
                return round(value / 18.0182, 2), True, "Converted from mg/dL to mmol/L (/18.0182)"

        # 2. Cholesterol / HDL / LDL: mmol/L <-> mg/dL (Factor 38.67)
        if analyte_code in {"LIP_CHOL", "LIP_HDL", "LIP_LDL"}:
            if u_from == "mmol/l" and u_target == "mg/dl":
                return round(value * 38.67, 1), True, "Converted from mmol/L to mg/dL (x38.67)"
            if u_from == "mg/dl" and u_target == "mmol/l":
                return round(value / 38.67, 2), True, "Converted from mg/dL to mmol/L (/38.67)"

        # 3. Triglycerides: mmol/L <-> mg/dL (Factor 88.57)
        if analyte_code == "LIP_TRIG":
            if u_from == "mmol/l" and u_target == "mg/dl":
                return round(value * 88.57, 1), True, "Converted from mmol/L to mg/dL (x88.57)"
            if u_from == "mg/dl" and u_target == "mmol/l":
                return round(value / 88.57, 2), True, "Converted from mg/dL to mmol/L (/88.57)"

        # 4. Creatinine: umol/L or µmol/L <-> mg/dL (Factor 88.4)
        if analyte_code == "KID_CREAT":
            if u_from in {"umol/l", "µmol/l"} and u_target == "mg/dl":
                return round(value / 88.4, 2), True, "Converted from umol/L to mg/dL (/88.4)"
            if u_from == "mg/dl" and u_from in {"umol/l", "µmol/l"}:
                return round(value * 88.4, 1), True, "Converted from mg/dL to umol/L (x88.4)"

        # 5. Hemoglobin: g/L <-> g/dL (Factor 10.0)
        if analyte_code == "CBC_HGB":
            if u_from == "g/l" and u_target == "g/dl":
                return round(value / 10.0, 1), True, "Converted from g/L to g/dL (/10.0)"
            if u_from == "g/dl" and u_target == "g/l":
                return round(value * 10.0, 1), True, "Converted from g/dL to g/L (x10.0)"

        # 6. Bilirubin: umol/L <-> mg/dL (Factor 17.1)
        if analyte_code in {"LIV_TBIL", "LIV_DBIL"}:
            if u_from in {"umol/l", "µmol/l"} and u_target == "mg/dl":
                return round(value / 17.1, 2), True, "Converted from umol/L to mg/dL (/17.1)"

        # 7. 25-OH Vitamin D: nmol/L <-> ng/mL (Factor 2.496)
        if analyte_code == "VIT_D":
            if u_from == "nmol/l" and u_target == "ng/ml":
                return round(value / 2.496, 1), True, "Converted from nmol/L to ng/mL (/2.496)"
            if u_from == "ng/ml" and u_target == "nmol/l":
                return round(value * 2.496, 1), True, "Converted from ng/mL to nmol/L (x2.496)"

        # 8. Calcium: mmol/L <-> mg/dL (Factor 4.008)
        if analyte_code == "ELEC_CA":
            if u_from == "mmol/l" and u_target == "mg/dl":
                return round(value * 4.008, 2), True, "Converted from mmol/L to mg/dL (x4.008)"

        # No safe verified conversion rule exists
        return value, True, f"Original unit preserved (no automatic conversion rule between {from_unit} and {target_unit})"

    def normalize_biomarker(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a raw biomarker extraction:
        - Maps label to canonical code or UNKNOWN_ANALYTE
        - Preserves exact raw values, raw units, and source citations
        - Checks unit compatibility
        - Flags missing/untestable values
        - Flags low confidence for human review
        """
        raw_label = str(raw_data.get("label", "")).strip()
        analyte_code = self.resolve_analyte(raw_label)
        is_recognized = analyte_code is not None

        raw_value_numeric = raw_data.get("value_numeric")
        raw_value_text = raw_data.get("value_text")
        raw_unit = raw_data.get("unit")
        ref_low = raw_data.get("reference_low")
        ref_high = raw_data.get("reference_high")
        confidence = float(raw_data.get("extraction_confidence", 1.0))

        # Check for missing values / non-numeric status
        is_missing = False
        missing_keywords = ["qns", "not tested", "hemolyzed", "cancelled", "n/a", "none", "null", "insufficient", "quantity not sufficient"]
        if raw_value_numeric is None:
            if not raw_value_text:
                is_missing = True
            else:
                txt = str(raw_value_text).lower().strip()
                if any(kw in txt for kw in missing_keywords):
                    is_missing = True

        catalog_entry = self.catalog.get(analyte_code, {}) if is_recognized else {}
        standard_unit = catalog_entry.get("standard_unit", raw_unit)
        organ_system = catalog_entry.get("organ_system", "Unclassified")

        # Handle unit conversion if recognized
        normalized_value = raw_value_numeric
        unit_note = ""
        is_compatible = True

        if is_recognized and raw_value_numeric is not None and raw_unit:
            normalized_value, is_compatible, unit_note = self.convert_unit(
                analyte_code=analyte_code,
                value=raw_value_numeric,
                from_unit=raw_unit,
                target_unit=standard_unit
            )

        # Determine reference interval: Prefer report-provided range
        eval_low = ref_low if ref_low is not None else (
            float(catalog_entry["reference_low"]) if catalog_entry.get("reference_low") else None
        )
        eval_high = ref_high if ref_high is not None else (
            float(catalog_entry["reference_high"]) if catalog_entry.get("reference_high") else None
        )

        # Compute preliminary flag
        flag = "unknown"
        if is_missing:
            flag = "not_tested"
        elif not is_compatible:
            flag = "incompatible_units"
        elif not is_recognized:
            flag = "unclassified"
        elif normalized_value is not None and eval_low is not None and eval_high is not None:
            if normalized_value < eval_low:
                flag = "below_reference"
            elif normalized_value > eval_high:
                flag = "above_reference"
            else:
                flag = "within_reference"

        # Flag ambiguous / low-confidence extractions
        needs_human_verification = confidence < 0.85

        return {
            "analyte_code": analyte_code or "UNKNOWN_ANALYTE",
            "canonical_name": catalog_entry.get("canonical_name", raw_label),
            "label": raw_label,
            "raw_value_numeric": raw_value_numeric,
            "raw_value_text": raw_value_text,
            "raw_unit": raw_unit,
            "normalized_value": normalized_value,
            "standard_unit": standard_unit,
            "reference_low": eval_low,
            "reference_high": eval_high,
            "reference_text": raw_data.get("reference_text") or catalog_entry.get("reference_text"),
            "flag": flag,
            "organ_system": organ_system,
            "is_recognized": is_recognized,
            "is_compatible_units": is_compatible,
            "is_missing": is_missing,
            "extraction_confidence": confidence,
            "needs_human_verification": needs_human_verification,
            "unit_conversion_audit": unit_note,
            "source_page": raw_data.get("source_page", 1)
        }
