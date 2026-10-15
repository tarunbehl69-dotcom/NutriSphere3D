"""
NutriSphere X — Verified Anatomical Mapping Registry
Single Source of Truth for Human Anatomy, Organ Systems, and Laboratory Test Associations.

Provides Level 1 (Everyday Plain English) and Level 2 (Clinical Medical Depth) descriptions,
multi-organ associations, authentic 3D mesh identifiers, camera targets, and validation statuses.
"""

from typing import Dict, List, Any, Optional

ORGAN_REGISTRY: Dict[str, Dict[str, Any]] = {
    "liver": {
        "organ_id": "liver",
        "display_name": "Liver",
        "medical_name": "Hepar",
        "system": "Digestive system",
        "system_id": "digestive",
        "level1_role": "Your Body's Master Filter & Energy Center: Cleans your blood, breaks down nutrients from food, stores energy, and helps digest fats.",
        "level2_medical": "The liver is the principal metabolic factory of the human body. Hepatocytes synthesize albumin, blood coagulation factors, and bile acids. It processes metabolic byproducts, detoxifies medications and xenobiotics, and balances gluconeogenesis with glycogen storage.",
        "camera_pos": [-0.05, 0.38, 0.55],
        "camera_target": [-0.03, 0.35, 0.04],
        "anchor_world": [-0.03, 0.35, 0.04],
        "color_hex": 0xf97316,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["liver", "hepar", "segment of liver", "gallbladder", "bile duct"],
        "system_source": "digestive",
        "tests": [
            {
                "code": "LIV_ALT",
                "name": "ALT (Alanine Aminotransferase)",
                "level1_meaning": "A blood enzyme primarily found inside liver cells.",
                "level2_clinical": "Alanine Aminotransferase leaks into circulation when hepatocyte cell membranes experience stress or increased permeability. An elevation indicates hepatocellular strain; it is not a permanent disease diagnosis on its own.",
                "multi_organ_note": "Highly concentrated in liver parenchyma; evaluated alongside metabolic factors and medication history."
            },
            {
                "code": "LIV_AST",
                "name": "AST (Aspartate Aminotransferase)",
                "level1_meaning": "An enzyme measured in the blood that comes from the liver, heart, and skeletal muscle.",
                "level2_clinical": "Aspartate Aminotransferase is present in hepatocytes, cardiac myocytes, and skeletal muscle fibers. Evaluated in clinical ratio with ALT (De Ritis ratio).",
                "multi_organ_note": "Not liver-specific; intense physical workouts, heavy lifting, or muscular exertion can temporarily elevate AST without liver pathology."
            },
            {
                "code": "LIV_ALP",
                "name": "ALP (Alkaline Phosphatase)",
                "level1_meaning": "An enzyme found in the liver bile ducts and growing bones.",
                "level2_clinical": "Alkaline phosphatase is concentrated in biliary canalicular membranes and active osteoblast sites. Evaluated to differentiate biliary flow stasis from active bone remodeling.",
                "multi_organ_note": "Can reflect active bone remodeling (Vitamin D deficiency, fracture repair) or biliary tract flow."
            },
            {
                "code": "LIV_TBIL",
                "name": "Total Bilirubin",
                "level1_meaning": "Natural yellow pigment produced during normal breakdown of old red blood cells.",
                "level2_clinical": "Bilirubin is processed by hepatic glucuronidation into water-soluble conjugated forms for biliary excretion. Evaluated as conjugated vs unconjugated fractions.",
                "multi_organ_note": "Elevations can reflect pre-hepatic red cell clearance (hemolysis) or post-hepatic biliary drainage."
            },
            {
                "code": "LIV_ALB",
                "name": "Serum Albumin",
                "level1_meaning": "The primary circulating protein synthesized exclusively by your liver.",
                "level2_clinical": "Maintains intravascular oncotic pressure and transports hormones, fatty acids, and drugs. A marker of sustained hepatic synthetic reserve and nutritional protein intake.",
                "multi_organ_note": "Reflects liver synthesis, dietary protein adequacy, and renal retention."
            }
        ],
        "lifestyle": {
            "nutrition": "Emphasize antioxidant-rich foods: amla (Indian gooseberry), turmeric, cruciferous vegetables (cauliflower, cabbage), garlic, and whole pulses (moong, masoor dal).",
            "alcohol": "Over 90% of ingested alcohol is metabolized by hepatic alcohol dehydrogenase. Limiting intake prevents steatotic lipid accumulation and gives hepatocytes rest."
        }
    },
    "heart": {
        "organ_id": "heart",
        "display_name": "Heart",
        "medical_name": "Cor",
        "system": "Cardiovascular system",
        "system_id": "cardiovascular",
        "level1_role": "Your Body's Life Pump: Beats about 100,000 times a day to pump fresh oxygen and nutrients through blood vessels to every organ.",
        "level2_medical": "Four-chambered muscular organ comprising the left and right atria and ventricles, synchronized by the sinoatrial and atrioventricular conduction systems. Coronary arteries supply the contracting myocardium.",
        "camera_pos": [0.05, 0.45, 0.50],
        "camera_target": [0.04, 0.43, 0.03],
        "anchor_world": [0.04, 0.43, 0.03],
        "color_hex": 0xef4444,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["ventricle", "atrium", "ascending aorta", "pulmonary trunk", "coronary", "cardiac", "myocard", "papillary muscle"],
        "system_source": "cardiovascular",
        "tests": [
            {
                "code": "LIP_LDL",
                "name": "LDL Cholesterol",
                "level1_meaning": "Cholesterol transported through your circulation inside lipoprotein particles.",
                "level2_clinical": "Low-Density Lipoprotein transports cholesterol to peripheral tissues. Elevated circulating ApoB/LDL particles can penetrate the vascular endothelial intima over years.",
                "multi_organ_note": "Synthesized and cleared via hepatic LDL receptors; circulates systemically through all vascular beds."
            },
            {
                "code": "LIP_APOB",
                "name": "Apolipoprotein B (ApoB)",
                "level1_meaning": "A direct count of all cholesterol-carrying particles in your bloodstream.",
                "level2_clinical": "Each atherogenic lipoprotein particle (LDL, VLDL, IDL) carries exactly one ApoB molecule, making it a direct particle-count biomarker superior to calculated LDL alone.",
                "multi_organ_note": "Produced in liver and intestine."
            },
            {
                "code": "CAR_TROP",
                "name": "Troponin I",
                "level1_meaning": "A specialized protein found inside heart muscle cells.",
                "level2_clinical": "Cardiac Troponin I is released specifically when myocardial cells undergo acute ischemic or inflammatory membrane stress. Evaluated in clinical care settings.",
                "multi_organ_note": "Highly specific to cardiac myocardium."
            },
            {
                "code": "LIP_TRIG",
                "name": "Triglycerides",
                "level1_meaning": "The standard form of dietary and circulating fat stored from excess calories.",
                "level2_clinical": "Esterified fatty acids packaged by the liver into VLDL. Highly responsive to refined dietary carbohydrates, simple sugars, and alcohol intake.",
                "multi_organ_note": "Synthesized in liver, stored in adipose tissue, circulated to cardiac and skeletal muscle for fuel."
            }
        ],
        "lifestyle": {
            "nutrition": "Choose soluble fiber-rich foods: oats (beta-glucan), flaxseeds, chia seeds, walnuts, and home-cooked low-sodium vegetable curries.",
            "alcohol": "Excess alcohol intake raises blood pressure and sympathetic tone. Moderating intake helps peripheral blood vessels relax and maintains healthy arterial elasticity."
        }
    },
    "left_kidney": {
        "organ_id": "left_kidney",
        "display_name": "Left Kidney",
        "medical_name": "Ren Sinister",
        "system": "Renal & Urinary system",
        "system_id": "renal",
        "level1_role": "Left Water & Salt Filter: Filters blood continuously, removes waste through urine, and balances body hydration.",
        "level2_medical": "Retroperitoneal organ situated between T12 and L3. Composed of approximately 1 million nephrons that perform glomerular filtration, tubular reabsorption, and acid-base maintenance while secreting erythropoietin.",
        "camera_pos": [0.08, 0.32, -0.45],
        "camera_target": [0.05, 0.30, -0.01],
        "anchor_world": [0.05, 0.30, -0.01],
        "color_hex": 0xe11d48,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["kidney.l", "renal pelvis.l", "ureter.l"],
        "system_source": "renal",
        "tests": [
            {
                "code": "REN_CREAT",
                "name": "Serum Creatinine",
                "level1_meaning": "A blood measurement used to help assess kidney filtration function.",
                "level2_clinical": "Creatinine is a steady metabolic breakdown product of muscle creatine. Because it is filtered freely by glomeruli without significant reabsorption, it reflects renal clearance capacity.",
                "multi_organ_note": "Produced constantly by skeletal muscle mass; excreted almost entirely by renal nephrons."
            },
            {
                "code": "REN_EGFR",
                "name": "eGFR (Estimated Glomerular Filtration Rate)",
                "level1_meaning": "Estimated rate showing how many milliliters of blood your kidneys clean each minute.",
                "level2_clinical": "Mathematical index calculated from serum creatinine, age, and sex (CKD-EPI equation). Values above 60 mL/min/1.73m² indicate stable filtration.",
                "multi_organ_note": "Reflects overall systemic renal perfusion and filtration efficiency."
            },
            {
                "code": "REN_BUN",
                "name": "Blood Urea Nitrogen (BUN)",
                "level1_meaning": "A waste product from digested dietary protein cleared from your blood by the kidneys.",
                "level2_clinical": "Urea is formed in the liver during protein deamination and excreted through renal tubules. The BUN-to-Creatinine ratio helps distinguish pre-renal dehydration from intrinsic renal changes.",
                "multi_organ_note": "Produced in liver from dietary protein; filtered and reabsorbed by renal tubules."
            }
        ],
        "lifestyle": {
            "nutrition": "Stay well-hydrated with fresh water, avoid excess dietary sodium in packaged snacks, and enjoy fresh fruits like apples, berries, and cucumber.",
            "alcohol": "Alcohol suppresses antidiuretic hormone (ADH), inducing diuresis and rapid fluid loss. Rehydrate with water and electrolytes."
        }
    },
    "right_kidney": {
        "organ_id": "right_kidney",
        "display_name": "Right Kidney",
        "medical_name": "Ren Dexter",
        "system": "Renal & Urinary system",
        "system_id": "renal",
        "level1_role": "Right Water & Salt Filter: Located just beneath the liver, working alongside the left kidney to purify blood.",
        "level2_medical": "Situated slightly lower than the left kidney to accommodate the right hepatic lobe. Shares identical nephron filtration architecture and endocrine roles (renin secretion, 1-alpha-hydroxylation of Vitamin D).",
        "camera_pos": [-0.08, 0.30, -0.45],
        "camera_target": [-0.05, 0.28, -0.01],
        "anchor_world": [-0.05, 0.28, -0.01],
        "color_hex": 0xe11d48,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["kidney.r", "renal pelvis.r", "ureter.r"],
        "system_source": "renal",
        "tests": [
            {
                "code": "REN_CREAT",
                "name": "Serum Creatinine",
                "level1_meaning": "A blood measurement used to help assess kidney filtration function.",
                "level2_clinical": "Creatinine reflects bilateral renal clearance. Evaluated together with eGFR.",
                "multi_organ_note": "Filtered symmetrically across both kidneys."
            },
            {
                "code": "REN_EGFR",
                "name": "eGFR",
                "level1_meaning": "Estimated rate of blood filtration across both kidneys.",
                "level2_clinical": "Reflects combined glomerular filtration capacity of both kidneys.",
                "multi_organ_note": "Combined bilateral filtration index."
            }
        ],
        "lifestyle": {
            "nutrition": "Maintain consistent daily fluid intake and minimize unnecessary NSAID painkiller use without physician guidance.",
            "alcohol": "Avoid binge alcohol episodes that cause acute dehydration and temporary renal perfusion drops."
        }
    },
    "kidneys": {
        "organ_id": "kidneys",
        "display_name": "Kidneys (Both)",
        "medical_name": "Renes",
        "system": "Renal & Urinary system",
        "system_id": "renal",
        "level1_role": "Your Natural Water & Salt Filters: Paired organs filtering around 200 quarts of fluid daily to balance water and electrolytes.",
        "level2_medical": "Bilateral renal system maintaining fluid balance, acid-base homeostasis, systemic arterial pressure (renin-angiotensin-aldosterone axis), and bone mineral regulation via calcitriol synthesis.",
        "camera_pos": [0.00, 0.28, -0.55],
        "camera_target": [0.00, 0.26, -0.01],
        "anchor_world": [0.00, 0.26, -0.01],
        "color_hex": 0xe11d48,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["kidney.l", "kidney.r", "renal pelvis.l", "renal pelvis.r", "ureter.l", "ureter.r"],
        "system_source": "renal",
        "tests": [
            {
                "code": "REN_CREAT",
                "name": "Serum Creatinine",
                "level1_meaning": "A blood measurement used to help assess kidney function.",
                "level2_clinical": "Standard filtration biomarker cleared by glomerular filtration.",
                "multi_organ_note": "Generated by muscle; cleared by kidneys."
            },
            {
                "code": "REN_EGFR",
                "name": "eGFR",
                "level1_meaning": "Estimated rate showing how many milliliters of blood your kidneys clean each minute.",
                "level2_clinical": "Estimated Glomerular Filtration Rate; values ≥ 60 mL/min/1.73m² confirm healthy filtration.",
                "multi_organ_note": "Primary global marker of filtration capacity."
            },
            {
                "code": "REN_BUN",
                "name": "Blood Urea Nitrogen (BUN)",
                "level1_meaning": "Protein breakdown waste cleared by the kidneys.",
                "level2_clinical": "Evaluated alongside creatinine to assess hydration balance.",
                "multi_organ_note": "Formed in liver, excreted in urine."
            }
        ],
        "lifestyle": {
            "nutrition": "Drink 2 to 2.5 liters of water daily, limit high-sodium processed foods, and consume fresh antioxidant fruits.",
            "alcohol": "Rehydrate with water and coconut water after any alcohol consumption to restore fluid balance."
        }
    },
    "lungs": {
        "organ_id": "lungs",
        "display_name": "Lungs",
        "medical_name": "Pulmones",
        "system": "Respiratory system",
        "system_id": "respiratory",
        "level1_role": "Your Oxygen Exchange Center: Takes in fresh oxygen when you breathe in and releases carbon dioxide waste when you breathe out.",
        "level2_medical": "Bilateral pulmonary organs featuring 5 lobes (3 right, 2 left) containing branching bronchial trees terminating in roughly 300 million alveoli, where alveolar-capillary gas diffusion occurs.",
        "camera_pos": [0.00, 0.48, 0.65],
        "camera_target": [0.01, 0.46, -0.01],
        "anchor_world": [0.01, 0.46, -0.01],
        "color_hex": 0x0ea5e9,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["lung", "lobe", "bronch", "pleura", "trachea"],
        "system_source": "respiratory",
        "tests": [
            {
                "code": "CBC_HGB",
                "name": "Hemoglobin",
                "level1_meaning": "The primary iron-containing protein in your red blood cells that carries oxygen from your lungs to your body.",
                "level2_clinical": "Hemoglobin molecules bind oxygen reversibly in pulmonary capillaries at high pO2 and release it in peripheral tissues. It is not an indicator of direct lung tissue injury.",
                "multi_organ_note": "Synthesized in bone marrow; transports oxygen from lungs to all organs."
            },
            {
                "code": "CBC_RBC",
                "name": "Red Blood Cell Count",
                "level1_meaning": "The total number of oxygen-carrying cells circulating in your blood.",
                "level2_clinical": "Erythrocyte abundance reflects bone marrow output regulated by renal erythropoietin in response to ambient tissue oxygenation.",
                "multi_organ_note": "Produced in marrow, triggered by kidney oxygen sensors."
            }
        ],
        "lifestyle": {
            "nutrition": "Support respiratory tissue with Vitamin C-rich foods: citrus fruits, amla, bell peppers, tomatoes, and adequate hydration.",
            "alcohol": "Excess alcohol intake dampens mucosal defense mechanisms in the upper airways. Moderation supports clear respiratory cilia function."
        }
    },
    "stomach": {
        "organ_id": "stomach",
        "display_name": "Stomach",
        "medical_name": "Gaster",
        "system": "Digestive system",
        "system_id": "digestive",
        "level1_role": "Your Main Food Breakdown Chamber: Churns meals with digestive acid and prepares nutrients for absorption.",
        "level2_medical": "Muscular reservoir between the esophagus and duodenum. Gastric parietal cells secrete hydrochloric acid (HCl) and intrinsic factor, which is required for Vitamin B12 absorption in the ileum.",
        "camera_pos": [0.06, 0.35, 0.50],
        "camera_target": [0.04, 0.33, 0.04],
        "anchor_world": [0.04, 0.33, 0.04],
        "color_hex": 0xfb923c,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["stomach", "mucosa of stomach"],
        "system_source": "digestive",
        "tests": [
            {
                "code": "VIT_B12",
                "name": "Vitamin B12",
                "level1_meaning": "An essential vitamin that requires stomach acid and intrinsic factor for absorption.",
                "level2_clinical": "Gastric intrinsic factor binds cobalamin, allowing receptor-mediated uptake in the terminal ileum. Normal levels confirm functional gastric mucosal absorption.",
                "multi_organ_note": "Requires stomach intrinsic factor for binding; absorbed in small intestine; stored in liver."
            }
        ],
        "lifestyle": {
            "nutrition": "Incorporate fermented foods (homemade curd, buttermilk), avoid skipping meals, and minimize excessively greasy, late-night foods.",
            "alcohol": "Alcohol directly stimulates gastric acid secretion and can irritate the delicate protective mucus lining of the stomach if consumed on an empty stomach."
        }
    },
    "pancreas": {
        "organ_id": "pancreas",
        "display_name": "Pancreas",
        "medical_name": "Pancreas",
        "system": "Digestive & Endocrine system",
        "system_id": "digestive",
        "level1_role": "Your Blood Sugar & Enzyme Factory: Produces insulin to balance blood glucose, plus enzymes to digest food.",
        "level2_medical": "Dual endocrine and exocrine organ. Acinar cells produce digestive enzymes (amylase, lipase, trypsinogen) delivered into the duodenum; Islets of Langerhans beta cells secrete insulin to regulate systemic glucose uptake.",
        "camera_pos": [0.01, 0.30, 0.45],
        "camera_target": [0.01, 0.28, 0.02],
        "anchor_world": [0.01, 0.28, 0.02],
        "color_hex": 0xf59e0b,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["pancreas", "pancreatic duct", "accessory pancreatic duct"],
        "system_source": "digestive",
        "tests": [
            {
                "code": "GLU_FAST",
                "name": "Fasting Blood Glucose",
                "level1_meaning": "The amount of sugar circulating in your bloodstream after an overnight fast.",
                "level2_clinical": "Reflects baseline basal glycemic control governed by pancreatic insulin secretion and hepatic gluconeogenesis balance.",
                "multi_organ_note": "Regulated by pancreatic insulin, balanced by liver glucose output."
            },
            {
                "code": "GLU_HBA1C",
                "name": "HbA1c (Glycated Hemoglobin)",
                "level1_meaning": "A 3-month average of blood sugar levels bound to red blood cells.",
                "level2_clinical": "Percentage of hemoglobin bound to glucose over red blood cell lifespan (90-120 days). Reflects chronic glycemic stability.",
                "multi_organ_note": "A red blood cell protein measurement that reflects pancreatic endocrine performance."
            }
        ],
        "lifestyle": {
            "nutrition": "Favor complex carbohydrates with high fiber: whole wheat roti, oats, fenugreek (methi) seeds, chickpeas, and fresh green vegetables.",
            "alcohol": "Heavy alcohol consumption can cause premature activation of digestive enzymes inside pancreatic ducts. Moderation preserves pancreatic duct health."
        }
    },
    "spleen": {
        "organ_id": "spleen",
        "display_name": "Spleen",
        "medical_name": "Splen / Lien",
        "system": "Immune & Lymphatic system",
        "system_id": "spleen",
        "level1_role": "Your Blood Filter & Immune Watchtower: Recycles old red blood cells, stores platelets, and helps fight blood-borne infections.",
        "level2_medical": "Largest secondary lymphoid organ in the human body, situated in the left hypochondrium. Red pulp sinusoids filter senescent erythrocytes and pool platelets; white pulp lymphoid follicles coordinate B-cell antibody responses against encapsulated pathogens.",
        "camera_pos": [0.12, 0.35, -0.38],
        "camera_target": [0.08, 0.33, -0.11],
        "anchor_world": [0.08, 0.33, -0.11],
        "color_hex": 0xa855f7,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["spleen", "vh_f_spleen"],
        "system_source": "spleen",
        "tests": [
            {
                "code": "CBC_PLT",
                "name": "Platelet Count",
                "level1_meaning": "Small disc-shaped cell fragments in your blood that help form clots and stop bleeding.",
                "level2_clinical": "Megakaryocyte-derived fragments essential for primary hemostasis. Approximately one-third of the body's circulating platelets are dynamically pooled within the splenic red pulp.",
                "multi_organ_note": "Synthesized in bone marrow; dynamically pooled and filtered by the spleen."
            },
            {
                "code": "CBC_WBC",
                "name": "White Blood Cell Count",
                "level1_meaning": "Total circulating immune cells that defend your body against infections.",
                "level2_clinical": "White blood cells circulate between lymphoid organs, the spleen, and peripheral tissues to mount innate and adaptive immune defenses.",
                "multi_organ_note": "Coordinated between bone marrow, lymph nodes, and the spleen."
            }
        ],
        "lifestyle": {
            "nutrition": "Support immune tissue with zinc and antioxidant-rich foods: pumpkin seeds, sesame seeds, spinach, and whole legumes.",
            "alcohol": "Chronic high alcohol exposure can increase portal venous pressure, affecting splenic vascular dynamics."
        }
    },
    "small_intestine": {
        "organ_id": "small_intestine",
        "display_name": "Small Intestine",
        "medical_name": "Intestinum Tenue",
        "system": "Digestive system",
        "system_id": "digestive",
        "level1_role": "Your Nutrient Absorption Highway: Absorbs vitamins, minerals, amino acids, and healthy fats from food into your bloodstream.",
        "level2_medical": "Long tubular segment comprising duodenum, jejunum, and ileum. Microvilli on mucosal enterocytes expand surface area to ~30 square meters, facilitating active enzymatic hydrolysis and carrier-mediated nutrient transport into the portal vein.",
        "camera_pos": [0.00, 0.22, 0.50],
        "camera_target": [0.00, 0.20, 0.02],
        "anchor_world": [0.00, 0.20, 0.02],
        "color_hex": 0xf43f5e,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["duodenum", "jejunum", "ileum"],
        "system_source": "digestive",
        "tests": [
            {
                "code": "IRO_FE",
                "name": "Serum Iron",
                "level1_meaning": "Essential mineral absorbed across the small intestine to build red blood cells.",
                "level2_clinical": "Dietary iron is absorbed primarily by duodenal enterocytes via divalent metal transporter 1 (DMT1) and exported into plasma via ferroportin.",
                "multi_organ_note": "Absorbed in duodenum, transported in blood by transferrin, stored in liver and marrow."
            },
            {
                "code": "IRO_FERR",
                "name": "Ferritin",
                "level1_meaning": "Your body's master cellular storage bank for iron.",
                "level2_clinical": "Intracellular hollow protein shell storing up to 4,500 iron atoms. Reflects total body iron stores when not confounded by acute systemic inflammation.",
                "multi_organ_note": "Absorbed via gut; stored in liver and reticuloendothelial macrophages."
            }
        ],
        "lifestyle": {
            "nutrition": "Pair plant-based iron sources (spinach, lentils) with Vitamin C (lemon juice, amla) to enhance intestinal iron absorption.",
            "alcohol": "Excess alcohol can temporarily loosen tight junction proteins between intestinal enterocytes, increasing gut permeability."
        }
    },
    "large_intestine": {
        "organ_id": "large_intestine",
        "display_name": "Large Intestine",
        "medical_name": "Intestinum Crassum",
        "system": "Digestive system",
        "system_id": "digestive",
        "level1_role": "Your Water Recycling & Gut Microbiome Center: Reabsorbs water and minerals, houses friendly gut bacteria, and forms waste.",
        "level2_medical": "The colon (cecum, ascending, transverse, descending, and sigmoid colon) reabsorbs water and electrolytes (Na, Cl) while trillions of anaerobic commensal bacteria ferment non-digestible fiber into beneficial short-chain fatty acids (acetate, propionate, butyrate).",
        "camera_pos": [-0.05, 0.15, 0.58],
        "camera_target": [-0.04, 0.13, 0.00],
        "anchor_world": [-0.04, 0.13, 0.00],
        "color_hex": 0xec4899,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["colon", "caecum", "cecum", "rectum", "appendix", "taenia"],
        "system_source": "digestive",
        "tests": [
            {
                "code": "INF_CRP",
                "name": "Inflammatory Markers (CRP)",
                "level1_meaning": "A protein measured in the blood that rises during body inflammation.",
                "level2_clinical": "C-Reactive Protein rises in systemic inflammatory states, helping distinguish inflammatory digestive conditions from functional symptoms.",
                "multi_organ_note": "Synthesized in liver in response to IL-6 released from gut or vascular tissues."
            }
        ],
        "lifestyle": {
            "nutrition": "Feed beneficial gut flora with diverse dietary fiber: whole grains, oats, bananas, onions, garlic, and fermented curd (dahi).",
            "alcohol": "Frequent alcohol consumption can alter gut microbiome diversity and cause transient digestive bloating."
        }
    },
    "thyroid": {
        "organ_id": "thyroid",
        "display_name": "Thyroid",
        "medical_name": "Glandula Thyroidea",
        "system": "Endocrine system",
        "system_id": "endocrine",
        "level1_role": "Your Metabolism Thermostat: Butterfly-shaped gland in your neck controlling your body's energy use, heart rate, and temperature.",
        "level2_medical": "Endocrine gland positioned anterior to the trachea beneath the cricoid cartilage. Follicular cells produce thyroxine (T4) and triiodothyronine (T3) regulated by pituitary thyroid-stimulating hormone (TSH) in a negative feedback loop.",
        "camera_pos": [0.00, 0.62, 0.35],
        "camera_target": [0.00, 0.60, 0.03],
        "anchor_world": [0.00, 0.60, 0.03],
        "color_hex": 0xeab308,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["thyroid gland"],
        "system_source": "endocrine",
        "tests": [
            {
                "code": "THY_TSH",
                "name": "TSH (Thyroid-Stimulating Hormone)",
                "level1_meaning": "A messenger hormone from the brain that directs the thyroid on how much energy hormone to produce.",
                "level2_clinical": "Thyroid-Stimulating Hormone is secreted by anterior pituitary thyrotropes in sensitive inverse response to circulating free thyroid hormones.",
                "multi_organ_note": "Produced by pituitary gland in the brain; acts directly on follicular cells in the thyroid gland."
            },
            {
                "code": "THY_FT4",
                "name": "Free T4 (Free Thyroxine)",
                "level1_meaning": "The main hormone released by your thyroid into your bloodstream.",
                "level2_clinical": "Unbound circulating thyroxine available for cellular uptake and peripheral deiodination into active T3.",
                "multi_organ_note": "Produced in thyroid; converted to active T3 in liver and peripheral tissues."
            }
        ],
        "lifestyle": {
            "nutrition": "Ensure adequate dietary iodine from iodized table salt, dairy, and trace minerals from pumpkin seeds and sunflower seeds.",
            "alcohol": "Excess alcohol can transiently alter pituitary-thyroid axis signaling, causing temporary morning fatigue."
        }
    },
    "urinary_bladder": {
        "organ_id": "urinary_bladder",
        "display_name": "Urinary Bladder",
        "medical_name": "Vesica Urinaria",
        "system": "Renal & Urinary system",
        "system_id": "renal",
        "level1_role": "Your Urine Storage Reservoir: Flexible muscular balloon in the pelvis holding urine until you are ready to release it.",
        "level2_medical": "Pelvic reservoir lined with distensible transitional urothelium. Smooth detrusor muscle walls contract synchronously under parasympathetic control during micturition while ureteral orifices prevent vesicoureteral reflux.",
        "camera_pos": [0.00, 0.05, 0.45],
        "camera_target": [0.00, 0.02, 0.02],
        "anchor_world": [0.00, 0.02, 0.02],
        "color_hex": 0xec4899,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["urinary bladder", "urethra"],
        "system_source": "renal",
        "tests": [
            {
                "code": "URI_ROUT",
                "name": "Urinalysis / Urine Routine",
                "level1_meaning": "Comprehensive screening check for urine clarity, acidity, protein, glucose, and microscopic cells.",
                "level2_clinical": "Evaluates specific gravity, urinary pH, leukocyte esterase, nitrites, and microscopic sediment for indications of hydration or microbial presence.",
                "multi_organ_note": "Reflects both renal filtration and downstream bladder urothelial health."
            }
        ],
        "lifestyle": {
            "nutrition": "Drink ample water throughout the day to keep urine clear or pale straw-colored, flushing urinary pathways naturally.",
            "alcohol": "Alcohol is a bladder irritant and diuretic that accelerates bladder filling while causing systemic dehydration."
        }
    },
    "brain": {
        "organ_id": "brain",
        "display_name": "Brain",
        "medical_name": "Encephalon",
        "system": "Nervous system",
        "system_id": "nervous",
        "level1_role": "Your Master Control Center: Coordinates thinking, memory, emotion, movement, balance, and automatic bodily rhythms.",
        "level2_medical": "Central nervous organ consisting of cerebral hemispheres, basal ganglia, brainstem, and cerebellum. Glial networks, neurotransmitters, and complex neural circuits regulate motor coordination, cognitive processing, and neuroendocrine homeostasis.",
        "camera_pos": [0.00, 0.80, 0.40],
        "camera_target": [0.00, 0.77, -0.01],
        "anchor_world": [0.00, 0.77, -0.01],
        "color_hex": 0x8b5cf6,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["cerebr", "brain", "cortex", "gyrus", "thalamus", "ventricle", "pons", "medulla oblongata", "cerebell", "midbrain", "insula"],
        "system_source": "nervous",
        "tests": [
            {
                "code": "VIT_B12",
                "name": "Vitamin B12",
                "level1_meaning": "Protects nerve insulation (myelin) and supports clear thinking and memory.",
                "level2_clinical": "Essential enzymatic cofactor in methionine synthesis and myelin sheath maintenance. Protects against peripheral neuropathy and subacute combined degeneration.",
                "multi_organ_note": "Absorbed in small intestine; protects central and peripheral nervous myelin."
            },
            {
                "code": "VIT_FOL",
                "name": "Serum Folate",
                "level1_meaning": "Essential B-vitamin supporting cellular DNA repair and healthy nerve communication.",
                "level2_clinical": "Cofactor in single-carbon transfer pathways necessary for purine synthesis and homocysteine remethylation in central neurons.",
                "multi_organ_note": "Works in tandem with B12 in neuronal methylation."
            },
            {
                "code": "ELE_NA",
                "name": "Serum Sodium",
                "level1_meaning": "Key mineral salt that drives nerve electrical signals and brain water balance.",
                "level2_clinical": "Principal extracellular cation maintaining serum osmolality and driving action potentials across neuronal axonal membranes.",
                "multi_organ_note": "Regulated by kidneys; essential for central nervous electrical conduction."
            }
        ],
        "lifestyle": {
            "nutrition": "Nourish brain tissue with walnuts (omega-3 fatty acids), spinach, seeds, whole grains, and antioxidant-rich berries.",
            "alcohol": "Alcohol binds GABA receptors and suppresses glutamate signaling, slowing reaction times and blunting memory consolidation."
        }
    },
    "spine": {
        "organ_id": "spine",
        "display_name": "Spine & Bones",
        "medical_name": "Columna Vertebralis",
        "system": "Skeletal system",
        "system_id": "skeletal",
        "level1_role": "Your Body's Strong Framework: Protects your spinal cord, supports posture, and stores vital calcium minerals.",
        "level2_medical": "Articulated column consisting of 33 vertebrae (cervical, thoracic, lumbar, sacral, coccygeal) separated by fibrocartilaginous intervertebral discs, providing axial support and protecting the central spinal cord.",
        "camera_pos": [0.00, 0.45, -0.65],
        "camera_target": [0.00, 0.44, -0.04],
        "anchor_world": [0.00, 0.44, -0.04],
        "color_hex": 0xf8fafc,
        "validation_status": "VERIFIED_ANATOMICAL_MESH",
        "mesh_keywords": ["vertebra", "intervertebral", "sacrum", "coccyx", "atlas (c1)", "axis (c2)"],
        "system_source": "skeletal",
        "tests": [
            {
                "code": "VIT_D",
                "name": "25-OH Vitamin D",
                "level1_meaning": "The essential sunshine vitamin that helps your bones absorb calcium from food.",
                "level2_clinical": "25-Hydroxyvitamin D is the primary circulating form reflecting total body stores. It enables intestinal calcium absorption and maintains bone mineral density.",
                "multi_organ_note": "Synthesized in skin, activated in liver and kidneys; strengthens skeletal bones."
            },
            {
                "code": "MIN_CAL",
                "name": "Serum Calcium",
                "level1_meaning": "The primary building-block mineral for strong bones and teeth.",
                "level2_clinical": "Over 99% of body calcium is stored in bone hydroxyapatite. Serum levels are tightly regulated by parathyroid hormone and Vitamin D.",
                "multi_organ_note": "Stored in skeleton; regulated by parathyroid and kidneys."
            }
        ],
        "lifestyle": {
            "nutrition": "Strengthen bone structure with sesame seeds (til), ragi (finger millet), dairy or fortified plant milk, and safe morning sunlight exposure.",
            "alcohol": "Chronic heavy alcohol consumption reduces osteoblast bone-building activity and impairs Vitamin D metabolic activation."
        }
    }
}


