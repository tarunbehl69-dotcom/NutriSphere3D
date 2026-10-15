"""
NutriSphere 3D - Pydantic Schemas, API Contracts & Privacy Models
Implements strict validation for:
- ReportOut, AnalyteOut, InterpretationOut, UploadStatusOut
- NutritionContextIn, AlcoholContextIn, ReportSummaryOut, ChartPoint, ErrorOut
- ConsentDeclarationIn, UserOut
Enforces:
- File size and MIME type validation
- Numeric biological plausibility checking
- Non-diagnostic clinical phrasing
- Explicit consent & conspicuous deletion controls
- Ownership & privacy guarantees (Zero PHI in logs)
"""

from typing import Optional, List, Any, Dict
from datetime import datetime, timezone
import re
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


# --- Base Response & Error Models ---

class HealthCheckResponse(BaseModel):
    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(default="0.2.0-step2", description="Software version")
    database: str = Field(default="connected", description="SQLite connectivity status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    clinical_notice: str = Field(
        default="NutriSphere 3D provides educational explanations only, not diagnostic decisions.",
        description="Mandatory clinical educational notice"
    )


class ErrorOut(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- User & Privacy Authentication Models ---

class UserOut(BaseModel):
    """User representation for API responses - strictly sanitized (zero password/salt)."""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    created_at: Optional[str] = None


class TestCatalogItemOut(BaseModel):
    """Catalog item schema for medical test lookup and clinical guidance."""
    analyte_code: str
    canonical_name: str
    panel: str
    aliases: Optional[str] = ""
    standard_unit: str
    acceptable_units: Optional[str] = None
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    reference_text: Optional[str] = None
    organ_system: str
    educational_explanation: Optional[str] = None
    clinical_questions: Optional[str] = None
    medical_references: Optional[str] = None


class ConsentDeclarationIn(BaseModel):
    """Explicit consent payload required before report ingestion."""
    has_consented: bool = Field(..., description="Affirmative agreement to educational scope and privacy policy")
    consent_version: str = Field(default="2026.1", description="Legal/clinical disclosure version")
    disclaimer_acknowledged: bool = Field(..., description="Confirmation that laboratory ranges do not diagnose disease")
    purge_on_session_end: bool = Field(default=False, description="Option to delete data automatically on session termination")

    @field_validator("has_consented", "disclaimer_acknowledged")
    @classmethod
    def require_affirmative_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Explicit affirmative consent and clinical disclaimer acknowledgment are required.")
        return v


# --- Medical Biomarker & Interpretation Models ---

class InterpretationOut(BaseModel):
    """Non-diagnostic educational interpretation for an individual biomarker."""
    biomarker_id: Optional[str] = None
    analyte_code: Optional[str] = None
    explanation: str = Field(..., description="Plain-English description of biological role")
    reasoning_limits: str = Field(
        default="Analysis based on laboratory threshold; cannot rule out or establish medical diagnosis.",
        description="Explicit limitation of laboratory assessment"
    )
    followup: Optional[str] = Field(
        default="Consult with treating physician for clinical correlation and symptom evaluation.",
        description="Non-prescriptive follow-up recommendation"
    )
    clinical_questions: List[str] = Field(
        default_factory=lambda: [
            "How does this finding fit into my overall health and current symptoms?",
            "Is a confirmatory or repeat test recommended?"
        ],
        description="Empowering follow-up questions for a licensed doctor"
    )
    factors_affecting_test: List[str] = Field(
        default_factory=list,
        description="Known non-pathological factors (hydration, fasting, diurnal rhythm)"
    )
    possible_reasons: List[str] = Field(
        default_factory=list,
        description="Non-diagnostic physiological and clinical factors from medical literature"
    )
    urgency_level: str = Field(
        default="routine",
        description="routine, monitor, priority, urgent_assessment"
    )
    urgency_notice: Optional[str] = Field(
        default=None,
        description="Clear symptom-aware safety escalation notice when critical threshold met"
    )
    is_borderline: bool = Field(
        default=False,
        description="True if value is within 5% of interval boundary"
    )
    uncertainty_notice: Optional[str] = Field(
        default=None,
        description="Notice if value is from unverified OCR or has low confidence"
    )
    contextual_notes: List[str] = Field(
        default_factory=list,
        description="Considerations based on opt-in medications, age, pregnancy"
    )
    related_tests: List[str] = Field(default_factory=list)
    medical_reference: Optional[str] = Field(default="AACC / Mayo Clinic Laboratories Reference Guide")
    disclaimer: str = Field(
        default="This explanation is educational health literacy, not a medical prescription or diagnosis."
    )


CLINICAL_PLAUSIBILITY_RANGES: Dict[str, Tuple[float, float, str]] = {
    "CBC_HGB": (1.0, 30.0, "g/dL"),
    "CBC_WBC": (0.05, 500.0, "10^3/uL"),
    "CBC_PLT": (1.0, 4000.0, "10^3/uL"),
    "CBC_RBC": (0.5, 12.0, "10^6/uL"),
    "KID_CREAT": (0.05, 45.0, "mg/dL"),
    "KID_BUN": (1.0, 300.0, "mg/dL"),
    "ELEC_K": (1.0, 15.0, "mEq/L"),
    "ELEC_NA": (80.0, 200.0, "mEq/L"),
    "GLU_FASTING": (10.0, 2500.0, "mg/dL"),
    "GLU_PP": (10.0, 2500.0, "mg/dL"),
    "GLU_HBA1C": (2.0, 25.0, "%"),
    "LIP_CHOL": (20.0, 1500.0, "mg/dL"),
    "THY_TSH": (0.001, 300.0, "uIU/mL"),
    "VIT_D": (1.0, 350.0, "ng/mL"),
    "MET_BASE_EXCESS": (-35.0, 35.0, "mEq/L"),
    "BONE_T_SCORE": (-10.0, 10.0, "score"),
    "BONE_Z_SCORE": (-10.0, 10.0, "score")
}


class AnalyteOut(BaseModel):
    """Validated structured biomarker measurement with clinical plausibility checking."""
    id: Optional[str] = None
    report_id: Optional[str] = None
    analyte_code: str = Field(..., description="Canonical analyte identifier or UNKNOWN_ANALYTE")
    label: str = Field(..., min_length=1, max_length=120)
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    unit: Optional[str] = None
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    reference_text: Optional[str] = None
    flag: str = Field(
        default="unknown",
        description="Non-diagnostic flag: within_reference, above_reference, below_reference, urgent_review, unclassified, not_tested, incompatible_units"
    )
    organ_system: str = Field(default="General")
    source_page: int = Field(default=1, ge=1)
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    interpretation: Optional[InterpretationOut] = None

    @field_validator("unit")
    @classmethod
    def validate_compatible_units(cls, v: Optional[str]) -> Optional[str]:
        """Prevent obvious physical unit corruption."""
        if not v:
            return v
        cleaned = v.strip().lower()
        invalid_units = {"bpm", "mmhg", "km", "miles", "celsius", "fahrenheit", "kg"}
        if cleaned in invalid_units:
            raise ValueError(f"Unit '{v}' is physically incompatible with laboratory analyte measurements.")
        return v

    @model_validator(mode="after")
    def validate_clinical_plausibility(self) -> "AnalyteOut":
        """Analyte-specific biological plausibility checks replacing crude non-negative rules."""
        val = self.value_numeric
        if val is None:
            return self

        code = (self.analyte_code or "").upper()
        label = (self.label or "").lower()

        # Specifically signed indices that can legitimately be negative
        can_be_negative = (
            code in {"MET_BASE_EXCESS", "BONE_T_SCORE", "BONE_Z_SCORE"} or
            "base excess" in label or "t-score" in label or "z-score" in label or "deviation" in label
        )

        if code in CLINICAL_PLAUSIBILITY_RANGES:
            p_min, p_max, _ = CLINICAL_PLAUSIBILITY_RANGES[code]
            if val < p_min or val > p_max:
                raise ValueError(
                    f"Value {val} for {self.label} ({code}) is outside the clinically plausible physiological range [{p_min}, {p_max}]."
                )
        else:
            if not can_be_negative and val < 0:
                raise ValueError(f"Value {val} for {self.label} cannot be negative.")
            if val > 10000000.0:
                raise ValueError(f"Value {val} exceeds reasonable biological limit (10,000,000).")

        return self


class UploadStatusOut(BaseModel):
    """Extraction pipeline and OCR status."""
    report_id: str
    status: str = Field(..., description="uploaded, parsing, ocr_in_progress, extracted, needs_human_verification, verified, error")
    progress_percent: int = Field(default=0, ge=0, le=100)
    message: str
    source_pages_count: int = 1
    low_confidence_fields: List[str] = Field(default_factory=list)
    requires_verification: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReportOut(BaseModel):
    """Complete structured laboratory report output."""
    id: str
    user_id: str
    file_name: str
    mime_type: str
    file_size_bytes: int = Field(ge=0, le=15 * 1024 * 1024)
    uploaded_at: str
    collection_date: Optional[str] = None
    laboratory_name: Optional[str] = None
    analysis_status: str = "verified"
    biomarkers_count: int = 0
    biomarkers: List[AnalyteOut] = Field(default_factory=list)
    extraction_notes: Optional[str] = None
    consent_verified: bool = True


class ReportSummaryOut(BaseModel):
    """Holistic summary of extracted tests with clinical cautions and uncertainty metrics."""
    report_id: str
    patient_identifier: str = Field(default="SYNTH-PATIENT-DEMO")
    collection_date: Optional[str] = None
    total_biomarkers: int
    within_reference_count: int
    above_reference_count: int
    below_reference_count: int
    unclassified_count: int
    urgent_review_count: int = 0
    high_priority_findings: List[str] = Field(
        default_factory=list,
        description="Cautious symptom-aware escalation points without definitive diagnosis"
    )
    cross_marker_insights: List[str] = Field(
        default_factory=list,
        description="Conditional multi-test patterns with uncertainty disclaimers"
    )
    multimarker_clusters: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Synthesized multi-test clinical clusters (Hepatic, Renal, Metabolic, Lipid, Thyroid, Anemia)"
    )
    organ_literacy_notice: str = Field(
        default="Visual 3D organ highlights illustrate biological systems associated with these lab tests for health literacy only, not physical damage or medical diagnosis."
    )
    clinical_disclaimer: str = Field(
        default="NutriSphere 3D does not provide medical diagnoses. Lab intervals represent statistical reference populations. Consult a physician for diagnostic evaluation."
    )


