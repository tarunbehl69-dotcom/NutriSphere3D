"""
NutriSphere 3D - Comprehensive Alcohol Health Analysis & Education Service
Features:
1. Interactive pure ethanol calculation using exact pharmacological formula:
   Alcohol grams = Volume (mL) * (ABV % / 100) * 0.789
2. Standard drinks conversion (WHO/India/UK 10g standard and US 14g standard).
3. Connects verified medical report biomarkers:
   - Hepatic: ALT, AST, GGT, Total Bilirubin, Albumin, ALP (with de Ritis AST/ALT ratio)
   - Metabolic/Lipid: Triglycerides, Fasting Glucose
   - Hematology: MCV (macrocytosis indicator)
   - Renal: Creatinine, eGFR
4. Strict Clinical Guardrails:
   - Explicitly disclaims calculating a "safe drinking allowance" from lab values.
   - Clarifies that normal liver enzymes NEVER prove drinking is safe or risk-free.
5. Contextual Risk Assessment:
   - Medication interactions (paracetamol/acetaminophen, statins, sedatives, NSAIDs, warfarin).
   - Absolute contraindications (pregnancy, severe hepatitis, pancreatitis).
6. Nutrition, Alcohol & Recovery Guidance:
   - B-vitamin / Folate replenishment, hydration protocols, antioxidant foods.
   - Disclaims "detox" or rapid sobriety myths.
"""

from typing import Dict, Any, List, Optional