ORGAN_ALIASES = {
    "liver": "liver",
    "hepar": "liver",
    "heart": "heart",
    "cor": "heart",
    "left kidney": "left_kidney",
    "left_kidney": "left_kidney",
    "right kidney": "right_kidney",
    "right_kidney": "right_kidney",
    "kidneys": "kidneys",
    "renes": "kidneys",
    "kidney": "kidneys",
    "lungs": "lungs",
    "pulmones": "lungs",
    "lung": "lungs",
    "stomach": "stomach",
    "gaster": "stomach",
    "pancreas": "pancreas",
    "spleen": "spleen",
    "splen": "spleen",
    "lien": "spleen",
    "small intestine": "small_intestine",
    "small_intestine": "small_intestine",
    "large intestine": "large_intestine",
    "large_intestine": "large_intestine",
    "intestines": "large_intestine",
    "colon": "large_intestine",
    "thyroid": "thyroid",
    "glandula thyroidea": "thyroid",
    "urinary bladder": "urinary_bladder",
    "urinary_bladder": "urinary_bladder",
    "bladder": "urinary_bladder",
    "brain": "brain",
    "encephalon": "brain",
    "spine": "spine",
    "spine & bones": "spine",
    "bones": "spine",
    "columna vertebralis": "spine",
}