class ChartPoint(BaseModel):
    """Single normalized data point for longitudinal trend graphs."""
    date: str
    value: float
    unit: str
    reference_low: Optional[float] = None
    reference_high: Optional[float] = None
    flag: str = "within_reference"
    is_compatible_method: bool = True
    uncertainty_margin: Optional[float] = None


# --- Nutrition & Alcohol Educational Inputs ---

class NutritionContextIn(BaseModel):
    """Opt-in dietary context for culturally grounded food-first education."""
    dietary_pattern: str = Field(default="vegetarian", description="vegetarian, vegan, non-vegetarian, pescatarian, jain")
    allergies: List[str] = Field(default_factory=list, description="Reported food allergens (peanuts, dairy, gluten, soy, tree_nuts)")
    cultural_restrictions: Optional[str] = None
    calorie_target_opt_in: bool = Field(default=False, description="Explicit opt-in required for numeric targets")
    reported_conditions: List[str] = Field(default_factory=list, description="Self-reported clinician-verified diagnoses (e.g. chronic kidney disease)")
    report_id: Optional[str] = None

    @field_validator("dietary_pattern")
    @classmethod
    def validate_diet_pattern(cls, v: str) -> str:
        allowed = {"vegetarian", "vegan", "non-vegetarian", "pescatarian", "jain"}
        if v.lower().strip() not in allowed:
            raise ValueError(f"Dietary pattern must be one of: {', '.join(sorted(allowed))}")
        return v.lower().strip()


