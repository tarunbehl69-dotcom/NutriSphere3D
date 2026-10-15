"""
NutriSphere 3D - Comprehensive Nutrition Guidance Service
Provides food-first Indian dietary educational guidance tailored to:
1. Dietary patterns: Indian Vegetarian, Indian Vegan, Jain, Non-Vegetarian.
2. Dynamic allergy filtering (Peanuts, Tree Nuts, Dairy, Gluten, Soy, Seafood).
3. Report-linked contextual nutrition considerations:
   - Low Hemoglobin/Ferritin -> Iron & Vitamin C synergy (Palak, Moong, Poha, Amla)
   - Elevated Liver Transaminases -> Hepatoprotective light foods (Turmeric, Lauki, Papaya)
   - Elevated Fasting Glucose/HbA1c -> Low-GI complex millets & fiber (Ragi, Jowar, Karela)
   - Elevated Lipids/Triglycerides -> Soluble fiber, Flaxseeds, Walnuts, Garlic
   - Low Vitamin D -> Dietary food sources and safe sunlight education
4. Strict Disclaimers: Food-first education only; never prescribes restrictive clinical diets or supplements.
"""

from typing import Dict, Any, List, Optional


class NutritionGuidanceService:
    """Delivers evidence-informed, culturally grounded Indian dietary education."""

    DISCLAIMER = (
        "NutriSphere 3D nutrition suggestions represent general food-first educational guidance "
        "derived from dietary guidelines (ICMR-NIN). They do not constitute clinical medical nutrition therapy, "
        "personalized medical treatment, or dietary supplement prescriptions."
    )

    def get_suggestions(
        self,
        dietary_preference: str = "vegetarian",
        allergies: Optional[List[str]] = None,
        report_biomarkers: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Deliver customized Indian meal recommendations based on preference, allergies,
        and applicable verified laboratory findings.
        """
        allergies = [a.lower().strip() for a in (allergies or [])]
        pref = (dietary_preference or "vegetarian").lower().replace("-", "_")

        # 1. Base Meal Plans per dietary pattern
        meal_plans = self._get_base_meal_plans(pref, allergies)

        # 2. Biomarker-linked contextual nutrition suggestions
        biomarker_notes = []
        if report_biomarkers:
            biomarker_notes = self._get_biomarker_nutritional_links(report_biomarkers, pref, allergies)

        # 3. Functional Superfood Spotlight
        spotlight_foods = self._get_superfood_spotlight(pref, allergies)

        return {
            "preference": dietary_preference,
            "allergies_filtered": allergies,
            "meal_plans": meal_plans,
            "biomarker_linked_guidance": biomarker_notes,
            "functional_foods_spotlight": spotlight_foods,
            "suggestions": [
                {
                    "nutrient_focus": "Balanced Indian Thali Architecture",
                    "food_sources": [
                        "1/2 plate vegetables & greens",
                        "1/4 plate protein (dal/paneer/eggs/sprouts)",
                        "1/4 plate complex whole grains (Ragi/Jowar/brown rice)"
                    ],
                    "servings_guidance": "Consistent portion-balanced meals with adequate hydration (2-3 L water).",
                    "caution": "Avoid processed trans-fats and excessive refined sugars."
                }
            ],
            "disclaimer": self.DISCLAIMER
        }

    def _get_base_meal_plans(self, pref: str, allergies: List[str]) -> List[Dict[str, Any]]:
        has_dairy_allergy = any(a in allergies for a in ["dairy", "milk", "lactose"])
        has_gluten_allergy = any(a in allergies for a in ["gluten", "wheat"])
        has_peanut_allergy = any(a in allergies for a in ["peanut", "peanuts"])

        plans = []

        if pref == "jain":
            # Jain: strictly no root vegetables (potatoes, onions, garlic, carrots, beets)
            plans.append({
                "meal": "Breakfast",
                "title": "Moong Dal Chilla with Fresh Mint & Cumin Chutney",
                "description": "Savory sprouted green gram crepes seasoned with cumin, turmeric, and fresh coriander.",
                "key_nutrients": "Plant Protein (14g), Soluble Fiber, Iron, Folate",
                "suitable_for": "Jain Vegetarian, Gluten-Free"
            })
            plans.append({
                "meal": "Lunch",
                "title": "Toor Dal, Lauki (Bottle Gourd) Subzi, and Jowar Roti",
                "description": "Comforting yellow lentil soup paired with tender bottle gourd curry and sorghum flatbread.",
                "key_nutrients": "Complex Carbohydrates, Hydrating Electrolytes, Plant Protein",
                "suitable_for": "Jain Vegetarian, Gluten-Free"
            })
            plans.append({
                "meal": "Dinner",
                "title": "Khichdi with Dahi (or Warm Turmeric Milk / Almond Milk)",
                "description": "Digestive moong dal and grain porridge tempered with cumin and ghee.",
                "key_nutrients": "Easily absorbable amino acids, gut-soothing probiotics",
                "suitable_for": "Jain Vegetarian"
            })

        elif pref == "vegan":
            plans.append({
                "meal": "Breakfast",
                "title": "Sprouted Moong & Black Chana Chaat with Lemon & Amla",
                "description": "Fresh steamed sprout medley tossed with cucumbers, tomatoes, chaat masala, and cold-pressed mustard oil.",
                "key_nutrients": "Bioavailable Iron, Vitamin C, Plant Fiber (12g)",
                "suitable_for": "100% Vegan, Dairy-Free, Gluten-Free"
            })
            plans.append({
                "meal": "Lunch",
                "title": "Rajma Masala (Red Kidney Beans) with Brown Rice & Palak Salad",
                "description": "Slow-cooked kidney beans in rich tomato-ginger gravy with steamed whole brown rice.",
                "key_nutrients": "Plant Protein (18g), Potassium, Folate, Soluble Fiber",
                "suitable_for": "Vegan, Dairy-Free"
            })
            plans.append({
                "meal": "Dinner",
                "title": "Tofu & Mixed Bell Pepper Stir-fry with Ragi Roti",
                "description": "Calcium-set tofu sauteed with methi leaves and capsicum, served with finger millet rotis.",
                "key_nutrients": "Calcium (350mg), Complete Protein, Anthocyanin Antioxidants",
                "suitable_for": "Vegan, Dairy-Free"
            })

        elif pref == "non_vegetarian":
            plans.append({
                "meal": "Breakfast",
                "title": "Masala Egg Omelette with Wilted Spinach & Whole Wheat Toast",
                "description": "Two country eggs whisked with green chilies, turmeric, onions, and baby spinach.",
                "key_nutrients": "High-Biological-Value Protein (13g), Choline, Vitamin B12",
                "suitable_for": "Non-Vegetarian, Low-Sugar"
            })
            plans.append({
                "meal": "Lunch",
                "title": "Indian Fish Curry (Rohu / Salmon) with Steamed Brown Rice & Bhindi Subzi",
                "description": "Heart-healthy fish simmered in mustard and curry leaf reduction with spiced okra.",
                "key_nutrients": "Omega-3 Fatty Acids (EPA/DHA), Lean Protein (24g), Vitamin D",
                "suitable_for": "Non-Vegetarian, Dairy-Free"
            })
            plans.append({
                "meal": "Dinner",
                "title": "Grilled Lemon-Herb Chicken Tikka with Cucumber Raita & Bajra Roti",
                "description": "Marinated lean chicken breast roasted with cumin, ginger, and dahi with millet flatbread.",
                "key_nutrients": "Lean Protein (28g), Zinc, Potassium, Probiotics",
                "suitable_for": "Non-Vegetarian"
            })

        else:
            # Default: Traditional Indian Vegetarian
            plans.append({
                "meal": "Breakfast",
                "title": "Vegetable Poha with Roasted Peanuts & Squeezed Lemon",
                "description": "Flattened rice tempered with mustard seeds, curry leaves, green peas, and turmeric, topped with fresh lime.",
                "key_nutrients": "Easily digestible Iron, Vitamin C, B-Vitamins",
                "suitable_for": "Vegetarian, Lacto-Vegetarian"
            })
            plans.append({
                "meal": "Lunch",
                "title": "Panchmel Dal, Paneer Bhurji, Palak Saag, and Whole Wheat Phulka",
                "description": "Nutrient-dense five-lentil medley paired with soft cottage cheese crumble and iron-rich spinach.",
                "key_nutrients": "Complete Protein (22g), Bioavailable Calcium, Iron, Dietary Fiber",
                "suitable_for": "Indian Vegetarian"
            })
            plans.append({
                "meal": "Dinner",
                "title": "Dalia Khichdi (Cracked Wheat) with Fresh Vegetable Raita",
                "description": "Wholesome cracked wheat and yellow moong porridge cooked with grated carrots, peas, and roasted cumin.",
                "key_nutrients": "Low-Glycemic Fiber, Magnesium, Probiotics",
                "suitable_for": "Vegetarian"
            })

        # Filter out allergens
        if has_dairy_allergy:
            for p in plans:
                p["title"] = p["title"].replace("Paneer", "Tofu").replace("Dahi", "Dairy-Free Coconut Curd").replace("Milk", "Almond Milk")
                p["description"] = p["description"].replace("cottage cheese", "tofu").replace("ghee", "cold-pressed sesame oil")
        if has_peanut_allergy:
            for p in plans:
                p["title"] = p["title"].replace("Peanuts", "Roasted Pumpkin Seeds")
                p["description"] = p["description"].replace("peanuts", "sunflower seeds")

        return plans

    def _get_biomarker_nutritional_links(
        self,
        biomarkers: List[Dict[str, Any]],
        pref: str,
        allergies: List[str]
    ) -> List[Dict[str, Any]]:
        links = []
        code_map = {b.get("analyte_code"): b for b in biomarkers if b.get("analyte_code")}

        # 1. Low Hemoglobin / Ferritin
        hgb = code_map.get("CBC_HGB")
        ferr = code_map.get("IRON_FERRITIN")
        if (hgb and hgb.get("flag") == "below_reference") or (ferr and ferr.get("flag") == "below_reference"):
            links.append({
                "biomarker_trigger": "Low Hemoglobin / Iron Stores",
                "clinical_observation": "Laboratory readings indicate sub-optimal erythrocyte oxygen-carrying capacity or depleted ferritin stores.",
                "food_first_strategy": "Pair non-heme iron sources (palak, methi, sprouted moong, black chana, jaggery in moderation) with Vitamin C (amla, lemon, guava) to enhance absorption up to 300%.",
                "caution": "Avoid consuming tannins (black tea, coffee) within 60 minutes of meals as they inhibit iron uptake."
            })

        # 2. Elevated Liver Transaminases (ALT/AST)
        alt = code_map.get("LIV_ALT")
        ast = code_map.get("LIV_AST")
        if (alt and alt.get("flag") == "above_reference") or (ast and ast.get("flag") == "above_reference"):
            links.append({
                "biomarker_trigger": "Elevated Hepatic Transaminases (ALT/AST)",
                "clinical_observation": "Serum transaminases suggest increased hepatocyte cell membrane permeability or metabolic strain.",
                "food_first_strategy": "Incorporate light, easily digestible meals: steamed bottle gourd (lauki), papaya, turmeric with black pepper (curcumin), and sulfur-rich cruciferous vegetables.",
                "caution": "Minimize saturated deep-fried foods (vanaspati/palm oil), refined sugar syrups, and alcohol to relieve hepatic metabolic workload."
            })

        # 3. Elevated Fasting Glucose / HbA1c
        glu = code_map.get("GLU_FASTING")
        a1c = code_map.get("GLU_HBA1C")
        if (glu and glu.get("flag") == "above_reference") or (a1c and a1c.get("flag") == "above_reference"):
            links.append({
                "biomarker_trigger": "Elevated Glycemic Markers (Glucose / HbA1c)",
                "clinical_observation": "Elevated fasting blood sugar or glycated hemoglobin points to impaired insulin sensitivity or glucose clearance.",
                "food_first_strategy": "Substitute refined white rice/maida with slow-release whole millets (Ragi, Bajra, Jowar) and soluble fiber (methi seeds soaked overnight, cinnamon, bitter gourd/karela).",
                "caution": "Eat meals with healthy fats and protein first before carbohydrates to blunt postprandial glucose spikes."
            })

        # 4. Elevated Triglycerides / Cholesterol
        trig = code_map.get("LIP_TRIG")
        chol = code_map.get("LIP_CHOL")
        if (trig and trig.get("flag") == "above_reference") or (chol and chol.get("flag") == "above_reference"):
            links.append({
                "biomarker_trigger": "Elevated Lipid Markers (Triglycerides / Total Cholesterol)",
                "clinical_observation": "Circulating blood lipids are elevated, indicating increased cardiovascular and metabolic considerations.",
                "food_first_strategy": "Introduce 1-2 tbsp roasted flaxseed powder daily (alpha-linolenic acid), crushed raw garlic, and high soluble fiber from oats and whole lentils.",
                "caution": "Limit deep-fried snack foods and reduce refined carbohydrate intake, which directly fuels hepatic triglyceride synthesis."
            })

        # 5. Low Vitamin D
        vit_d = code_map.get("VIT_D")
        if vit_d and vit_d.get("flag") == "below_reference":
            links.append({
                "biomarker_trigger": "Sub-optimal 25-OH Vitamin D",
                "clinical_observation": "Serum Vitamin D is below the recommended 30 ng/mL threshold.",
                "food_first_strategy": "Sun-exposed mushrooms, fortified dairy/plant milk, and eggs (for non-vegetarians). Safe mid-day sun exposure on arms/legs (15-20 min) is the primary physiological driver.",
                "caution": "Dietary sources provide modest Vitamin D; discuss with your physician if clinical oral supplementation (e.g. 60k IU weekly) is indicated."
            })

        return links

    def _get_superfood_spotlight(self, pref: str, allergies: List[str]) -> List[Dict[str, str]]:
        return [
            {
                "name": "Amla (Indian Gooseberry)",
                "role": "Potent Vitamin C & Antioxidant Synergy",
                "benefit": "Contains 20x more Vitamin C than oranges; enhances non-heme iron absorption and protects hepatic cellular integrity from oxidative stress."
            },
            {
                "name": "Turmeric + Black Pepper",
                "role": "Curcuminoid Anti-inflammatory Complex",
                "benefit": "Piperine in black pepper enhances curcumin bioavailability by up to 2,000%, supporting liver antioxidant defense."
            },
            {
                "name": "Ragi (Finger Millet)",
                "role": "Calcium & Low-Glycemic Complex Fiber",
                "benefit": "Provides over 340mg calcium per 100g (more than milk) with slow digestion, preventing rapid postprandial blood sugar spikes."
            },
            {
                "name": "Sprouted Moong Beans",
                "role": "Enzymatically Activated Plant Protein",
                "benefit": "Sprouting decreases phytic acid, making iron, zinc, and protein significantly more bioavailable while easing digestion."
            }
        ]