def resolve_canonical_organ(query: str) -> Optional[str]:
    """Resolve an organ query, Latin name, or alias to a canonical organ ID."""
    if not query:
        return None
    q = query.strip().lower()
    if q in ORGAN_ALIASES:
        return ORGAN_ALIASES[q]
    norm_q = q.replace(" ", "_")
    if norm_q in ORGAN_REGISTRY:
        return norm_q
    for alias, canonical in ORGAN_ALIASES.items():
        if alias in q or q in alias:
            return canonical
    return None


def get_organ_by_id(organ_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve verified organ metadata by canonical ID (case-insensitive) or alias."""
    canonical = resolve_canonical_organ(organ_id)
    if canonical:
        return ORGAN_REGISTRY.get(canonical)
    return ORGAN_REGISTRY.get(organ_id.lower().replace(" ", "_"))


get_organ = get_organ_by_id


def get_all_organs() -> List[Dict[str, Any]]:
    """Return all verified anatomical organ definitions."""
    return list(ORGAN_REGISTRY.values())


def find_organ_for_test(analyte_code_or_name: str) -> Optional[Dict[str, Any]]:
    """Find the primary organ associated with a lab test code or name."""
    query = analyte_code_or_name.upper().strip()
    for organ in ORGAN_REGISTRY.values():
        for test in organ.get("tests", []):
            if test["code"].upper() == query or query in test["name"].upper():
                return organ
    return None