class AlcoholContextIn(BaseModel):
    """Contextual factors for evidence-based alcohol health education."""
    frequency_per_week: int = Field(default=0, ge=0, le=100, description="Estimated drinking days per week")
    typical_standard_drinks: float = Field(default=0.0, ge=0.0, le=50.0, description="Estimated drinks on drinking days")
    has_liver_conditions: bool = False
    takes_medications: bool = False
    pregnancy_status: bool = False

    @field_validator("frequency_per_week", "typical_standard_drinks")
    @classmethod
    def check_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Alcohol consumption metrics cannot be negative.")
        return v


class DeleteReportOut(BaseModel):
    """Response returned upon conspicuous report deletion."""
    report_id: str
    status: str = "deleted"
    message: str = "Report and associated extracted biomarkers purged completely."
    audit_event_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LoginIn(BaseModel):
    """Login credentials for server-side authentication."""
    username: str
    password: str


class TokenOut(BaseModel):
    """Server-validated session token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class VerifyBiomarkersIn(BaseModel):
    """Payload for human verification and corrections of extracted report data."""
    collection_date: Optional[str] = None
    laboratory_name: Optional[str] = None
    biomarkers: List[AnalyteOut] = Field(default_factory=list)


class MedicationContextItem(BaseModel):
    """Individual medication item for voluntary context."""
    drug_name: str
    dosage: Optional[str] = None
    purpose: Optional[str] = None


class ReportInterpretRequestIn(BaseModel):
    """Optional voluntary patient context for personalized, non-diagnostic report interpretation."""
    medications: Optional[List[MedicationContextItem]] = None
    age: Optional[int] = Field(default=None, ge=0, le=130)
    pregnancy_status: Optional[bool] = False
    medical_conditions: Optional[List[str]] = None


class AlcoholCalculationIn(BaseModel):
    """Payload for calculating grams of ethanol and standard drinks."""
    beverage_type: str = Field(..., description="Beer, Wine, Whisky, Vodka, Rum, Other")
    volume_ml: float = Field(..., ge=0.0, le=10000.0, description="Volume in milliliters")
    abv_percent: float = Field(..., ge=0.0, le=100.0, description="Alcohol by volume percentage")
    drinking_days_per_week: int = Field(default=1, ge=0, le=7, description="Number of drinking days per week")


class AlcoholCalculationOut(BaseModel):
    """Calculated alcohol metric output without claims of individual safe allowance."""
    beverage_type: str
    volume_ml: float
    abv_percent: float
    pure_alcohol_grams: float = Field(..., description="Calculated using volume * (ABV/100) * 0.789")
    standard_drinks_who: float = Field(..., description="Standard drinks (10g ethanol WHO/India/UK standard)")
    standard_drinks_us: float = Field(..., description="Standard drinks (14g ethanol US standard)")
    drinking_days_per_week: int
    weekly_grams: float
    educational_risk_tier: str
    guidance_message: str
    clinical_disclaimer: str = "This calculator measures intake volume only. No laboratory test or mathematical formula can establish a guaranteed safe personal drinking allowance."


class AlcoholIntakeRecordIn(BaseModel):
    """Payload for logging personal alcohol consumption."""
    beverage_type: str
    volume_ml: float = Field(..., ge=0.0, le=10000.0)
    abv_percent: float = Field(..., ge=0.0, le=100.0)
    drinking_days_per_week: int = Field(default=1, ge=0, le=7)
    recorded_date: Optional[str] = None


class AlcoholIntakeRecordOut(BaseModel):
    """Stored alcohol consumption record."""
    id: str
    user_id: str
    beverage_type: str
    volume_ml: float
    abv_percent: float
    pure_alcohol_grams: float
    standard_drinks: float
    drinking_days_per_week: int
    weekly_grams: float
    recorded_date: str
    created_at: str


class AIReportChatIn(BaseModel):
    """Query payload for the grounded AI medical report assistant."""
    report_id: str
    question: str = Field(..., min_length=2, max_length=1000)
    conversation_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class AIReportChatOut(BaseModel):
    """Report-grounded response with explicit citations and uncertainty safeguards."""
    response: str
    referenced_biomarkers: List[str] = Field(default_factory=list)
    suggested_questions: List[str] = Field(default_factory=list)
    mode: str = "deterministic_clinical_grounding"
    clinical_disclaimer: str = "NutriSphere 3D Assistant provides educational information grounded in your laboratory report. It does not provide medical diagnoses, treatment plans, or prescriptions."


# ==========================================
# NUTRISPHERE QUEST — GAME MODELS
# ==========================================

class GameAchievement(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_at: Optional[str] = None


class GameProgressOut(BaseModel):
    """Complete player progression state."""
    user_id: str
    xp: int
    level: int
    level_title: str
    current_mission: str
    completed_missions_count: int
    next_level_xp: int
    xp_to_next_level: int
    completed_missions: List[str] = Field(default_factory=list)
    unlocked_achievements: List[GameAchievement] = Field(default_factory=list)


class GameMissionCompleteIn(BaseModel):
    """Request payload when a player completes an educational mission."""
    mission_id: str = Field(..., description="e.g. liver_lab, heart_station, kidney_room, digestive_journey, nutrition_plate, alcohol_journey, report_detective")
    score: int = Field(default=100, ge=0, le=100)


class GameMissionCompleteOut(BaseModel):
    """Outcome of completing an educational mission."""
    success: bool
    mission_id: str
    xp_earned: int
    total_xp: int
    level: int
    level_title: str
    level_up: bool
    new_achievements: List[GameAchievement] = Field(default_factory=list)
    message: str


class GameQuizSubmitIn(BaseModel):
    """Payload for submitting an answer to an educational game quiz."""
    quiz_id: str
    question_id: str
    selected_option: int = Field(..., ge=0, le=4)


class GameQuizSubmitOut(BaseModel):
    """Instant feedback and XP award for an educational quiz question."""
    quiz_id: str
    question_id: str
    is_correct: bool
    xp_awarded: int
    total_xp: int
    explanation: str
    correct_option: int


class GameChallengeCompleteIn(BaseModel):
    """Payload for completing an interactive mini-challenge (Plate building, circulation, report detective)."""
    challenge_id: str
    payload_summary: Optional[str] = None
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class GameChallengeCompleteOut(BaseModel):
    """Result of completing a mini-challenge."""
    challenge_id: str
    success: bool
    xp_earned: int
    total_xp: int
    feedback: str
    new_achievements: List[GameAchievement] = Field(default_factory=list)
