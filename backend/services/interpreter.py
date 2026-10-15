"""
NutriSphere 3D - Comprehensive Medical Report Interpretation Engine
Evidence-linked, non-diagnostic interpretation service explaining all 74 catalog analytes
across 14 clinical panels in accessible plain language.

Guiding Principles:
1. Honest, non-diagnostic scope: Never claims a confirmed diagnosis or prescribes treatments.
2. Preserves laboratory reference intervals, original units, and reported flags.
3. Identifies critical/panic values requiring prompt medical escalation.
4. Synthesizes multi-marker clusters (Hepatic, Renal, Metabolic, Lipid, Thyroid, Anemia).
5. Highlights uncertainty for low-confidence or unverified OCR values.
6. Integrates opt-in patient context (medications, pregnancy, age).
7. Zero PHI leakage in operational logging.
"""

import csv
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from backend.models import InterpretationOut

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
CATALOG_CSV_PATH = DATA_DIR / "test_catalog_seed.csv"

# Critical / Panic alert criteria (urgent clinical assessment thresholds)
CRITICAL_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "ELEC_K": {
        "low": 2.8,
        "high": 6.2,
        "unit": "mEq/L",
        "message": "Critical potassium anomaly. Severe risk of cardiac conduction disturbances or arrhythmias. If feeling palpitations, chest discomfort, or profound muscle weakness, seek emergency medical attention."
    },
    "ELEC_NA": {
        "low": 120.0,
        "high": 160.0,
        "unit": "mEq/L",
        "message": "Severe sodium dysregulation. Acute risk of neurological alteration, lethargy, or seizure activity. Immediate clinical evaluation required."
    },
    "GLU_FASTING": {
        "low": 50.0,
        "high": 400.0,
        "unit": "mg/dL",
        "message": "Critical glucose crisis. Values <50 mg/dL indicate acute neuroglycopenic hypoglycemia; values >400 mg/dL indicate severe hyperglycemia risking ketoacidosis or hyperosmolar crisis. Prompt emergency or urgent physician attention advised."
    },
    "GLU_PP": {
        "low": 50.0,
        "high": 400.0,
        "unit": "mg/dL",
        "message": "Severe postprandial glucose fluctuation requiring urgent clinical evaluation."
    },
    "CBC_HGB": {
        "low": 7.0,
        "high": 22.0,
        "unit": "g/dL",
        "message": "Critical hemoglobin finding. Severe acute anemia compromises tissue oxygenation; extreme elevations risk hyperviscosity syndrome. Prompt physician evaluation required."
    },
    "CBC_PLT": {
        "low": 20.0,
        "high": 1000.0,
        "unit": "10^3/uL",
        "message": "Critical platelet count. Severe risk of spontaneous mucosal or internal hemorrhage (<20,000/uL) or microvascular thrombosis. Immediate medical evaluation recommended."
    },
    "CARD_TROP_I": {
        "high": 0.04,
        "unit": "ng/mL",
        "message": "Elevated Cardiac Troponin I. Highly sensitive marker of acute myocardial cellular injury. In the presence of acute chest pressure, radiation to arm/jaw, or shortness of breath, call emergency services (911/112) immediately."
    },
    "CARD_TROP_T": {
        "high": 0.014,
        "unit": "ng/mL",
        "message": "Elevated Cardiac Troponin T. Acute myocardial injury indicator requiring immediate physician evaluation."
    },
    "ELEC_CA": {
        "low": 6.5,
        "high": 13.0,
        "unit": "mg/dL",
        "message": "Critical serum calcium level. Severe neuromuscular irritability (tetany) or cardiac QT interval changes possible. Prompt physician consultation required."
    },
    "CBC_WBC": {
        "low": 1.0,
        "high": 50.0,
        "unit": "10^3/uL",
        "message": "Critical leukocyte count. High vulnerability to opportunistic bacterial sepsis (<1,000/uL) or leukemoid reaction (>50,000/uL). Contact your physician urgently."
    },
    "KID_EGFR": {
        "low": 15.0,
        "unit": "mL/min",
        "message": "Severely reduced estimated glomerular filtration rate (<15 mL/min/1.73m²), indicative of stage 5 kidney failure. Nephrology consultation required."
    },
    "LIV_TBIL": {
        "high": 15.0,
        "unit": "mg/dL",
        "message": "Severely elevated total bilirubin with pronounced jaundice risk and hepatic/biliary compromise."
    },
    "COAG_INR": {
        "high": 4.5,
        "unit": "ratio",
        "message": "Critically elevated INR indicating profound anticoagulation and heightened risk of spontaneous or trauma-induced bleeding."
    }
}