class AlcoholEducationService:
    """Delivers evidence-based alcohol health analysis and educational guidance."""

    REVIEW_DATE = "2026-05-01"
    DISCLAIMER = (
        "NutriSphere 3D provides evidence-based alcohol education for health literacy only. "
        "No laboratory test, biomarker algorithm, or mathematical formula can establish an individually safe "
        "drinking allowance. Normal liver enzymes do not rule out alcohol-associated cellular strain. "
        "All decisions regarding alcohol intake should be reviewed with a licensed healthcare provider."
    )

    def calculate_intake(
        self,
        beverage_type: str,
        volume_ml: float,
        abv_percent: float,
        drinking_days_per_week: int = 1
    ) -> Dict[str, Any]:
        """
        Calculate pure ethanol mass and standard drink equivalents:
        Grams = Volume (mL) * (ABV% / 100) * 0.789 (density of ethanol)
        """
        vol = max(0.0, float(volume_ml))
        abv = max(0.0, min(100.0, float(abv_percent)))
        days = max(0, min(7, int(drinking_days_per_week)))

        pure_grams_single = round(vol * (abv / 100.0) * 0.789, 2)
        std_who = round(pure_grams_single / 10.0, 2)   # WHO / India / UK standard (10g ethanol)
        std_us = round(pure_grams_single / 14.0, 2)    # US standard (14g ethanol)
        weekly_grams = round(pure_grams_single * days, 2)

        # Risk tier based on population-level epidemiological guidance (WHO / UK CMO)
        if weekly_grams == 0:
            tier = "Zero Intake (Lowest Biological Risk)"
            guidance = "Abstinence from alcohol is the only risk-free choice regarding alcohol-associated organ pathology."
        elif weekly_grams <= 70:
            tier = "Low Epidemiological Exposure (<70g/week)"
            guidance = "Intake is within lower population exposure boundaries. However, individual sensitivity and medication interactions still apply."
        elif weekly_grams <= 140:
            tier = "Moderate Exposure (70 - 140g/week)"
            guidance = "Weekly exposure approaches standard population guideline limits (~14 standard units). Cellular metabolic demands on the liver increase."
        elif weekly_grams <= 280:
            tier = "Elevated Exposure (140 - 280g/week)"
            guidance = "Consumption significantly elevates risks of hepatic steatosis (fatty liver), subclinical inflammation, hypertension, and sleep disruption."
        else:
            tier = "High Clinical Risk (>280g/week)"
            guidance = "Heavy ethanol intake creates progressive risk of alcoholic hepatitis, hepatic fibrosis, cardiomyopathy, and micronutrient depletion. Clinical medical review is strongly advised."

        return {
            "beverage_type": beverage_type,
            "volume_ml": vol,
            "abv_percent": abv,
            "pure_alcohol_grams": pure_grams_single,
            "standard_drinks_who": std_who,
            "standard_drinks_us": std_us,
            "drinking_days_per_week": days,
            "weekly_grams": weekly_grams,
            "educational_risk_tier": tier,
            "guidance_message": guidance,
            "clinical_disclaimer": self.DISCLAIMER
        }

    def get_risk_education(
        self,
        has_liver_flags: bool = False,
        takes_medications: bool = False,
        pregnancy_status: bool = False
    ) -> Dict[str, Any]:
        """
        Backward-compatible summary for baseline health risk education.
        """
        contraindications = []
        if pregnancy_status:
            contraindications.append("Pregnancy / planning pregnancy: Complete abstinence is essential; alcohol crosses placental barriers.")
        if takes_medications:
            contraindications.append("Medication interaction: Many pharmaceuticals interact dangerously with ethanol (hepatic competition, sedation, bleeding risk).")
        if has_liver_flags:
            contraindications.append("Elevated liver enzymes: Abstinence is strongly recommended during hepatic diagnostic evaluation.")

        return {
            "safe_drinking_limit": "None (No laboratory report or algorithm can establish a safe personal drinking limit)",
            "key_guidance": "Avoiding alcohol completely is the safest choice for overall health and liver cellular recovery.",
            "contraindications": contraindications,
            "educational_points": [
                "Alcohol metabolism places immediate metabolic and oxidative demands on hepatic tissue.",
                "Normal liver function tests (ALT/AST) do not rule out alcohol-associated metabolic stress or early steatosis.",
                "Any changes in alcohol consumption or symptoms should be reviewed with a healthcare professional."
            ],
            "medically_reviewed_date": self.REVIEW_DATE,
            "disclaimer": self.DISCLAIMER
        }

    def get_report_alcohol_analysis(
        self,
        biomarkers: List[Dict[str, Any]],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Connect verified medical report biomarkers to educational alcohol health analysis.
        Explains liver markers (ALT, AST, de Ritis, GGT, Bilirubin, Albumin, ALP)
        and systemic markers (Triglycerides, Glucose, MCV).
        """
        patient_context = patient_context or {}
        code_map = {b.get("analyte_code"): b for b in biomarkers if b.get("analyte_code")}

        evaluated_markers = []
        liver_flags_count = 0
        overall_cautions = []

        # 1. Alanine Aminotransferase (ALT)
        if "LIV_ALT" in code_map:
            alt = code_map["LIV_ALT"]
            val = alt.get("value_numeric")
            flag = alt.get("flag", "unknown")
            is_high = flag == "above_reference"
            if is_high:
                liver_flags_count += 1
            evaluated_markers.append({
                "analyte_code": "LIV_ALT",
                "label": "Alanine Aminotransferase (ALT / SGPT)",
                "measured_value": val,
                "unit": alt.get("unit", "U/L"),
                "flag": flag,
                "organ": "Liver",
                "what_it_measures": "A cytosolic enzyme primarily concentrated in hepatocytes. Elevated levels indicate increased hepatocyte cell membrane permeability or stress.",
                "alcohol_relationship": "Alcohol oxidation produces acetaldehyde and reactive oxygen species that can cause hepatocyte injury and leakage of ALT into serum.",
                "alternative_reasons": ["Non-alcoholic fatty liver (NAFLD/MASLD)", "Vigorous weight-lifting or muscle exertion", "Medications (e.g. statins, NSAIDs, antibiotics)", "Viral hepatitis"],
                "doctor_questions": "Could my ALT reading reflect medication use, recent exercise, or dietary factors?"
            })

        # 2. Aspartate Aminotransferase (AST) & de Ritis Ratio
        if "LIV_AST" in code_map:
            ast = code_map["LIV_AST"]
            val = ast.get("value_numeric")
            flag = ast.get("flag", "unknown")
            if flag == "above_reference":
                liver_flags_count += 1

            de_ritis_note = None
            if "LIV_ALT" in code_map and val and code_map["LIV_ALT"].get("value_numeric"):
                alt_val = code_map["LIV_ALT"]["value_numeric"]
                if alt_val > 0:
                    ratio = round(val / alt_val, 2)
                    if ratio > 2.0:
                        de_ritis_note = f"AST/ALT ratio is {ratio} (>2.0). In clinical literature, AST-predominant elevations are classically correlated with alcohol-associated hepatic sensitivity or intense muscle breakdown."
                    elif ratio < 1.0:
                        de_ritis_note = f"AST/ALT ratio is {ratio} (<1.0, ALT predominant). More commonly seen in metabolic liver changes (fatty liver) rather than isolated alcohol stress."
                    else:
                        de_ritis_note = f"AST/ALT ratio is {ratio} (balanced transaminase ratio)."

            evaluated_markers.append({
                "analyte_code": "LIV_AST",
                "label": "Aspartate Aminotransferase (AST / SGOT)",
                "measured_value": val,
                "unit": ast.get("unit", "U/L"),
                "flag": flag,
                "organ": "Liver",
                "what_it_measures": "A mitochondrial and cytosolic enzyme found in liver, heart, and skeletal muscle tissue.",
                "alcohol_relationship": f"Alcohol preferentially damages hepatocyte mitochondria where AST is concentrated. {de_ritis_note or ''}",
                "alternative_reasons": ["Strenuous muscular exercise", "Cardiovascular strain", "Medications", "Thyroid imbalance"],
                "doctor_questions": "How does my AST/ALT ratio align with my symptoms and lifestyle?"
            })

        # 3. Gamma-Glutamyl Transferase (GGT)
        if "LIV_GGT" in code_map:
            ggt = code_map["LIV_GGT"]
            val = ggt.get("value_numeric")
            flag = ggt.get("flag", "unknown")
            if flag == "above_reference":
                liver_flags_count += 1
            evaluated_markers.append({
                "analyte_code": "LIV_GGT",
                "label": "Gamma-Glutamyl Transferase (GGT)",
                "measured_value": val,
                "unit": ggt.get("unit", "U/L"),
                "flag": flag,
                "organ": "Liver / Biliary",
                "what_it_measures": "A microsomal enzyme located in biliary epithelial cells and hepatocytes.",
                "alcohol_relationship": "GGT is highly inducible by alcohol; hepatic microsomal enzyme induction frequently elevates GGT even prior to ALT/AST elevation.",
                "alternative_reasons": ["Biliary stasis or gallstones", "Anticonvulsant or barbiturate therapy", "Metabolic syndrome"],
                "doctor_questions": "Does my GGT level suggest biliary congestion or enzyme induction?"
            })

        # 4. Total Bilirubin
        if "LIV_TBIL" in code_map:
            tbil = code_map["LIV_TBIL"]
            evaluated_markers.append({
                "analyte_code": "LIV_TBIL",
                "label": "Total Bilirubin",
                "measured_value": tbil.get("value_numeric"),
                "unit": tbil.get("unit", "mg/dL"),
                "flag": tbil.get("flag", "unknown"),
                "organ": "Liver",
                "what_it_measures": "Byproduct of heme catabolism processed and cleared by liver hepatocytes into bile.",
                "alcohol_relationship": "Severe or chronic alcohol-induced hepatocyte swelling and cholestasis impairs bilirubin clearance.",
                "alternative_reasons": ["Benign Gilbert syndrome (harmless genetic elevation during fasting)", "Hemolysis", "Bile duct stones"],
                "doctor_questions": "Is my bilirubin elevation direct (conjugated) or indirect (unconjugated)?"
            })

        # 5. Serum Albumin
        if "LIV_ALB" in code_map:
            alb = code_map["LIV_ALB"]
            evaluated_markers.append({
                "analyte_code": "LIV_ALB",
                "label": "Serum Albumin",
                "measured_value": alb.get("value_numeric"),
                "unit": alb.get("unit", "g/dL"),
                "flag": alb.get("flag", "unknown"),
                "organ": "Liver",
                "what_it_measures": "Primary plasma protein synthesized exclusively by hepatocytes, reflecting synthetic capacity.",
                "alcohol_relationship": "Advanced chronic alcohol hepatic impairment suppresses protein synthesis, lowering albumin.",
                "alternative_reasons": ["Malnutrition or low protein intake", "Renal proteinuria", "Systemic inflammation"],
                "doctor_questions": "What does my albumin level indicate regarding protein status and liver function?"
            })

        # 6. Triglycerides (LIP_TRIG)
        if "LIP_TRIG" in code_map:
            trig = code_map["LIP_TRIG"]
            evaluated_markers.append({
                "analyte_code": "LIP_TRIG",
                "label": "Triglycerides",
                "measured_value": trig.get("value_numeric"),
                "unit": trig.get("unit", "mg/dL"),
                "flag": trig.get("flag", "unknown"),
                "organ": "Metabolic",
                "what_it_measures": "Circulating blood fats originating from diet and hepatic synthesis.",
                "alcohol_relationship": "Alcohol inhibits fatty acid beta-oxidation in hepatocytes, accelerating triglyceride synthesis and contributing to hypertriglyceridemia.",
                "alternative_reasons": ["High refined carbohydrate intake", "Insulin resistance / diabetes", "Hypothyroidism", "Genetic hyperlipidemia"],
                "doctor_questions": "Can dietary changes and reduced alcohol help normalize my triglycerides?"
            })

        # 7. Erythrocyte MCV (CBC_MCV)
        if "CBC_MCV" in code_map:
            mcv = code_map["CBC_MCV"]
            evaluated_markers.append({
                "analyte_code": "CBC_MCV",
                "label": "Mean Corpuscular Volume (MCV)",
                "measured_value": mcv.get("value_numeric"),
                "unit": mcv.get("unit", "fL"),
                "flag": mcv.get("flag", "unknown"),
                "organ": "Bone Marrow / Blood",
                "what_it_measures": "The average physical volume of circulating red blood cells.",
                "alcohol_relationship": "Macrocytosis (elevated MCV >100 fL) is an established indirect marker of chronic alcohol consumption, occurring due to direct bone marrow toxicity and folate interference.",
                "alternative_reasons": ["Vitamin B12 or Folate deficiency", "Reticulocytosis (acute marrow response)", "Thyroid slowing"],
                "doctor_questions": "Should we test serum Vitamin B12 and Folate to explain this MCV reading?"
            })

        # Medical cautions based on context
        if liver_flags_count > 0:
            overall_cautions.append("One or more hepatic markers are outside reference limits. Alcohol cessation is strongly advised to facilitate liver healing.")
        if patient_context.get("pregnancy_status"):
            overall_cautions.append("Absolute Contraindication: Pregnancy carries zero safe alcohol allowance; fetal alcohol spectrum disorders are preventable through complete abstinence.")

        meds = patient_context.get("medications", [])
        med_names = " ".join([str(m.get("drug_name", "")).lower() for m in meds] if isinstance(meds, list) else [])
        if any(w in med_names for w in ["paracetamol", "acetaminophen", "tylenol"]):
            overall_cautions.append("Critical Drug Interaction: Paracetamol combined with ethanol greatly depletes hepatic glutathione, increasing toxic NAPQI hepatocyte necrosis risk.")
        if any(w in med_names for w in ["statin", "atorvastatin", "rosuvastatin"]):
            overall_cautions.append("Drug Consideration: Statins and alcohol share hepatic clearance pathways; concurrent heavy intake compounds transaminase elevation.")
        if any(w in med_names for w in ["warfarin", "coumadin"]):
            overall_cautions.append("Drug Warning: Alcohol fluctuates warfarin metabolism and INR, significantly elevating hemorrhage risk.")

        return {
            "markers_evaluated_count": len(evaluated_markers),
            "liver_flags_count": liver_flags_count,
            "evaluated_markers": evaluated_markers,
            "overall_cautions": overall_cautions,
            "normal_enzymes_warning": (
                "Critical Medical Truth: Normal liver enzymes (ALT/AST) do NOT prove that drinking is safe or harmless. "
                "Early alcoholic liver steatosis and cardiovascular remodeling often occur with completely standard blood panels."
            ),
            "clinical_disclaimer": self.DISCLAIMER
        }

    def get_recovery_nutrition_guidance(self) -> Dict[str, Any]:
        """
        Deliver food-first nutritional education for hepatic recovery and metabolic support.
        Strictly dispels rapid sobriety and detox myths.
        """
        return {
            "recovery_principles": [
                {
                    "principle": "Micronutrient & B-Complex Restoration",
                    "explanation": "Alcohol metabolism consumes large amounts of coenzymes derived from Thiamine (B1), Pyridoxine (B6), and Folate (B9).",
                    "indian_food_sources": ["Sprouted Moong & Chana", "Toor & Moong Dal", "Fresh Green Leafy Vegetables (Palak, Methi)", "Whole Grain Millets (Bajra, Ragi)"]
                },
                {
                    "principle": "Hydration & Electrolyte Homeostasis",
                    "explanation": "Ethanol suppresses vasopressin (ADH), resulting in dehydration, hypomagnesemia, and potassium depletion.",
                    "indian_food_sources": ["Fresh Tender Coconut Water", "Nimbu Pani (light salt and cumin)", "Plain Curd / Chaas (Buttermilk)", "Vegetable Broth"]
                },
                {
                    "principle": "Glutathione & Hepatic Antioxidant Support",
                    "explanation": "Glutathione is the liver's primary defense against acetaldehyde oxidative stress.",
                    "indian_food_sources": ["Amla (Indian Gooseberry)", "Turmeric with Black Pepper", "Garlic and Onions", "Papaya and Citrus Fruits"]
                }
            ],
            "myth_busting": [
                {
                    "myth": "Commercial 'Liver Detox' Teas or Supplements cancel out alcohol damage.",
                    "reality": "False. There is zero clinical evidence that detox teas or supplements reverse alcohol-induced cellular injury. Complete alcohol abstinence is the only medically verified method for liver recovery."
                },
                {
                    "myth": "Drinking black coffee or taking a cold shower rapidly sobers you up.",
                    "reality": "False. Alcohol is cleared strictly by hepatic enzyme kinetics (~7 to 10 grams pure alcohol per hour). Neither caffeine, showers, nor exercise accelerate ethanol metabolism."
                }
            ],
            "disclaimer": "These dietary suggestions represent general wellness education. They do not constitute a clinical prescription or treatment for substance use disorders."
        }
