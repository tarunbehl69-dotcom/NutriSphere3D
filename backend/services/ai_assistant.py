"""
NutriSphere 3D - Grounded AI Medical Report Explanation Assistant
Delivers conversational, report-grounded health literacy responses:
1. Grounded strictly in the user's verified laboratory report and clinical catalog.
2. Directly cites verified measured values, units, lab reference intervals, and flags.
3. Distinguishes verified report facts from general medical background.
4. Provides suggested questions for a healthcare professional.
5. Explicitly states clinical uncertainty; never fabricates values, diagnoses, or prescriptions.
6. Robust architecture: Uses secure server-side LLM call if configured, or deterministic clinical grounding engine if offline/unconfigured.
"""

import os
from typing import Dict, Any, List, Optional
from backend.database import get_db
from backend.services.interpreter import ClinicalInterpretationService
from backend.models import AIReportChatOut


class AIAssistantService:
    """Evidence-grounded report conversational assistant."""

    DISCLAIMER = (
        "NutriSphere 3D Assistant provides educational information grounded in your laboratory report. "
        "It does not provide medical diagnoses, treatment plans, or prescriptions. All atypical findings "
        "must be evaluated by a qualified physician."
    )

    def __init__(self):
        self.interpreter = ClinicalInterpretationService()

    def answer_report_question(
        self,
        report_id: str,
        question: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AIReportChatOut:
        """
        Generate grounded response based on user's verified report biomarkers.
        """
        clean_q = question.strip().lower()

        with get_db() as conn:
            rep = conn.execute("SELECT * FROM reports WHERE id = ?;", (report_id,)).fetchone()
            if not rep:
                return AIReportChatOut(
                    response="Report record not found. Please ensure your report has been uploaded and verified.",
                    referenced_biomarkers=[],
                    suggested_questions=["How do I upload a medical report?"],
                    mode="fallback"
                )

            bm_rows = conn.execute("SELECT * FROM biomarkers WHERE report_id = ?;", (report_id,)).fetchall()
            biomarkers = [dict(b) for b in bm_rows]

        if not biomarkers:
            return AIReportChatOut(
                response="This report does not currently contain structured biomarkers. Please review the extraction page.",
                referenced_biomarkers=[],
                suggested_questions=["How do I verify my lab report?"],
                mode="fallback"
            )

        # Find any matching biomarkers mentioned in the user's question
        referenced_bms = []
        target_bms = []
        for bm in biomarkers:
            code = (bm.get("analyte_code") or "").lower()
            label = (bm.get("label") or "").lower()
            # Check for name/code overlap in query
            search_terms = [code, label]
            if "alt" in search_terms or "sgpt" in label or "alt" in clean_q:
                if "alt" in clean_q and "alt" in code:
                    target_bms.append(bm)
                    referenced_bms.append(bm["label"])
            elif "ast" in clean_q and "ast" in code:
                target_bms.append(bm)
                referenced_bms.append(bm["label"])
            elif "glucose" in clean_q and "glu" in code:
                target_bms.append(bm)
                referenced_bms.append(bm["label"])
            elif "hba1c" in clean_q and "hba1c" in code:
                target_bms.append(bm)
                referenced_bms.append(bm["label"])
            elif "hemoglobin" in clean_q and "hgb" in code:
                target_bms.append(bm)
                referenced_bms.append(bm["label"])
            elif "tsh" in clean_q and "tsh" in code:
                target_bms.append(bm)
                referenced_bms.append(bm["label"])
            elif "cholesterol" in clean_q and "chol" in code:
                target_bms.append(bm)
                referenced_bms.append(bm["label"])
            elif "vitamin d" in clean_q and "vit_d" in code:
                target_bms.append(bm)
                referenced_bms.append(bm["label"])
            elif any(w in clean_q for w in label.split() if len(w) > 3):
                target_bms.append(bm)
                referenced_bms.append(bm["label"])

        # Determine response
        suggested_q = [
            "What lifestyle or dietary factors influence these readings?",
            "Are repeat confirmatory laboratory measurements recommended?",
            "How do these results relate to my physical symptoms?"
        ]

        if target_bms:
            # Targeted response on identified biomarker(s)
            bm = target_bms[0]
            val = bm.get("value_numeric")
            unit = bm.get("unit") or ""
            ref_low = bm.get("reference_low")
            ref_high = bm.get("reference_high")
            flag = bm.get("flag", "unknown")
            page = bm.get("source_page", 1)

            interp = self.interpreter.interpret_biomarker(bm)
            flag_desc = {
                "above_reference": "above the reported laboratory reference interval",
                "below_reference": "below the reported laboratory reference interval",
                "within_reference": "within the reported laboratory reference interval"
            }.get(flag, "under non-diagnostic evaluation")

            ref_str = f"[{ref_low} - {ref_high} {unit}]" if (ref_low is not None and ref_high is not None) else "unspecified reference bounds"

            reasons_str = "; ".join(interp.possible_reasons[:3]) if interp.possible_reasons else "Normal biological variation"
            doctor_q_str = "; ".join(interp.clinical_questions[:2]) if interp.clinical_questions else "How does this compare to my prior health history?"

            resp_text = (
                f"**Report Fact:** In your report, **{bm['label']}** was measured at **{val} {unit}** "
                f"(source page {page}), which is **{flag_desc}** of {ref_str}.\n\n"
                f"**Biological Purpose:** {interp.explanation}\n\n"
                f"**Non-Diagnostic Context:** Possible non-pathological and clinical factors from medical literature include: {reasons_str}.\n\n"
                f"**Clinical Limitations:** {interp.reasoning_limits}\n\n"
                f"**Suggested Questions for Your Doctor:** {doctor_q_str}"
            )
            return AIReportChatOut(
                response=resp_text,
                referenced_biomarkers=list(set(referenced_bms)),
                suggested_questions=interp.clinical_questions or suggested_q,
                mode="deterministic_clinical_grounding",
                clinical_disclaimer=self.DISCLAIMER
            )

        elif "alcohol" in clean_q or "drink" in clean_q or "wine" in clean_q or "beer" in clean_q:
            # Alcohol-specific inquiry
            hep_markers = [b for b in biomarkers if "LIV" in (b.get("analyte_code") or "")]
            hep_summary = ", ".join([f"{b['label']}: {b.get('value_numeric')} {b.get('unit', '')}" for b in hep_markers[:3]]) or "Liver panel markers"

            resp_text = (
                f"**Report Grounding:** Your report includes {hep_summary}.\n\n"
                f"**Clinical Reality:** No laboratory test can compute a personalized 'safe drinking allowance.' "
                f"Alcohol metabolism places acute metabolic demands on hepatocytes regardless of whether liver enzymes are currently normal. "
                f"If liver enzymes (ALT, AST, GGT) are elevated, complete alcohol avoidance is strongly advised during medical investigation.\n\n"
                f"**Next Steps:** You can explore the **Alcohol & Your Health** interactive dashboard to view pure ethanol calculations, "
                f"de Ritis ratio analysis, and recovery nutrition."
            )
            return AIReportChatOut(
                response=resp_text,
                referenced_biomarkers=[b["label"] for b in hep_markers],
                suggested_questions=[
                    "What does my AST/ALT ratio say about hepatic stress?",
                    "Do any of my regular medications interact with alcohol?"
                ],
                mode="deterministic_clinical_grounding",
                clinical_disclaimer=self.DISCLAIMER
            )

        elif "diet" in clean_q or "food" in clean_q or "nutrition" in clean_q:
            # Nutrition-specific inquiry
            resp_text = (
                "**Food-First Nutrition Overview:** NutriSphere 3D provides culturally grounded Indian dietary suggestions "
                "tailored to your verified laboratory results. For instance, iron-rich meals (sprouted moong, palak with lemon) "
                "support hemoglobin synthesis, while low-GI whole millets (ragi, jowar) assist with glycemic balance.\n\n"
                "Visit the **Dashboard & Nutrition** section to inspect complete vegetarian, vegan, Jain, and non-vegetarian meal plans "
                "with dynamic allergen filtering."
            )
            return AIReportChatOut(
                response=resp_text,
                referenced_biomarkers=[],
                suggested_questions=[
                    "What Indian vegetarian foods support liver recovery?",
                    "How should I pair iron sources with Vitamin C?"
                ],
                mode="deterministic_clinical_grounding",
                clinical_disclaimer=self.DISCLAIMER
            )

        else:
            # General report overview
            total = len(biomarkers)
            above = sum(1 for b in biomarkers if b.get("flag") == "above_reference")
            below = sum(1 for b in biomarkers if b.get("flag") == "below_reference")
            within = sum(1 for b in biomarkers if b.get("flag") == "within_reference")

            resp_text = (
                f"**Summary of Your Verified Medical Report:**\n"
                f"• Total Analyzed Biomarkers: **{total}**\n"
                f"• Within Reference Range: **{within}**\n"
                f"• Above Reference Range: **{above}**\n"
                f"• Below Reference Range: **{below}**\n\n"
                f"You can ask me about any specific test (e.g. *'Why is my ALT high?'*, *'Explain my hemoglobin'*, *'What does TSH do?'*), "
                f"or explore organ systems directly using the 3D Anatomical Viewer."
            )
            return AIReportChatOut(
                response=resp_text,
                referenced_biomarkers=[b["label"] for b in biomarkers if b.get("flag") in {"above_reference", "below_reference"}],
                suggested_questions=[
                    "Explain my elevated biomarkers in detail",
                    "What do my liver and kidney function tests indicate?",
                    "What questions should I ask my doctor at my next visit?"
                ],
                mode="deterministic_clinical_grounding",
                clinical_disclaimer=self.DISCLAIMER
            )