# Non-pathological & clinical factors catalog for clinical literacy
PHYSIOLOGICAL_FACTORS: Dict[str, Dict[str, Any]] = {
    "Hematology": {
        "high_reasons": ["Dehydration / hemoconcentration", "High altitude living", "Smoking / carbon monoxide exposure", "Physiological bone marrow stimulation"],
        "low_reasons": ["Nutritional deficiencies (Iron, Vitamin B12, Folate)", "Acute or chronic occult blood loss", "Hemodilution (e.g. pregnancy, fluid overload)", "Bone marrow suppression or chronic disease"],
        "factors": ["Hydration state", "Recent intense exertion", "Posture during phlebotomy", "Altitude"]
    },
    "Liver": {
        "high_reasons": ["Metabolic liver changes (steatosis / fatty liver)", "Strenuous weight lifting or muscle damage", "Medications (statins, NSAIDs, antibiotics)", "Alcohol consumption or viral exposure"],
        "low_reasons": ["Malnutrition or severe protein deficiency (for albumin)", "Advanced end-stage liver synthetic decline", "Normal healthy individual baseline"],
        "factors": ["Recent vigorous exercise within 48h", "Over-the-counter medications / supplements", "Fasting duration", "Alcohol intake within 72h"]
    },
    "Kidney": {
        "high_reasons": ["Dehydration / reduced fluid intake", "High dietary red meat or creatine intake", "Large muscle mass or heavy lifting", "Medications altering tubular secretion (trimethoprim, cimetidine)"],
        "low_reasons": ["Low muscle mass / sarcopenia", "Amputation or muscle wasting", "Low dietary protein intake", "Overhydration"],
        "factors": ["Hydration status", "High-protein meal prior to blood draw", "Creatine monohydrate supplementation", "Body mass composition"]
    },
    "Metabolic": {
        "high_reasons": ["Dehydration / hemoconcentration", "Diuretic therapy", "Excessive alkali or antacid ingestion", "Metabolic alkalosis"],
        "low_reasons": ["Diarrhea or renal tubular losses", "Metabolic acidosis / ketoacidosis", "Strenuous anaerobic exercise"],
        "factors": ["Respiratory ventilation rate", "Recent intense anaerobic exercise", "Medication context"]
    },
    "Diabetes": {
        "high_reasons": ["Incomplete fasting prior to morning draw", "Acute infection, trauma, or physiological stress", "Insulin resistance or impaired glucose tolerance", "Medications such as glucocorticoids / steroids"],
        "low_reasons": ["Prolonged fasting or intense endurance exercise", "Insulin / secretagogue medication timing", "Early reactive hypoglycemia"],
        "factors": ["Strict 8-12 hour fasting compliance", "Recent carbohydrate consumption", "Acute psychological or physical stress", "Hemoglobin variants (for HbA1c)"]
    },
    "Lipid": {
        "high_reasons": ["Diet high in saturated fats or refined carbohydrates", "Sedentary lifestyle or metabolic syndrome", "Familial / genetic hyperlipidemia", "Hypothyroidism or nephrotic condition"],
        "low_reasons": ["Malnutrition or severe malabsorption", "Hyperthyroidism", "High-intensity athletic conditioning (for triglycerides)"],
        "factors": ["Non-fasting blood draw (affects triglycerides)", "Recent alcohol intake", "Acute illness / hospital admission (falsely lowers LDL)", "Rapid weight loss"]
    },
    "Thyroid": {
        "high_reasons": ["Primary thyroid underactivity (hypothyroidism)", "Autoimmune thyroiditis (Hashimoto's)", "Recovery phase of thyroid illness", "Biotin supplement interference"],
        "low_reasons": ["Primary thyroid overactivity (hyperthyroidism / Graves')", "Excessive thyroid hormone replacement dose", "First trimester pregnancy (hCG cross-reactivity)", "Severe non-thyroidal illness"],
        "factors": ["High-dose Biotin (Vitamin B7) within 48h", "Time of day (circadian TSH peak in early morning)", "Pregnancy", "Acute systemic illness"]
    },
    "Vitamins": {
        "high_reasons": ["High-dose oral supplementation", "Hypervitaminosis or excess fortified foods", "Normal individual variation"],
        "low_reasons": ["Inadequate dietary intake or strict restrictive diet", "Limited sunlight exposure (for Vitamin D)", "Malabsorption (celiac, Crohn's, bariatric surgery)", "Metformin or PPI medication use (for B12)"],
        "factors": ["Recent supplement doses", "Sunlight exposure / season", "Gastrointestinal absorption status"]
    },
    "Minerals": {
        "high_reasons": ["Renal clearance reduction", "High supplement intake or antacids containing minerals", "Hypoaldosteronism or tissue breakdown"],
        "low_reasons": ["Diuretic medication therapy", "Gastrointestinal losses (vomiting, diarrhea)", "Inadequate dietary intake or poor absorption"],
        "factors": ["Hemolysis of specimen in tube (falsely elevates potassium)", "Fasting vs non-fasting", "Hydration status"]
    },
    "Iron": {
        "high_reasons": ["Acute or chronic inflammatory state (ferritin is an acute phase reactant)", "Iron overload / hemochromatosis", "Frequent blood transfusions", "Liver cellular injury"],
        "low_reasons": ["Iron deficiency anemia", "Chronic occult blood loss (gastrointestinal, heavy menses)", "Poor dietary iron bioavailability", "High endurance athletic training"],
        "factors": ["Diurnal variation (iron is higher in morning)", "Systemic inflammation / infection (elevates ferritin)", "Recent iron supplement intake"]
    },
    "Hormones": {
        "high_reasons": ["Stress response, intense exercise, or circadian peak", "Medications (antipsychotics, antiemetics)", "Endocrine gland hyperactivity"],
        "low_reasons": ["Endocrine gland hypofunction", "Aging and physiological senescence", "Severe chronic illness or extreme caloric deficit"],
        "factors": ["Time of morning blood draw (crucial for cortisol and testosterone)", "Sleep quality and stress", "Menstrual cycle phase"]
    },
    "Cardiac": {
        "high_reasons": ["Acute myocardial injury / infarction", "Myocarditis or pericarditis", "Severe tachycardia or sustained extreme exercise", "Severe pulmonary embolism or renal clearance decline"],
        "low_reasons": ["Healthy baseline reference finding", "Absence of detectable myocardial cellular necrosis"],
        "factors": ["Recent extreme endurance marathon running", "Renal insufficiency (can reduce troponin clearance)", "Assay platform sensitivity"]
    },
    "Inflammation": {
        "high_reasons": ["Acute bacterial or viral infection", "Systemic autoimmune flare (rheumatoid arthritis, lupus)", "Tissue trauma, surgery, or burns", "Chronic vascular inflammation (atherosclerosis)"],
        "low_reasons": ["Absence of active acute systemic inflammatory response", "Healthy baseline anti-inflammatory state"],
        "factors": ["Recent dental procedures or minor injuries", "Upper respiratory infections within 2 weeks", "Physical exercise"]
    },
    "Coagulation": {
        "high_reasons": ["Anticoagulant therapy (Warfarin, Heparin, DOACs)", "Liver synthetic dysfunction (clotting factor deficit)", "Vitamin K deficiency", "Inherited coagulation factor deficiencies"],
        "low_reasons": ["Hypercoagulable states", "Normal healthy clotting baseline"],
        "factors": ["Underfilled blood tube (citrate dilution artifact)", "Dietary Vitamin K intake (leafy greens)", "Timing of anticoagulant doses"]
    },
    "Urine": {
        "high_reasons": ["Urinary tract infection or bacterial colonization", "Transient benign proteinuria (exercise, fever)", "Glomerular permeability alteration", "Glycosuria exceeding renal threshold (>180 mg/dL blood glucose)"],
        "low_reasons": ["Normal clean physiological specimen"],
        "factors": ["Clean-catch midstream collection technique", "Recent intense exercise", "Hydration concentration vs dilution"]
    },
    "Infectious": {
        "high_reasons": ["Active, acute, or past infection", "Successful vaccination response (for antibody titers)", "Cross-reacting antibodies"],
        "low_reasons": ["Absence of specific pathogen antigen/antibody", "Window period prior to seroconversion"],
        "factors": ["Timing of blood draw relative to symptom onset", "Prior vaccination history", "Immunocompromised status"]
    }
}


class ClinicalInterpretationService:
    """Comprehensive, non-diagnostic clinical report interpretation engine."""

    DISCLAIMER = (
        "NutriSphere 3D provides educational explanations of laboratory findings for health literacy purposes only. "
        "Laboratory reference intervals represent statistical reference populations, not definitive diagnoses. "
        "Normal values cannot definitively rule out subclinical conditions, and atypical results are not medical diagnoses. "
        "All findings must be evaluated by a licensed physician in the context of personal medical history and physical examination."
    )

    def __init__(self):
        self.catalog: Dict[str, Dict[str, Any]] = {}
        self._load_catalog()

    def _load_catalog(self):
        """Load 74-analyte dictionary from CSV."""
        if not CATALOG_CSV_PATH.exists():
            return
        with open(CATALOG_CSV_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["analyte_code"]
                self.catalog[code] = row

    def evaluate_urgency(
        self,
        analyte_code: str,
        value_numeric: Optional[float],
        ref_high: Optional[float] = None,
        ref_low: Optional[float] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Evaluate if a biomarker value triggers clinical emergency or urgent assessment criteria.
        Returns: (urgency_level: 'routine'|'monitor'|'priority'|'urgent_assessment', notice: Optional[str])
        """
        if value_numeric is None:
            return "routine", None

        code = (analyte_code or "").upper()

        # 1. Specific panic / critical threshold criteria
        if code in CRITICAL_THRESHOLDS:
            rule = CRITICAL_THRESHOLDS[code]
            is_low_crit = "low" in rule and value_numeric <= rule["low"]
            is_high_crit = "high" in rule and value_numeric >= rule["high"]

            if is_low_crit or is_high_crit:
                return "urgent_assessment", rule["message"]

        # 2. Cardiac troponin general escalation if above reference high
        if "TROP" in code and ref_high is not None and value_numeric > ref_high:
            return "urgent_assessment", "Reported troponin exceeds laboratory decision limit. Immediate emergency medical assessment advised to rule out acute coronary event."

        # 3. Severe out-of-range deviations (>3x upper limit or <0.3x lower limit for standard tests)
        if ref_high is not None and ref_high > 0 and value_numeric > (ref_high * 3.0):
            return "priority", "Pronounced elevation (>3x standard reference limit). Recommend timely medical follow-up."
        if ref_low is not None and ref_low > 0 and value_numeric < (ref_low * 0.4):
            return "priority", "Pronounced reduction (<40% standard reference limit). Recommend timely medical follow-up."

        if (ref_high is not None and value_numeric > ref_high) or (ref_low is not None and value_numeric < ref_low):
            return "monitor", None

        return "routine", None

    def evaluate_borderline(
        self,
        value_numeric: Optional[float],
        ref_low: Optional[float],
        ref_high: Optional[float]
    ) -> bool:
        """Check if numeric reading is within 5% of either reference boundary."""
        if value_numeric is None:
            return False

        if ref_low is not None and ref_low > 0:
            diff_low = abs(value_numeric - ref_low) / ref_low
            if diff_low <= 0.05:
                return True

        if ref_high is not None and ref_high > 0:
            diff_high = abs(value_numeric - ref_high) / ref_high
            if diff_high <= 0.05:
                return True

        return False

    def get_contextual_considerations(
        self,
        analyte_code: str,
        patient_context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate non-diagnostic contextual notes based on opt-in patient factors."""
        if not patient_context:
            return []

        notes = []
        code = (analyte_code or "").upper()
        medications = patient_context.get("medications", [])
        med_names = " ".join([str(m.get("drug_name", "")).lower() for m in medications] if isinstance(medications, list) else [])
        is_pregnant = bool(patient_context.get("pregnancy_status", False))
        age = patient_context.get("age")

        # 1. Medication Context
        if "statin" in med_names or "atorvastatin" in med_names or "rosuvastatin" in med_names:
            if code in {"LIV_ALT", "LIV_AST"}:
                notes.append("Medication Context: HMG-CoA reductase inhibitors (statins) can cause benign transaminase elevations. Review with prescribing doctor.")
            if code in {"LIP_CHOL", "LIP_LDL"}:
                notes.append("Medication Context: Statin therapy actively modulates LDL cholesterol targets.")

        if "metformin" in med_names and code in {"GLU_FASTING", "GLU_HBA1C"}:
            notes.append("Medication Context: Metformin supports insulin sensitivity and hepatic glucose regulation.")

        if ("cholecalciferol" in med_names or "vitamin d" in med_names) and code == "VIT_D":
            notes.append("Medication Context: Active Vitamin D supplementation typically takes 8-12 weeks to reflect in serum 25-OH Vitamin D equilibrium.")

        if ("lisinopril" in med_names or "losartan" in med_names or "ace" in med_names) and code in {"ELEC_K", "KID_CREAT"}:
            notes.append("Medication Context: RAAS inhibitor medications can influence renal hemodynamics and elevate potassium.")

        if ("warfarin" in med_names or "coumadin" in med_names) and code in {"COAG_INR", "COAG_PT"}:
            notes.append("Medication Context: Anticoagulation therapy requires individualized therapeutic INR target ranges (typically 2.0-3.0).")

        # 2. Pregnancy Context
        if is_pregnant:
            if code in {"CBC_HGB", "CBC_HCT", "CBC_RBC"}:
                notes.append("Pregnancy Context: Expanded maternal plasma volume creates physiological hemodilution, naturally lowering hemoglobin in 2nd/3rd trimester.")
            if code == "LIV_ALP":
                notes.append("Pregnancy Context: Placental alkaline phosphatase isoenzymes physiologically increase in the late second and third trimesters.")
            if code == "GLU_FASTING":
                notes.append("Pregnancy Context: Gestational glucose evaluation utilizes specific maternal guidelines (typically <92-95 mg/dL).")

        # 3. Age Context
        if age and age >= 65:
            if code == "KID_EGFR":
                notes.append("Age Context: Glomerular filtration rate undergoes expected age-related decline (~1 mL/min/year after age 40).")
            if code == "LIV_ALP":
                notes.append("Age Context: Mild bone isoenzyme elevation is commonly observed in mature adults.")

        return notes

    def interpret_biomarker(
        self,
        biomarker: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> InterpretationOut:
        """
        Generate complete, evidence-linked educational interpretation for a single biomarker.
        Handles: purpose, reported intervals, normal/abnormal/borderline states,
        critical panic values, non-pathological factors, questions for doctors,
        and uncertainty indicators for unverified OCR extractions.
        """
        code = biomarker.get("analyte_code", "UNKNOWN_ANALYTE")
        label = biomarker.get("label", "Laboratory Analyte")
        val_numeric = biomarker.get("value_numeric")
        val_text = biomarker.get("value_text")
        unit = biomarker.get("unit") or ""
        ref_low = biomarker.get("reference_low")
        ref_high = biomarker.get("reference_high")
        ref_text = biomarker.get("reference_text")
        flag = biomarker.get("flag", "unknown")
        confidence = float(biomarker.get("extraction_confidence", 1.0))
        source_page = biomarker.get("source_page", 1)

        is_recognized = code in self.catalog
        catalog_entry = self.catalog.get(code, {})
        panel = catalog_entry.get("panel", "General")
        panel_factors = PHYSIOLOGICAL_FACTORS.get(panel, {
            "high_reasons": ["Physiological adaptation", "Clinical elevation factors"],
            "low_reasons": ["Nutritional deficit", "Clinical reduction factors"],
            "factors": ["Hydration", "Fasting status", "Medications"]
        })

        # 1. Evaluate Urgency & Panic Thresholds
        urgency_level, urgency_notice = self.evaluate_urgency(code, val_numeric, ref_high, ref_low)

        # 2. Evaluate Borderline Status
        is_borderline = self.evaluate_borderline(val_numeric, ref_low, ref_high)

        # 3. Uncertainty Notice for OCR / Low Confidence
        uncertainty_notice = None
        if confidence < 0.85:
            uncertainty_notice = (
                f"Unverified Reading Notice: Extracted from document page {source_page} with optical character "
                f"recognition (confidence {int(confidence * 100)}%). OCR scans may introduce character misreads. "
                "Confirm this reading with your physical paper laboratory report before discussing with your doctor."
            )

        # 4. Reference Interval Description (Prefers laboratory's reported interval)
        if ref_low is not None and ref_high is not None:
            ref_desc = f"Reported laboratory reference interval: {ref_low} - {ref_high} {unit}."
        elif ref_text:
            ref_desc = f"Reported laboratory reference interval: {ref_text}."
        elif catalog_entry.get("reference_text"):
            ref_desc = f"Catalog standard interval: {catalog_entry['reference_text']} (Laboratory-specific ranges take precedence)."
        else:
            ref_desc = "No reference interval provided on laboratory report. Reference intervals vary by analyzer methodology and patient demographics."

        # 5. Purpose & Explanation
        purpose = catalog_entry.get("description") or f"Measures {label} concentration in biological specimen."
        
        if not is_recognized:
            explanation = (
                f"Test '{label}' was extracted from your laboratory report. This analyte is not currently indexed "
                "in our standard 74-analyte educational dictionary. Original readings and units have been preserved "
                "without speculative automated interpretation. Please discuss this specific test with your physician."
            )
            reasoning_limits = "Automated interpretation withheld for uncataloged tests to prevent inaccurate medical assumptions."
            followup = "Request clarification from your ordering healthcare provider regarding the clinical rationale for this test."
            questions = ["What specific physiological function does this test evaluate in my health context?"]
            med_ref = "Clinical Laboratory Improvement Amendments (CLIA) Manual"
            possible_reasons = []
            factors_affecting = ["Specimen handling", "Timing of blood draw", "Hydration"]
        elif val_numeric is None and val_text:
            explanation = (
                f"{label}: {purpose} The laboratory reported a qualitative or non-numeric result: '{val_text}'. "
                f"{ref_desc}"
            )
            reasoning_limits = "Non-numeric values represent qualitative presence, agglutination, or specimen status."
            followup = "Discuss the qualitative laboratory notation with your physician."
            questions = ["Does this qualitative result require repeat testing or quantitative follow-up?"]
            med_ref = catalog_entry.get("medical_references") or "AACC Reference Guide"
            possible_reasons = []
            factors_affecting = panel_factors.get("factors", [])
        else:
            # Numeric value explanation
            status_phrase = (
                "within typical laboratory limits" if flag == "within_reference"
                else ("reported above the standard reference interval" if flag == "above_reference"
                else ("reported below typical reference thresholds" if flag == "below_reference"
                else "evaluated relative to laboratory reference boundaries"))
            )
            
            borderline_phrase = " (borderline reading near boundary cutoff)" if is_borderline else ""
            urgent_phrase = " [CRITICAL ALERT LEVEL]" if urgency_level == "urgent_assessment" else ""

            explanation = (
                f"{label}: {purpose} Your reported reading of {val_numeric} {unit} is {status_phrase}{borderline_phrase}{urgent_phrase}. "
                f"{ref_desc}"
            )

            reasoning_limits = (
                "A statistical reference interval is not a definitive diagnosis. Healthy individuals can fall "
                "outside population intervals, and normal readings cannot definitively rule out subclinical disease."
            )

            if urgency_level == "urgent_assessment":
                followup = "CRITICAL FINDING: Seek prompt medical or emergency assessment. Contact your ordering doctor without delay."
            elif flag in {"above_reference", "below_reference"}:
                followup = "Consult your physician for clinical correlation with symptoms, dietary factors, and repeat confirmation."
            else:
                followup = "Discuss how this normal reading correlates with your ongoing preventative health goals."

            # Assemble possible reasons based on high vs low
            if flag == "above_reference":
                possible_reasons = panel_factors.get("high_reasons", [])
            elif flag == "below_reference":
                possible_reasons = panel_factors.get("low_reasons", [])
            else:
                possible_reasons = ["Healthy biological homeostasis", "Effective metabolic equilibrium"]

            if is_borderline:
                possible_reasons = ["Minor physiological day-to-day fluctuation", "Hydration variance"] + possible_reasons

            # Clinical questions
            raw_q = catalog_entry.get("clinical_questions", "")
            questions = [q.strip() for q in raw_q.split(";") if q.strip()] if raw_q else [
                "How does this finding fit into my overall health and current symptoms?",
                "Is repeat confirmatory testing recommended?"
            ]

            med_ref = catalog_entry.get("medical_references") or "Mayo Clinic Laboratories / AACC Handbook"
            factors_affecting = panel_factors.get("factors", [])

        # 6. Contextual Notes
        context_notes = self.get_contextual_considerations(code, patient_context)

        return InterpretationOut(
            biomarker_id=biomarker.get("id"),
            analyte_code=code,
            explanation=explanation,
            reasoning_limits=reasoning_limits,
            followup=followup,
            clinical_questions=questions,
            factors_affecting_test=factors_affecting,
            possible_reasons=possible_reasons,
            urgency_level=urgency_level,
            urgency_notice=urgency_notice,
            is_borderline=is_borderline,
            uncertainty_notice=uncertainty_notice,
            contextual_notes=context_notes,
            related_tests=[code],
            medical_reference=med_ref,
            disclaimer=self.DISCLAIMER
        )

    def interpret_marker(
        self,
        analyte_code: str,
        value_numeric: Optional[float],
        ref_low: Optional[float] = None,
        ref_high: Optional[float] = None,
        unit: Optional[str] = None
    ) -> Dict[str, Any]:
        """Backward-compatible helper for individual marker interpretation."""
        flag = "unknown"
        if value_numeric is not None:
            if ref_low is not None and ref_high is not None:
                if value_numeric < ref_low:
                    flag = "below_reference"
                elif value_numeric > ref_high:
                    flag = "above_reference"
                else:
                    flag = "within_reference"
            elif ref_high is not None:
                flag = "above_reference" if value_numeric > ref_high else "within_reference"
            elif ref_low is not None:
                flag = "below_reference" if value_numeric < ref_low else "within_reference"
            else:
                flag = "unclassified"

        bm = {
            "analyte_code": analyte_code,
            "label": self.catalog.get(analyte_code, {}).get("analyte_name", analyte_code),
            "value_numeric": value_numeric,
            "reference_low": ref_low,
            "reference_high": ref_high,
            "unit": unit,
            "flag": flag,
            "extraction_confidence": 1.0
        }
        interp = self.interpret_biomarker(bm)
        return {
            "analyte_code": analyte_code,
            "value_numeric": value_numeric,
            "flag": flag,
            "summary": interp.explanation,
            "possible_reasons": interp.possible_reasons,
            "questions_for_doctor": interp.clinical_questions,
            "evidence_reference": interp.medical_reference,
            "disclaimer": self.DISCLAIMER,
            "urgency_level": interp.urgency_level,
            "interpretation": interp.model_dump()
        }

    def synthesize_multimarker_clusters(
        self,
        biomarkers: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple related biomarkers together to generate educational cross-marker insights.
        Synthesizes Hepatic, Renal, Metabolic, Lipid, Thyroid, and Anemia clusters with uncertainty disclaimers.
        """
        clusters = []
        code_map = {b.get("analyte_code"): b for b in biomarkers if b.get("analyte_code")}

        # 1. Hepatic Profile Cluster (ALT, AST, ALP, TBIL, ALB)
        alt = code_map.get("LIV_ALT")
        ast = code_map.get("LIV_AST")
        alp = code_map.get("LIV_ALP")
        tbil = code_map.get("LIV_TBIL")
        if alt or ast or alp:
            insights = []
            alt_val = alt.get("value_numeric") if alt else None
            ast_val = ast.get("value_numeric") if ast else None
            alt_high = alt.get("flag") == "above_reference" if alt else False
            ast_high = ast.get("flag") == "above_reference" if ast else False

            if alt_high and ast_high and alt_val and ast_val and alt_val > 0:
                ratio = round(ast_val / alt_val, 2)
                if ratio < 1.0:
                    insights.append(f"Elevated ALT and AST with AST/ALT ratio of {ratio} (ALT predominant). Commonly associated in clinical literature with metabolic liver changes (fatty liver), medication effects, or acute hepatic stress.")
                elif ratio > 2.0:
                    insights.append(f"Elevated AST and ALT with AST/ALT ratio of {ratio} (AST predominant). Often correlated with alcohol-associated hepatic sensitivity, intense skeletal muscle breakdown, or mitochondrial stress.")
                else:
                    insights.append(f"Concurrent transaminase elevation (AST/ALT ratio {ratio}). Non-pathological factors include recent strenuous exercise, muscle trauma, or statin therapy.")
            elif alt_high and not ast_high:
                insights.append("Isolated mild ALT elevation with normal AST. ALT is more liver-specific; isolated shifts frequently correlate with hydration, weight lifting, or mild dietary hepatic changes.")
            elif alp and alp.get("flag") == "above_reference":
                insights.append("Alkaline Phosphatase (ALP) elevation noted. Biliary or bone isoenzyme origin should be considered alongside bilirubin and bone markers.")
            else:
                insights.append("Hepatic transaminases and synthetic markers demonstrate balanced cellular integrity.")

            clusters.append({
                "cluster_name": "Hepatic Functional Profile",
                "organ_system": "Liver",
                "markers_evaluated": [k for k in ["LIV_ALT", "LIV_AST", "LIV_ALP", "LIV_TBIL", "LIV_ALB"] if k in code_map],
                "clinical_pattern": "Hepatocellular & Biliary Assessment",
                "educational_insights": insights,
                "uncertainty_disclaimer": "Enzyme shifts reflect cellular permeability and cannot distinguish between temporary exercise-induced strain, fatty liver, or pathology without ultrasound and clinical exam."
            })

        # 2. Renal Profile Cluster (Creatinine, BUN, eGFR, Electrolytes)
        creat = code_map.get("KID_CREAT")
        bun = code_map.get("KID_BUN")
        egfr = code_map.get("KID_EGFR")
        if creat or bun or egfr:
            insights = []
            creat_val = creat.get("value_numeric") if creat else None
            bun_val = bun.get("value_numeric") if bun else None

            if creat_val and bun_val and creat_val > 0:
                ratio = round(bun_val / creat_val, 1)
                if ratio > 20.0:
                    insights.append(f"BUN/Creatinine ratio of {ratio}:1 is elevated. High ratios frequently point to pre-renal factors (dehydration, low fluid intake, or high dietary protein) rather than intrinsic kidney injury.")
                elif ratio < 10.0:
                    insights.append(f"BUN/Creatinine ratio of {ratio}:1 is below standard. May correlate with low-protein diet or reduced muscle mass.")
                else:
                    insights.append(f"BUN/Creatinine ratio of {ratio}:1 reflects physiological equilibrium.")

            if egfr:
                egfr_val = egfr.get("value_numeric")
                if egfr_val and egfr_val < 60:
                    insights.append(f"eGFR of {egfr_val} mL/min indicates reduced filtration efficiency. Medical guidelines advise repeat testing after 3 months to distinguish acute changes from chronic baseline.")

            clusters.append({
                "cluster_name": "Renal & Filtration Dynamics",
                "organ_system": "Kidneys",
                "markers_evaluated": [k for k in ["KID_CREAT", "KID_BUN", "KID_EGFR", "ELEC_NA", "ELEC_K"] if k in code_map],
                "clinical_pattern": "Glomerular Filtration & Hydration Index",
                "educational_insights": insights or ["Renal filtration parameters reflect balanced clearance."],
                "uncertainty_disclaimer": "Creatinine and eGFR are influenced by muscle mass, dietary meat intake, and hydration. A single measurement cannot confirm chronic kidney disease."
            })

        # 3. Cardiometabolic & Diabetes Cluster (Glucose, HbA1c, Lipids)
        glu = code_map.get("GLU_FASTING")
        a1c = code_map.get("GLU_HBA1C")
        trig = code_map.get("LIP_TRIG")
        hdl = code_map.get("LIP_HDL")
        if glu or a1c or trig:
            insights = []
            glu_val = glu.get("value_numeric") if glu else None
            a1c_val = a1c.get("value_numeric") if a1c else None

            # Discordance analysis
            if glu_val and a1c_val:
                if glu_val > 100 and a1c_val <= 5.6:
                    insights.append(f"Fasting glucose ({glu_val} mg/dL) is elevated while HbA1c ({a1c_val}%) remains in the standard range. This discordance often reflects acute physiological stress, recent carbohydrate ingestion, or incomplete fasting.")
                elif glu_val <= 99 and a1c_val >= 5.7:
                    insights.append(f"Normal fasting glucose ({glu_val} mg/dL) coexisting with elevated HbA1c ({a1c_val}%). Indicates intermittent postprandial glucose excursions over the past 90 days.")
                elif glu_val > 100 and a1c_val >= 5.7:
                    insights.append(f"Concordant elevation in both fasting glucose ({glu_val} mg/dL) and HbA1c ({a1c_val}%). Consistent with impaired glycemic homeostasis.")

            if trig and hdl:
                trig_val = trig.get("value_numeric")
                hdl_val = hdl.get("value_numeric")
                if trig_val and hdl_val and hdl_val > 0:
                    tg_hdl_ratio = round(trig_val / hdl_val, 2)
                    if tg_hdl_ratio > 3.0:
                        insights.append(f"Triglyceride/HDL ratio of {tg_hdl_ratio} is elevated. In clinical literature, ratios >3.0 serve as an educational surrogate marker for insulin resistance.")

            clusters.append({
                "cluster_name": "Cardiometabolic & Glycemic Balance",
                "organ_system": "Pancreas",
                "markers_evaluated": [k for k in ["GLU_FASTING", "GLU_HBA1C", "GLU_PP", "LIP_TRIG", "LIP_HDL"] if k in code_map],
                "clinical_pattern": "Insulin Sensitivity & Long-Term Glycemic Tracking",
                "educational_insights": insights or ["Glycemic and insulin-responsive markers are within target intervals."],
                "uncertainty_disclaimer": "HbA1c can be affected by red blood cell turnover and hemoglobin variants. Definite diabetes or prediabetes diagnosis requires formal clinical evaluation."
            })

        # 4. Hematology & Anemia Cluster (HGB, MCV, Ferritin, Iron)
        hgb = code_map.get("CBC_HGB")
        mcv = code_map.get("CBC_MCV")
        ferr = code_map.get("IRON_FERRITIN")
        if hgb or mcv or ferr:
            insights = []
            hgb_low = hgb.get("flag") == "below_reference" if hgb else False
            mcv_val = mcv.get("value_numeric") if mcv else None
            ferr_low = ferr.get("flag") == "below_reference" if ferr else False

            if hgb_low:
                if mcv_val and mcv_val < 80.0:
                    if ferr_low:
                        insights.append("Microcytic anemia pattern with depleted ferritin: Classic pattern characteristic of iron deficiency anemia.")
                    else:
                        insights.append("Microcytic anemia pattern with preserved ferritin: Considerations include anemia of chronic inflammation or thalassemia trait.")
                elif mcv_val and mcv_val > 100.0:
                    insights.append("Macrocytic anemia pattern (elevated MCV): Considerations include Vitamin B12 deficiency, folate inadequacy, medication effects, or thyroid slowing.")
                else:
                    insights.append("Normocytic anemia pattern (normal MCV): Considerations include early nutritional deficit, acute occult blood loss, or systemic inflammation.")
            elif ferr_low and not hgb_low:
                insights.append("Isolated low ferritin with normal hemoglobin: Reflects early latent iron store depletion before overt anemia develops.")

            if insights:
                clusters.append({
                    "cluster_name": "Hematopoietic & Iron Stores Axis",
                    "organ_system": "Bones/Marrow",
                    "markers_evaluated": [k for k in ["CBC_HGB", "CBC_MCV", "CBC_MCH", "IRON_FERRITIN", "IRON_SERUM", "IRON_TIBC"] if k in code_map],
                    "clinical_pattern": "Erythropoiesis & Iron Bioavailability",
                    "educational_insights": insights,
                    "uncertainty_disclaimer": "Ferritin is an acute-phase reactant; concurrent infection or inflammation can elevate ferritin even in the presence of true iron deficiency."
                })

        # 5. Thyroid Axis Cluster (TSH, FT4, FT3)
        tsh = code_map.get("THY_TSH")
        ft4 = code_map.get("THY_FT4")
        if tsh or ft4:
            insights = []
            tsh_val = tsh.get("value_numeric") if tsh else None
            ft4_val = ft4.get("value_numeric") if ft4 else None
            tsh_flag = tsh.get("flag") if tsh else "unknown"
            ft4_flag = ft4.get("flag") if ft4 else "unknown"

            if tsh_flag == "above_reference" and ft4_flag == "within_reference":
                insights.append(f"Elevated TSH ({tsh_val} uIU/mL) with normal Free T4 ({ft4_val} ng/dL). Represents classic subclinical hypothyroidism pattern. Guidelines recommend retesting in 6-12 weeks.")
            elif tsh_flag == "above_reference" and ft4_flag == "below_reference":
                insights.append("Elevated TSH with depressed Free T4: Primary overt hypothyroidism pattern.")
            elif tsh_flag == "below_reference" and ft4_flag == "above_reference":
                insights.append("Suppressed TSH with elevated Free T4: Primary hyperthyroidism pattern.")
            elif tsh_flag == "below_reference" and ft4_flag == "within_reference":
                insights.append("Suppressed TSH with normal Free T4: Subclinical hyperthyroidism pattern.")

            if insights:
                clusters.append({
                    "cluster_name": "Thyroid Axis Feedback Dynamics",
                    "organ_system": "Thyroid",
                    "markers_evaluated": [k for k in ["THY_TSH", "THY_FT4", "THY_FT3"] if k in code_map],
                    "clinical_pattern": "Pituitary-Thyroid Axis Equilibrium",
                    "educational_insights": insights,
                    "uncertainty_disclaimer": "TSH exhibits a diurnal rhythm and can fluctuate during recovery from acute illness. Biotin supplements also interfere with certain thyroid immunoassay platforms."
                })

        return clusters

    def interpret_report(
        self,
        report_data: Dict[str, Any],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate complete holistic interpretation of an entire structured medical report:
        Enriches every biomarker with InterpretationOut, flags panic values,
        generates multi-marker cluster insights, and outputs high-priority findings.
        """
        biomarkers = report_data.get("biomarkers", [])
        enriched_biomarkers = []
        high_priority = []
        urgent_count = 0

        for bm in biomarkers:
            interp = self.interpret_biomarker(bm, patient_context=patient_context)
            bm_copy = dict(bm)
            bm_copy["interpretation"] = interp

            # Track urgency
            if interp.urgency_level == "urgent_assessment":
                urgent_count += 1
                high_priority.append(f"CRITICAL FINDING: {bm['label']} ({bm.get('value_numeric')} {bm.get('unit') or ''}) triggers clinical emergency notification protocol.")
            elif bm.get("flag") == "above_reference":
                high_priority.append(f"{bm['label']} ({bm.get('value_numeric')} {bm.get('unit') or ''}) is reported above reference interval. Review with physician.")
            elif bm.get("flag") == "below_reference":
                high_priority.append(f"{bm['label']} ({bm.get('value_numeric')} {bm.get('unit') or ''}) is reported below typical reference range. Discuss potential nutritional or metabolic factors.")

            enriched_biomarkers.append(bm_copy)

        if not high_priority:
            high_priority.append("All reported biomarkers are within standard reference intervals. Routine wellness review recommended.")

        # Synthesize multi-marker clusters
        multimarker_clusters = self.synthesize_multimarker_clusters(biomarkers)
        cross_marker_insights = [
            insight
            for cluster in multimarker_clusters
            for insight in cluster.get("educational_insights", [])
        ]

        if not cross_marker_insights:
            cross_marker_insights = [
                "Biomarkers evaluated across panels indicate coordinated organ homeostasis.",
                "Normal readings cannot definitively exclude subclinical conditions; laboratory intervals vary across methodologies."
            ]

        return {
            "report_id": report_data.get("id"),
            "patient_identifier": report_data.get("user_id", "SYNTH-PATIENT"),
            "collection_date": report_data.get("collection_date"),
            "total_biomarkers": len(enriched_biomarkers),
            "within_reference_count": sum(1 for b in biomarkers if b.get("flag") == "within_reference"),
            "above_reference_count": sum(1 for b in biomarkers if b.get("flag") == "above_reference"),
            "below_reference_count": sum(1 for b in biomarkers if b.get("flag") == "below_reference"),
            "unclassified_count": sum(1 for b in biomarkers if b.get("flag") in {"unknown", "unclassified", "not_tested", "incompatible_units"}),
            "urgent_review_count": urgent_count,
            "high_priority_findings": high_priority,
            "cross_marker_insights": cross_marker_insights,
            "multimarker_clusters": multimarker_clusters,
            "enriched_biomarkers": enriched_biomarkers,
            "organ_literacy_notice": "Visual 3D organ highlights illustrate biological systems associated with these lab tests for health literacy only, not physical damage or medical diagnosis.",
            "clinical_disclaimer": self.DISCLAIMER
        }
