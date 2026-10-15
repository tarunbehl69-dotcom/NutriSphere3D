/**
 * NutriSphere X — The Body Atlas 3D Visualization Engine
 * 
 * Signature Experiences:
 * - "Your Body is the Interface": Real anatomical 3D models serving as primary medical navigation
 * - "The Organ Reveal": Cinematic camera tweening, selective organ isolation, high-contrast shaders
 * - "BioSignals": Spatial 3D-to-2D anchor projection & dynamic SVG connector curves to verified biomarker cards
 * - "My Health Story": Guided 6-scene clinical story mode through patient findings
 * - High-Contrast Clinical Theater Mode (0x0a0f1d) & Light Studio Switcher
 * - 3D HUD Tooltip with Latin TA2 terminology, systems, and mapped analytes
 * - Real glTF 2.0 / GLB assemblies with Draco decompression (NIH & BodyParts3D CC BY 4.0)
 */

class AnatomyExplorer {
  constructor(containerId = 'canvas-3d-container', options = {}) {
    this.container = document.getElementById(containerId);
    this.options = Object.assign({
      enableOrbitControls: true,
      autoRotate: false,
      onOrganSelected: null,
      mode: 'full', // 'full' (atlas), 'compact' (hero), 'results'
      defaultTheme: 'dark', // 'dark' (clinical theater) or 'light'
      reportId: 'rep_demo_2026_001'
    }, options);

    this.systems = {};
    this.organs = {};
    this.meshToOrganName = new Map();
    this.activeOrgan = null;
    this.hoveredOrgan = null;
    this.isIsolated = false;
    this.bodyShellVisible = true;
    this.bodyShellOpacity = 0.45;
    this.activeSystemFilter = 'all';
    this.currentTheme = this.options.defaultTheme || 'dark';
    this.currentVisualMode = 'standard'; // 'standard', 'xray', 'ghost'
    this.explodeFactor = 0.0; // 0.0 to 1.0
    this.reportId = this.options.reportId || 'rep_demo_2026_001';

    // Health Story Mode State
    this.storyModeActive = false;
    this.storyStepIndex = 0;
    this.storyTimer = null;
    this.storyIsPaused = false;

    // Verified Biomarker Data Store (Rohan Sharma 2026 Encounter)
    this.verifiedBiomarkers = {
      'Liver': [
        { name: 'ALT (SGPT)', val: 58, unit: 'U/L', ref: '10 - 49', flag: 'high', label: 'Mildly High', conf: 'Verified 98%', page: 'Page 1', note: 'Indicates hepatocellular membrane permeability; common in metabolic stress, medication clearance, or alcohol intake.' },
        { name: 'AST (SGOT)', val: 46, unit: 'U/L', ref: '10 - 34', flag: 'high', label: 'Mildly High', conf: 'Verified 97%', page: 'Page 1', note: 'Mitochondrial and cytoplasmic enzyme found in hepatocytes and cardiac myocytes; de Ritis ratio AST/ALT = 0.79.' },
        { name: 'Bilirubin Total', val: 0.9, unit: 'mg/dL', ref: '0.2 - 1.2', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 1', note: 'Breakdown byproduct of heme catabolism; reflects normal biliary excretory capacity.' },
        { name: 'Alkaline Phosphatase (ALP)', val: 82, unit: 'U/L', ref: '44 - 147', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 1', note: 'Normal biliary ductal and bone alkaline phosphatase activity.' },
        { name: 'Albumin', val: 4.4, unit: 'g/dL', ref: '3.5 - 5.0', flag: 'normal', label: 'Normal', conf: 'Verified 98%', page: 'Page 1', note: 'Primary hepatic plasma oncotic protein; indicates intact hepatic protein synthetic capacity.' }
      ],
      'Heart': [
        { name: 'Total Cholesterol', val: 218, unit: 'mg/dL', ref: '< 200', flag: 'high', label: 'Borderline High', conf: 'Verified 99%', page: 'Page 2', note: 'Cumulative circulating sterol mass; evaluate alongside non-HDL and ApoB particle count.' },
        { name: 'LDL Cholesterol', val: 142, unit: 'mg/dL', ref: '< 100', flag: 'high', label: 'Elevated', conf: 'Verified 98%', page: 'Page 2', note: 'Primary atherogenic circulating lipoprotein; dietary saturated fat reduction and soluble fiber recommended.' },
        { name: 'HDL Cholesterol', val: 48, unit: 'mg/dL', ref: '> 40', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 2', note: 'Reverse cholesterol transport lipoprotein; optimal range protective against atheroma formation.' },
        { name: 'Triglycerides', val: 165, unit: 'mg/dL', ref: '< 150', flag: 'high', label: 'Borderline High', conf: 'Verified 98%', page: 'Page 2', note: 'Neutral storage lipids; responsive to dietary simple sugars, refined carbs, and alcohol.' },
        { name: 'Apolipoprotein B (ApoB)', val: 104, unit: 'mg/dL', ref: '< 90', flag: 'high', label: 'Elevated', conf: 'Verified 96%', page: 'Page 2', note: 'Total count of atherogenic particles (LDL, VLDL, IDL); superior risk predictor to LDL-C alone.' },
        { name: 'hs-CRP (Cardiac)', val: 1.8, unit: 'mg/L', ref: '< 2.0', flag: 'normal', label: 'Average Risk', conf: 'Verified 95%', page: 'Page 2', note: 'Systemic vascular inflammation marker; within standard moderate physiological tolerance.' }
      ],
      'Kidneys': [
        { name: 'Serum Creatinine', val: 1.05, unit: 'mg/dL', ref: '0.70 - 1.30', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 1', note: 'Endogenous muscle breakdown product filtered by renal glomeruli.' },
        { name: 'eGFR (CKD-EPI)', val: 88, unit: 'mL/min/1.73m²', ref: '> 90', flag: 'high', label: 'Borderline Normal', conf: 'Verified 99%', page: 'Page 1', note: 'Estimated glomerular filtration rate; sensitive to hydration state, protein intake, and age.' },
        { name: 'Blood Urea Nitrogen (BUN)', val: 16, unit: 'mg/dL', ref: '7 - 20', flag: 'normal', label: 'Normal', conf: 'Verified 98%', page: 'Page 1', note: 'Nitrogenous waste product from hepatic urea cycle; BUN/Creatinine ratio = 15.2 (optimal).' },
        { name: 'Serum Uric Acid', val: 6.2, unit: 'mg/dL', ref: '3.5 - 7.2', flag: 'normal', label: 'Normal', conf: 'Verified 97%', page: 'Page 1', note: 'Purine metabolite; normal excretion balance maintained by proximal renal tubules.' }
      ],
      'Pancreas': [
        { name: 'Fasting Blood Glucose', val: 104, unit: 'mg/dL', ref: '70 - 99', flag: 'high', label: 'Impaired Fasting', conf: 'Verified 99%', page: 'Page 2', note: 'Slightly elevated morning glucose indicating early peripheral insulin resistance (pre-diabetes range).' },
        { name: 'HbA1c (Glycated Hb)', val: 5.8, unit: '%', ref: '4.0 - 5.6', flag: 'high', label: 'Pre-Diabetes', conf: 'Verified 99%', page: 'Page 2', note: 'Reflects 90-day mean erythrocyte glycation; lifestyle glycemic control recommended.' },
        { name: 'Fasting Serum Insulin', val: 11.2, unit: 'uIU/mL', ref: '2.6 - 24.9', flag: 'normal', label: 'Normal', conf: 'Verified 95%', page: 'Page 2', note: 'Endocrine beta-cell hormone regulating cellular glucose uptake and lipogenesis.' }
      ],
      'Lungs': [
        { name: 'Hemoglobin', val: 14.8, unit: 'g/dL', ref: '13.8 - 17.2', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 1', note: 'Tetrameric oxygen-transport metalloprotein inside circulating erythrocytes.' },
        { name: 'Hematocrit (PCV)', val: 44.2, unit: '%', ref: '40.7 - 50.3', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 1', note: 'Volume percentage of whole blood composed of packed red blood cells.' },
        { name: 'RBC Count', val: 4.95, unit: 'M/uL', ref: '4.5 - 5.9', flag: 'normal', label: 'Normal', conf: 'Verified 98%', page: 'Page 1', note: 'Total erythrocyte mass ensuring adequate microvascular alveolar gas exchange.' }
      ],
      'Stomach': [
        { name: 'Vitamin B12 (Cobalamin)', val: 340, unit: 'pg/mL', ref: '211 - 911', flag: 'normal', label: 'Normal', conf: 'Verified 96%', page: 'Page 3', note: 'Requires gastric parietal cell intrinsic factor for distal ileal absorption.' },
        { name: 'Serum Gastrin', val: 48, unit: 'pg/mL', ref: '< 100', flag: 'normal', label: 'Normal', conf: 'Verified 94%', page: 'Page 3', note: 'G-cell peptide hormone regulating gastric hydrochloric acid secretion.' }
      ],
      'Intestines': [
        { name: 'Serum Ferritin', val: 180, unit: 'ng/mL', ref: '30 - 400', flag: 'normal', label: 'Normal', conf: 'Verified 98%', page: 'Page 3', note: 'Intracellular iron storage protein reflecting systemic iron stores and reticuloendothelial reserve.' },
        { name: 'Serum Iron', val: 95, unit: 'ug/dL', ref: '65 - 175', flag: 'normal', label: 'Normal', conf: 'Verified 97%', page: 'Page 3', note: 'Circulating transferrin-bound iron available for active erythropoiesis.' }
      ],
      'Spine': [
        { name: 'Serum Calcium', val: 9.6, unit: 'mg/dL', ref: '8.5 - 10.2', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 2', note: 'Ionized and protein-bound extracellular calcium regulating neuromuscular tone and bone mineralization.' },
        { name: '25-OH Vitamin D Total', val: 22.4, unit: 'ng/mL', ref: '30.0 - 100.0', flag: 'urgent', label: 'Insufficiency', conf: 'Verified 98%', page: 'Page 2', note: 'Circulating pre-hormone; values below 30 ng/mL impair intestinal calcium transport and bone density.' },
        { name: 'Alkaline Phosphatase (Bone)', val: 78, unit: 'U/L', ref: '44 - 147', flag: 'normal', label: 'Normal', conf: 'Verified 97%', page: 'Page 2', note: 'Osteoblast-derived isoenzyme indicating physiological bone remodeling turnover.' }
      ],
      'Thyroid': [
        { name: 'TSH (Thyrotropin)', val: 2.35, unit: 'uIU/mL', ref: '0.40 - 4.50', flag: 'normal', label: 'Normal', conf: 'Verified 99%', page: 'Page 2', note: 'Pituitary feedback hormone governing thyroid follicle T4 and T3 hormone synthesis.' },
        { name: 'Free T4 (Thyroxine)', val: 1.25, unit: 'ng/dL', ref: '0.82 - 1.77', flag: 'normal', label: 'Normal', conf: 'Verified 98%', page: 'Page 2', note: 'Unbound circulating thyroxine regulating peripheral cellular basal metabolic rate.' }
      ],
      'Brain': [
        { name: 'Serum Folate', val: 12.8, unit: 'ng/mL', ref: '> 4.0', flag: 'normal', label: 'Normal', conf: 'Verified 97%', page: 'Page 3', note: 'Essential methyl-donor cofactor for neuronal DNA synthesis and myelin sheath maintenance.' },
        { name: 'Homocysteine', val: 9.8, unit: 'umol/L', ref: '< 15.0', flag: 'normal', label: 'Normal', conf: 'Verified 95%', page: 'Page 3', note: 'Sulfur-containing amino acid intermediary; normal level indicates intact transsulfuration pathway.' }
      ]
    };

    // Standard clinical camera focus targets & easy plain-English medical metadata
    this.organCatalog = {
      'Liver': {
        name: 'Liver',
        easyRole: "Your Body's Master Filter & Energy Center",
        latin: 'Hepar',
        system: 'digestive',
        cameraPos: [-0.05, 0.38, 0.55],
        cameraTarget: [-0.03, 0.35, 0.04],
        anchorWorld: [-0.03, 0.35, 0.04],
        color: 0xf97316, // Vivid Hepatic Terracotta / Amber
        tests: ['ALT', 'AST', 'ALP', 'GGT', 'Bilirubin Total', 'Albumin', 'Total Protein'],
        role: 'Cleans toxins and chemicals from your blood, turns food into usable energy, produces bile to digest fats, and stores glycogen.',
        clinicalNote: 'Elevated liver enzymes (ALT 58 U/L, AST 46 U/L) mean liver cells are working under extra stress. This is often temporary and can be improved with nutritious foods, lower alcohol, and rest.',
        alcoholImpact: 'Over 90% of alcohol is processed here. Drinking too much overworks liver cells, leading to temporary cell stress and fat buildup.',
        nutritionAdvice: 'Eat antioxidant-rich Indian foods: amla (Indian gooseberry), turmeric, cruciferous vegetables, garlic, and lentils (dal).'
      },
      'Heart': {
        name: 'Heart',
        easyRole: "Your Body's Life Pump",
        latin: 'Cor',
        system: 'cardiovascular',
        cameraPos: [0.05, 0.45, 0.50],
        cameraTarget: [0.04, 0.43, 0.03],
        anchorWorld: [0.04, 0.43, 0.03],
        color: 0xef4444, // Bright Arterial Crimson
        tests: ['Total Cholesterol', 'LDL Cholesterol', 'HDL Cholesterol', 'Triglycerides', 'ApoB', 'Troponin I', 'hs-CRP'],
        role: 'Beats about 100,000 times a day to pump fresh oxygen and nutrients through your blood vessels to every part of your body.',
        clinicalNote: 'LDL ("bad") cholesterol at 142 mg/dL and ApoB at 104 mg/dL mean there are more circulating cholesterol particles than ideal. Eating more soluble fiber and heart-healthy fats helps lower them.',
        alcoholImpact: 'Heavy drinking raises blood pressure and can cause irregular heartbeats. Cutting back helps blood vessels relax.',
        nutritionAdvice: 'Choose heart-healthy foods: oats (rich in beta-glucan fiber), walnuts, chia seeds, flaxseeds, and low-sodium home-cooked meals.'
      },
      'Kidneys': {
        name: 'Kidneys',
        easyRole: 'Your Natural Water & Salt Filters',
        latin: 'Renes',
        system: 'renal',
        cameraPos: [0.00, 0.28, -0.55], // Posterior retroperitoneal view
        cameraTarget: [0.00, 0.26, -0.01],
        anchorWorld: [0.00, 0.26, -0.01],
        color: 0xe11d48, // Vivid Renal Ruby
        tests: ['Serum Creatinine', 'eGFR', 'Blood Urea Nitrogen (BUN)', 'Uric Acid', 'Urine Microalbumin', 'Electrolytes (Na, K)'],
        role: 'Filter about 200 quarts of fluid daily, balancing water and essential salts while removing waste through urine.',
        clinicalNote: 'Your filtration rate (eGFR 88 mL/min) and creatinine (1.05 mg/dL) show good, stable kidney filtration. Staying well-hydrated helps your kidneys work effortlessly.',
        alcoholImpact: 'Alcohol acts as a diuretic, making your body lose fluids and leading to dehydration and temporary electrolyte shifts.',
        nutritionAdvice: 'Drink plenty of water, avoid excess salt in snacks and processed food, and enjoy fresh fruits like apples, berries, and watermelon.'
      },
      'Lungs': {
        name: 'Lungs',
        easyRole: 'Your Oxygen Exchange Center',
        latin: 'Pulmones',
        system: 'respiratory',
        cameraPos: [0.00, 0.48, 0.65],
        cameraTarget: [0.01, 0.46, -0.01],
        anchorWorld: [0.01, 0.46, -0.01],
        color: 0x0ea5e9, // Vivid Pulmonary Azure
        tests: ['Hemoglobin', 'Hematocrit', 'RBC Count', 'Arterial Blood Gas', 'Oxygen Saturation'],
        role: 'Take in fresh oxygen when you breathe in and release carbon dioxide when you breathe out, keeping your blood oxygenated.',
        clinicalNote: 'Hemoglobin at 14.8 g/dL and red blood cells are at healthy levels, confirming that your blood carries oxygen efficiently to all organs.',
        alcoholImpact: 'Excess alcohol can weaken the lungs\' natural defense against respiratory bugs and irritation.',
        nutritionAdvice: 'Support lung tissue with vitamin C-rich foods: citrus fruits, amla, bell peppers, tomatoes, and plenty of water.'
      },
      'Pancreas': {
        name: 'Pancreas',
        easyRole: 'Your Blood Sugar & Enzyme Factory',
        latin: 'Pancreas',
        system: 'digestive',
        cameraPos: [0.01, 0.30, 0.45],
        cameraTarget: [0.01, 0.28, 0.02],
        anchorWorld: [0.01, 0.28, 0.02],
        color: 0xf59e0b, // Luminous Endocrine Amber
        tests: ['Fasting Blood Glucose', 'HbA1c', 'Serum Insulin', 'C-Peptide', 'Amylase', 'Lipase'],
        role: 'Produces insulin to keep blood sugar balanced, along with digestive juices that break down fats, proteins, and carbohydrates in food.',
        clinicalNote: 'Fasting glucose at 104 mg/dL and HbA1c at 5.8% indicate mild pre-diabetes. Simple lifestyle habits like brisk walks after meals and eating high-fiber whole grains can bring them back to normal.',
        alcoholImpact: 'Heavy alcohol can irritate pancreatic ducts and trigger inflammation. Moderation is key for pancreatic health.',
        nutritionAdvice: 'Emphasize high-fiber foods: whole wheat roti, oats, fenugreek (methi) seeds, chickpeas, and green leafy vegetables.'
      },
      'Stomach': {
        name: 'Stomach',
        easyRole: 'Your Main Food Breakdown Chamber',
        latin: 'Gaster',
        system: 'digestive',
        cameraPos: [0.06, 0.35, 0.50],
        cameraTarget: [0.04, 0.33, 0.04],
        anchorWorld: [0.04, 0.33, 0.04],
        color: 0xfb923c, // Warm Gastric Coral
        tests: ['Vitamin B12', 'Serum Gastrin', 'Pepsinogen I/II', 'Helicobacter pylori Serology'],
        role: 'Uses natural stomach acids and enzymes to churn food, break down protein, and make Vitamin B12 absorbable.',
        clinicalNote: 'Vitamin B12 at 340 pg/mL is normal, ensuring healthy red blood cells and nerve signaling.',
        alcoholImpact: 'Alcohol irritates the stomach lining and increases stomach acid, which can cause heartburn or gastritis if taken on an empty stomach.',
        nutritionAdvice: 'Include fermented curd/yogurt, lentils, fortified foods, and avoid overly greasy late-night meals.'
      },
      'Intestines': {
        name: 'Intestines',
        easyRole: 'Your Nutrient Absorption Highway',
        latin: 'Intestinum',
        system: 'digestive',
        cameraPos: [-0.05, 0.15, 0.58],
        cameraTarget: [-0.06, 0.13, 0.00],
        anchorWorld: [-0.06, 0.13, 0.00],
        color: 0xec4899, // Enteric Rose
        tests: ['Fecal Calprotectin', 'Serum Iron', 'Ferritin', 'Celiac Serology (tTG-IgA)', 'Stool Occult Blood'],
        role: 'Absorbs water, vitamins, minerals, iron, and glucose into the blood while housing trillions of beneficial gut bacteria.',
        clinicalNote: 'Iron and ferritin stores are well within normal ranges, indicating good nutrient absorption from your diet.',
        alcoholImpact: 'Frequent alcohol can loosen gut barriers and cause temporary bloating or digestive discomfort.',
        nutritionAdvice: 'Feed beneficial gut flora with prebiotics and fiber: oats, bananas, garlic, onions, buttermilk, and dal.'
      },
      'Brain': {
        name: 'Brain',
        easyRole: 'Your Master Control Center',
        latin: 'Encephalon',
        system: 'nervous',
        cameraPos: [0.00, 0.80, 0.40],
        cameraTarget: [0.00, 0.77, -0.01],
        anchorWorld: [0.00, 0.77, -0.01],
        color: 0x8b5cf6, // Electric Neuro Violet
        tests: ['Vitamin B12', 'Serum Folate', 'Homocysteine', 'TSH', 'Electrolytes'],
        role: 'Controls thinking, memories, emotions, movements, balance, and automatic bodily functions like breathing.',
        clinicalNote: 'Folate (12.8 ng/mL) and homocysteine (9.8 umol/L) are normal, showing healthy nerve protection and cellular repair.',
        alcoholImpact: 'Alcohol slows brain signaling, blunting reflexes and impairing memory formation and restful sleep.',
        nutritionAdvice: 'Nourish brain cells with walnuts, spinach, seeds, whole grains, and omega-3 rich foods.'
      },
      'Spine': {
        name: 'Spine & Bones',
        easyRole: "Your Body's Strong Bone Framework",
        latin: 'Columna Vertebralis',
        system: 'skeletal',
        cameraPos: [0.00, 0.45, -0.65],
        cameraTarget: [0.00, 0.44, -0.04],
        anchorWorld: [0.00, 0.44, -0.04],
        color: 0xf8fafc, // Bright Bone White
        tests: ['Serum Calcium', '25-OH Vitamin D', 'Alkaline Phosphatase (Bone)', 'Phosphorus', 'Parathyroid Hormone (PTH)'],
        role: 'Provides structural support, protects your spinal cord, allows movement, and stores calcium and minerals.',
        clinicalNote: 'Vitamin D is at 22.4 ng/mL (needs attention; healthy target is 30+ ng/mL). Vitamin D helps your bones absorb calcium. Consider safe sun exposure and speaking to your doctor about a D3 supplement.',
        alcoholImpact: 'Chronic alcohol reduces bone-building cell activity and interferes with vitamin D activation.',
        nutritionAdvice: 'Boost bone strength with sesame seeds (til), ragi (finger millet), curd/milk, and vitamin D3 with K2.'
      },
      'Thyroid': {
        name: 'Thyroid',
        easyRole: 'Your Metabolism Thermostat',
        latin: 'Glandula Thyroidea',
        system: 'endocrine',
        cameraPos: [0.00, 0.62, 0.35],
        cameraTarget: [0.00, 0.60, 0.03],
        anchorWorld: [0.00, 0.60, 0.03],
        color: 0xeab308, // Glowing Endocrine Gold
        tests: ['TSH', 'Free T3', 'Free T4', 'Anti-TPO Antibodies', 'Thyroglobulin'],
        role: 'Releases thyroid hormones that control your body\'s energy levels, calorie burning, and body temperature.',
        clinicalNote: 'TSH at 2.35 uIU/mL is completely normal, showing healthy thyroid function and stable metabolism.',
        alcoholImpact: 'Excess alcohol can temporarily disrupt hormone balance, leading to sluggishness.',
        nutritionAdvice: 'Include trace minerals from iodized salt, pumpkin seeds, sunflower seeds, and whole grains.'
      }
    };

    if (!this.container) return;

    if (!this.checkWebGL()) {
      this.render2DFallback();
      return;
    }

    this.initThreeJS();
    this.checkForUrlParams();
  }

  checkWebGL() {
    try {
      const canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  }

  initThreeJS() {
    if (typeof THREE === 'undefined') {
      console.warn('Three.js not loaded. Falling back to 2D view.');
      this.render2DFallback();
      return;
    }

    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || 640;

    // 1. Scene & High-Contrast Clinical Theater Backdrop
    this.scene = new THREE.Scene();
    this.darkBgColor = new THREE.Color(0x0a0f1d); // Deep Obsidian Theater Mode
    this.lightBgColor = new THREE.Color(0xf8fafc); // Clean Medical Studio
    this.scene.background = this.currentTheme === 'dark' ? this.darkBgColor : this.lightBgColor;

    // 2. Camera Setup (Centered at human torso)
    this.defaultCameraPos = new THREE.Vector3(0, 0.15, 2.2);
    this.defaultCameraTarget = new THREE.Vector3(0, 0.15, 0);

    this.camera = new THREE.PerspectiveCamera(40, width / height, 0.05, 50);
    this.camera.position.copy(this.defaultCameraPos);

    // 3. WebGL Renderer with High-Performance Settings
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputEncoding = THREE.sRGBEncoding || 3001;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);
    this.renderer.domElement.id = 'canvas-3d';

    // Ensure Floating Spatial Elements exist in container
    this.ensureSpatialOverlays();

    // 4. Clinical High-Contrast Lighting Rig
    this.ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    this.scene.add(this.ambientLight);

    this.hemiLight = new THREE.HemisphereLight(0x38bdf8, 0x1e293b, 0.85);
    this.hemiLight.position.set(0, 10, 0);
    this.scene.add(this.hemiLight);

    // Main Key Light
    this.keyLight = new THREE.DirectionalLight(0xffffff, 1.60);
    this.keyLight.position.set(5, 8, 6);
    this.scene.add(this.keyLight);

    // Soft Teal Front Fill Light
    this.fillLight = new THREE.DirectionalLight(0x99f6e4, 0.75);
    this.fillLight.position.set(-6, 2, 4);
    this.scene.add(this.fillLight);

    // High-Contrast Cyan Rim Light (Outlines organ contours against dark theater)
    this.rimLight = new THREE.DirectionalLight(0x38bdf8, 1.45);
    this.rimLight.position.set(0, -4, -6);
    this.scene.add(this.rimLight);

    // 5. Master Anatomy Group (Centered Life-Size Human Assembly)
    // The master anatomical model stands 1.68m tall; centering offset: Y = -0.844m
    this.masterGroup = new THREE.Group();
    this.masterGroup.position.set(0, -0.844, -0.016);
    this.scene.add(this.masterGroup);

    // 6. OrbitControls with smooth damping
    if (this.options.enableOrbitControls && typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.08;
      this.controls.target.copy(this.defaultCameraTarget);
      this.controls.minDistance = 0.3;
      this.controls.maxDistance = 6.0;
      this.controls.maxPolarAngle = Math.PI * 0.92;
      this.controls.minPolarAngle = Math.PI * 0.08;
    }

    // 7. Raycaster for organ picking & hovering
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();

    this.setupEventListeners();
    this.loadAuthenticHumanAnatomy();
    this.animate();

    window.addEventListener('resize', () => this.onWindowResize());
  }

  ensureSpatialOverlays() {
    // 1. HUD Tooltip
    let tooltip = document.getElementById('anatomy-hud-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'anatomy-hud-tooltip';
      tooltip.className = 'hidden';
      this.container.appendChild(tooltip);
    }
    this.hudTooltip = tooltip;

    // 2. SVG Connector Layer for BioSignals
    let svgLayer = document.getElementById('biosignal-svg-layer');
    if (!svgLayer) {
      svgLayer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svgLayer.id = 'biosignal-svg-layer';
      svgLayer.innerHTML = `
        <defs>
          <linearGradient id="connectorGlow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#159A92" stop-opacity="0.8"/>
            <stop offset="100%" stop-color="#79CFCB" stop-opacity="0.9"/>
          </linearGradient>
        </defs>
        <path id="biosignal-connector-path" class="biosignal-connector-line" d="" fill="none"/>
      `;
      this.container.appendChild(svgLayer);
    }
    this.svgLayer = svgLayer;
    this.connectorPath = document.getElementById('biosignal-connector-path');

    // 3. Screen-Space Organ Anchor Marker
    let anchorMarker = document.getElementById('organ-anchor-point');
    if (!anchorMarker) {
      anchorMarker = document.createElement('div');
      anchorMarker.id = 'organ-anchor-point';
      anchorMarker.className = 'organ-anchor-point opacity-0';
      this.container.appendChild(anchorMarker);
    }
    this.anchorMarker = anchorMarker;
  }

  loadAuthenticHumanAnatomy() {
    // Setup DRACOLoader for decompressed glTF binary assets
    let dracoLoader = null;
    if (typeof THREE.DRACOLoader !== 'undefined') {
      dracoLoader = new THREE.DRACOLoader();
      dracoLoader.setDecoderPath('/draco/gltf/');
    }

    const loader = (typeof THREE.GLTFLoader !== 'undefined') ? new THREE.GLTFLoader() : null;
    if (!loader) {
      console.warn('GLTFLoader not available. Rendering 2D fallback.');
      this.render2DFallback();
      return;
    }

    if (dracoLoader) {
      loader.setDRACOLoader(dracoLoader);
    }

    // High-Contrast Master System Assembly Specifications
    const systemManifest = [
      {
        id: 'skeletal',
        file: '/models/anatria/skeletal_male.glb',
        color: 0xf8fafc, // Crisp bright ivory bone (high contrast)
        roughness: 0.32,
        metalness: 0.06,
        opacity: 1.0
      },
      {
        id: 'cardiovascular',
        file: '/models/anatria/cardiovascular_male.glb',
        color: 0xef4444, // Bright Arterial Crimson
        roughness: 0.35,
        metalness: 0.15,
        opacity: 1.0
      },
      {
        id: 'respiratory',
        file: '/models/anatria/respiratory_male.glb',
        color: 0x0ea5e9, // Vivid Pulmonary Azure
        roughness: 0.38,
        metalness: 0.10,
        opacity: 0.95
      },
      {
        id: 'digestive',
        file: '/models/anatria/digestive_male.glb',
        color: 0xea580c, // Rich Warm Hepatic Terracotta
        roughness: 0.38,
        metalness: 0.12,
        opacity: 1.0
      },
      {
        id: 'renal',
        file: '/models/anatria/renal_male.glb',
        color: 0xe11d48, // Vivid Renal Ruby
        roughness: 0.35,
        metalness: 0.15,
        opacity: 1.0
      },
      {
        id: 'endocrine',
        file: '/models/anatria/endocrine_male.glb',
        color: 0xf59e0b, // Luminous Endocrine Amber/Gold
        roughness: 0.30,
        metalness: 0.10,
        opacity: 1.0
      },
      {
        id: 'nervous',
        file: '/models/anatria/nervous_male.glb',
        color: 0x8b5cf6, // Electric Neuro Violet
        roughness: 0.38,
        metalness: 0.10,
        opacity: 1.0
      },
      {
        id: 'regional',
        file: '/models/anatria/regional_male.glb',
        color: 0x38bdf8, // Luminous Holographic Cyan Shell
        roughness: 0.18,
        metalness: 0.08,
        opacity: this.bodyShellOpacity,
        transparent: true,
        isShell: true
      }
    ];

    systemManifest.forEach((sys) => {
      loader.load(sys.file, (gltf) => {
        const model = gltf.scene;
        model.name = sys.id;
        this.systems[sys.id] = model;

        if (sys.isShell) {
          this.bodyShell = model;
        }

        model.traverse((child) => {
          if (child.isMesh) {
            const meshName = (child.name || '').toLowerCase();
            let organKey = null;
            let meshColor = sys.color;

            // Granular anatomical mapping based on precise node names
            if (meshName.includes('liver') || meshName.includes('hepar')) {
              organKey = 'Liver';
              meshColor = 0xf97316; // Vibrant terracotta amber for liver
            } else if (meshName.includes('heart') || meshName.includes('ventricle') || meshName.includes('atrium') || meshName.includes('ascending aorta') || meshName.includes('myocard') || meshName.includes('coronary')) {
              organKey = 'Heart';
              meshColor = 0xef4444; // Vibrant crimson
            } else if (meshName.includes('kidney') || meshName.includes('renal')) {
              organKey = 'Kidneys';
              meshColor = 0xe11d48; // Renal ruby
            } else if (meshName.includes('lung') || meshName.includes('bronch') || meshName.includes('pleura')) {
              organKey = 'Lungs';
              meshColor = 0x0ea5e9; // Pulmonary azure
            } else if (meshName.includes('stomach') || meshName.includes('gaster')) {
              organKey = 'Stomach';
              meshColor = 0xfb923c; // Gastric coral
            } else if (meshName.includes('pancreas')) {
              organKey = 'Pancreas';
              meshColor = 0xf59e0b; // Amber
            } else if (meshName.includes('colon') || meshName.includes('ileum') || meshName.includes('duodenum') || meshName.includes('jejunum') || meshName.includes('cecum') || meshName.includes('rectum')) {
              organKey = 'Intestines';
              meshColor = 0xec4899; // Enteric rose
            } else if (meshName.includes('brain') || meshName.includes('midbrain') || meshName.includes('cerebr') || meshName.includes('hypothalamus') || meshName.includes('gyrus') || meshName.includes('cortex')) {
              organKey = 'Brain';
              meshColor = 0xa855f7; // Neuro violet
            } else if (meshName.includes('vertebra') || meshName.includes('spine') || meshName.includes('sacrum') || meshName.includes('intervertebral')) {
              organKey = 'Spine';
              meshColor = 0xf8fafc; // Bone white
            } else if (meshName.includes('thyroid')) {
              organKey = 'Thyroid';
              meshColor = 0xeab308; // Thyroid gold
            }

            child.userData.system = sys.id;
            child.userData.organName = organKey;
            child.userData.defaultColor = meshColor;
            child.userData.originalPosition = child.position.clone();

            // Apply authentic medical-grade PBR shading
            if (sys.isShell) {
              // Translucent, high-fidelity medical glass outer body shell
              child.material = new THREE.MeshPhysicalMaterial({
                color: 0x67e8f9,
                transparent: true,
                opacity: this.bodyShellOpacity,
                roughness: 0.18,
                metalness: 0.08,
                clearcoat: 1.0,
                clearcoatRoughness: 0.15,
                transmission: 0.45,
                ior: 1.35,
                depthWrite: false,
                side: THREE.DoubleSide
              });
              child.castShadow = false;
              child.receiveShadow = false;
            } else if (sys.id === 'respiratory') {
              // Lungs: Translucent pulmonary azure so Heart is clearly visible inside
              child.material = new THREE.MeshStandardMaterial({
                color: 0x0ea5e9,
                roughness: 0.40,
                metalness: 0.08,
                transparent: true,
                opacity: 0.35,
                depthWrite: false
              });
              child.userData.isTranslucent = true;
              child.userData.defaultOpacity = 0.35;
              child.castShadow = false;
              child.receiveShadow = false;
            } else if (sys.id === 'skeletal' && (meshName.includes('rib') || meshName.includes('sternum') || meshName.includes('cartilage'))) {
              // Thoracic cage ribs: Translucent ivory bone so internal organs shine through
              child.material = new THREE.MeshStandardMaterial({
                color: 0xf8fafc,
                roughness: 0.32,
                metalness: 0.06,
                transparent: true,
                opacity: 0.65,
                depthWrite: true
              });
              child.userData.isTranslucent = true;
              child.userData.defaultOpacity = 0.65;
              child.castShadow = true;
              child.receiveShadow = true;
            } else if (organKey === 'Heart') {
              // Vibrant arterial crimson heart with emissive myocardium
              child.material = new THREE.MeshStandardMaterial({
                color: 0xef4444,
                roughness: 0.25,
                metalness: 0.15,
                emissive: 0xdc2626,
                emissiveIntensity: 0.40
              });
              child.userData.defaultEmissive = 0.40;
              child.castShadow = true;
              child.receiveShadow = true;
              this.heartMeshes = this.heartMeshes || [];
              this.heartMeshes.push(child);
            } else if (sys.id === 'cardiovascular') {
              // Peripheral blood vessels: slightly translucent to prevent visual clutter
              child.material = new THREE.MeshStandardMaterial({
                color: 0xef4444,
                roughness: 0.35,
                metalness: 0.10,
                transparent: true,
                opacity: 0.50
              });
              child.userData.isTranslucent = true;
              child.userData.defaultOpacity = 0.50;
              child.castShadow = false;
              child.receiveShadow = false;
            } else if (organKey === 'Brain') {
              // Electric neuro-violet brain cortex with glowing emissive centers
              child.material = new THREE.MeshStandardMaterial({
                color: 0xa855f7,
                roughness: 0.28,
                metalness: 0.12,
                emissive: 0x7e22ce,
                emissiveIntensity: 0.45
              });
              child.userData.defaultEmissive = 0.45;
              child.castShadow = true;
              child.receiveShadow = true;
            } else if (sys.id === 'nervous') {
              // Minor peripheral nerves: subtle transparency
              child.material = new THREE.MeshStandardMaterial({
                color: 0x8b5cf6,
                roughness: 0.40,
                metalness: 0.08,
                transparent: true,
                opacity: 0.32
              });
              child.userData.isTranslucent = true;
              child.userData.defaultOpacity = 0.32;
              child.castShadow = false;
              child.receiveShadow = false;
            } else if (organKey === 'Liver') {
              // Rich terracotta amber liver
              child.material = new THREE.MeshStandardMaterial({
                color: 0xf97316,
                roughness: 0.28,
                metalness: 0.10,
                emissive: 0xc2410c,
                emissiveIntensity: 0.30
              });
              child.userData.defaultEmissive = 0.30;
              child.castShadow = true;
              child.receiveShadow = true;
            } else if (organKey === 'Kidneys') {
              // Renal ruby kidneys
              child.material = new THREE.MeshStandardMaterial({
                color: 0xe11d48,
                roughness: 0.28,
                metalness: 0.12,
                emissive: 0xbe123c,
                emissiveIntensity: 0.35
              });
              child.userData.defaultEmissive = 0.35;
              child.castShadow = true;
              child.receiveShadow = true;
            } else if (organKey === 'Pancreas') {
              child.material = new THREE.MeshStandardMaterial({
                color: 0xf59e0b,
                roughness: 0.30,
                metalness: 0.10,
                emissive: 0xb45309,
                emissiveIntensity: 0.30
              });
              child.userData.defaultEmissive = 0.30;
              child.castShadow = true;
              child.receiveShadow = true;
            } else if (organKey === 'Stomach') {
              child.material = new THREE.MeshStandardMaterial({
                color: 0xfb923c,
                roughness: 0.30,
                metalness: 0.10,
                emissive: 0xc2410c,
                emissiveIntensity: 0.25
              });
              child.userData.defaultEmissive = 0.25;
              child.castShadow = true;
              child.receiveShadow = true;
            } else if (organKey === 'Thyroid') {
              child.material = new THREE.MeshStandardMaterial({
                color: 0xeab308,
                roughness: 0.28,
                metalness: 0.10,
                emissive: 0xa16207,
                emissiveIntensity: 0.35
              });
              child.userData.defaultEmissive = 0.35;
              child.castShadow = true;
              child.receiveShadow = true;
            } else {
              // Standard organ & skeletal meshes
              child.material = new THREE.MeshStandardMaterial({
                color: meshColor,
                roughness: sys.roughness,
                metalness: sys.metalness,
                emissive: 0x000000,
                emissiveIntensity: 0.0
              });
              child.castShadow = true;
              child.receiveShadow = true;
            }

            if (organKey) {
              this.meshToOrganName.set(child, organKey);
              if (!this.organs[organKey]) {
                this.organs[organKey] = [];
              }
              this.organs[organKey].push(child);
            }
          }
        });

        this.masterGroup.add(model);
      }, undefined, (err) => {
        console.warn(`Could not load ${sys.file}:`, err);
      });
    });
  }

  setupEventListeners() {
    const dom = this.renderer.domElement;
    let clickStartX = 0;
    let clickStartY = 0;

    dom.addEventListener('mousedown', (e) => {
      clickStartX = e.clientX;
      clickStartY = e.clientY;
    });

    dom.addEventListener('mouseup', (e) => {
      // Disallow orbit rotation drag from registering as organ clicks
      const diffX = Math.abs(e.clientX - clickStartX);
      const diffY = Math.abs(e.clientY - clickStartY);
      if (diffX < 5 && diffY < 5) {
        this.handleRaycastClick(e);
      }
    });

    dom.addEventListener('mousemove', (e) => {
      const rect = dom.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      // Hover picking feedback & HUD Tooltip tracking
      this.raycaster.setFromCamera(this.mouse, this.camera);
      const interactiveMeshes = Array.from(this.meshToOrganName.keys());
      const intersects = this.raycaster.intersectObjects(interactiveMeshes, false);

      if (intersects.length > 0) {
        dom.style.cursor = 'pointer';
        const hitMesh = intersects[0].object;
        const organKey = this.meshToOrganName.get(hitMesh);
        if (organKey) {
          this.showHudTooltip(e, organKey);
          this.setHoverHighlight(organKey);
        }
      } else {
        dom.style.cursor = 'default';
        this.hideHudTooltip();
        this.clearHoverHighlight();
      }
    });

    dom.addEventListener('mouseleave', () => {
      this.hideHudTooltip();
      this.clearHoverHighlight();
    });
  }

  showHudTooltip(event, organKey) {
    if (!this.hudTooltip) return;
    const config = this.organCatalog[organKey];
    if (!config) return;

    const rect = this.container.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    this.hudTooltip.style.left = `${x}px`;
    this.hudTooltip.style.top = `${y}px`;

    const testsHtml = (config.tests || []).slice(0, 4).map(t =>
      `<span class="hud-test-badge">${t}</span>`
    ).join('');

    this.hudTooltip.innerHTML = `
      <div class="hud-title">${config.name.split(' (')[0]}</div>
      <div class="hud-latin">${config.latin || 'Organum humanum'} • TA2</div>
      <div class="hud-system">${config.system}</div>
      <div class="hud-tests">${testsHtml}</div>
      <div class="hud-action">
        <svg class="w-3 h-3 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
        <span>Click for Organ Reveal & BioSignals</span>
      </div>
    `;

    this.hudTooltip.classList.remove('hidden');
  }

  hideHudTooltip() {
    if (this.hudTooltip) {
      this.hudTooltip.classList.add('hidden');
    }
  }

  setHoverHighlight(organKey) {
    if (this.hoveredOrgan === organKey) return;
    this.clearHoverHighlight();
    this.hoveredOrgan = organKey;

    if (this.activeOrgan === organKey) return; // already active

    const meshes = this.organs[organKey] || [];
    meshes.forEach((mesh) => {
      if (mesh.material) {
        mesh.material.emissive.setHex(0x14b8a6); // Clinical teal hover glow
        mesh.material.emissiveIntensity = 0.28;
      }
    });
  }

  clearHoverHighlight() {
    if (!this.hoveredOrgan) return;
    if (this.hoveredOrgan !== this.activeOrgan) {
      const meshes = this.organs[this.hoveredOrgan] || [];
      meshes.forEach((mesh) => {
        if (mesh.material) {
          mesh.material.emissiveIntensity = 0.0;
        }
      });
    }
    this.hoveredOrgan = null;
  }

  handleRaycastClick(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const interactiveMeshes = Array.from(this.meshToOrganName.keys());
    const intersects = this.raycaster.intersectObjects(interactiveMeshes, false);

    if (intersects.length > 0) {
      const hitMesh = intersects[0].object;
      const organName = this.meshToOrganName.get(hitMesh);
      if (organName) {
        this.selectOrgan(organName, true);
      }
    }
  }

  // --- SIGNATURE INTERACTION: THE ORGAN REVEAL & BIOSIGNALS ---
  selectOrgan(organName, triggerCallback = true) {
    this.triggerOrganReveal(organName, triggerCallback);
  }

  triggerOrganReveal(organName, triggerCallback = true) {
    const config = this.organCatalog[organName];
    if (!config) return;

    this.activeOrgan = organName;

    // 1. Visual Highlighting & Non-Relevant Organ Dimming
    const selectedColor = new THREE.Color(config.color);
    const emissiveHighlight = new THREE.Color(0x159a92); // Precision Medical Teal (#159A92)

    this.meshToOrganName.forEach((orgKey, mesh) => {
      if (orgKey === organName) {
        mesh.visible = true;
        mesh.material.transparent = false;
        mesh.material.opacity = 1.0;
        mesh.material.color.copy(selectedColor);
        mesh.material.emissive.copy(emissiveHighlight);
        mesh.material.emissiveIntensity = 0.45;
      } else {
        if (this.isIsolated) {
          mesh.visible = false;
        } else {
          mesh.visible = true;
          mesh.material.transparent = true;
          mesh.material.opacity = 0.15; // Soft ethereal background dimming
          mesh.material.emissiveIntensity = 0.0;
        }
      }
    });

    // Also dim non-organ skeletal bones (like anterior ribs) and peripheral vessels so selected organ is clearly visible
    Object.keys(this.systems).forEach(sysId => {
      if (sysId !== 'regional') {
        this.systems[sysId].traverse(child => {
          if (child.isMesh && !this.meshToOrganName.has(child)) {
            if (this.isIsolated) {
              child.visible = false;
            } else {
              child.material.transparent = true;
              child.material.opacity = 0.12;
            }
          }
        });
      }
    });

    // 2. Smooth Cinematic Camera Tween: frame organ in the open center of the viewport
    const framedPos = [config.cameraPos[0] + 0.12, config.cameraPos[1], config.cameraPos[2]];
    const framedTarget = [config.cameraTarget[0] + 0.12, config.cameraTarget[1], config.cameraTarget[2]];
    this.transitionCamera(framedPos, framedTarget, 0.95);

    // 3. Trigger External Callback (for lab table filtering and sidebars)
    if (triggerCallback && typeof this.options.onOrganSelected === 'function') {
      this.options.onOrganSelected(organName, config);
    }

    // 4. Update UI labels, BioSignals spatial cards, and dynamic SVG connector
    this.updateOverlayUI(organName, config);
  }

  // --- 3D to 2D Screen-Space Projection for Organ Anchor ---
  getOrganScreenCoordinates(organName) {
    const config = this.organCatalog[organName];
    if (!config || !this.camera || !this.renderer) return null;

    let anchor = null;
    const meshes = this.organs[organName];
    if (meshes && meshes.length > 0) {
      const box = new THREE.Box3();
      meshes.forEach(m => box.expandByObject(m));
      anchor = box.getCenter(new THREE.Vector3());
    } else {
      anchor = new THREE.Vector3(...(config.anchorWorld || config.cameraTarget));
    }
    anchor.project(this.camera);

    const rect = this.renderer.domElement.getBoundingClientRect();
    const halfWidth = rect.width / 2;
    const halfHeight = rect.height / 2;

    const screenX = (anchor.x * halfWidth) + halfWidth;
    const screenY = -(anchor.y * halfHeight) + halfHeight;

    return {
      x: screenX,
      y: screenY,
      inFront: anchor.z < 1.0,
      visible: screenX >= 0 && screenX <= rect.width && screenY >= 0 && screenY <= rect.height
    };
  }

  // Update Dynamic SVG Connector Line and Pulsing Screen Anchor
  updateBioSignalsConnector() {
    if (!this.activeOrgan || !this.anchorMarker) return;

    const coords = this.getOrganScreenCoordinates(this.activeOrgan);
    if (!coords || !coords.inFront) {
      if (this.anchorMarker) this.anchorMarker.classList.add('opacity-0');
      if (this.connectorPath) this.connectorPath.setAttribute('d', '');
      return;
    }

    // Position Pulsing 3D Anchor Hotspot
    this.anchorMarker.style.left = `${coords.x}px`;
    this.anchorMarker.style.top = `${coords.y}px`;
    this.anchorMarker.classList.remove('opacity-0');

    // Draw Smooth Bezier Connector to Right Spatial Card
    const targetCard = document.getElementById('organ-detail-panel');
    if (targetCard && this.connectorPath) {
      const containerRect = this.container.getBoundingClientRect();
      const cardRect = targetCard.getBoundingClientRect();

      // Connector target: Left-center edge of the floating spatial card
      const targetX = cardRect.left - containerRect.left;
      const targetY = (cardRect.top - containerRect.top) + Math.min(120, cardRect.height / 3);

      if (targetX > coords.x) {
        const dx = targetX - coords.x;
        const cp1x = coords.x + dx * 0.45;
        const cp1y = coords.y;
        const cp2x = coords.x + dx * 0.55;
        const cp2y = targetY;

        const pathData = `M ${coords.x} ${coords.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${targetX} ${targetY}`;
        this.connectorPath.setAttribute('d', pathData);
      } else {
        this.connectorPath.setAttribute('d', '');
      }
    }
  }

  transitionCamera(targetPos, targetLookAt, duration = 0.95) {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion || typeof gsap === 'undefined') {
      this.camera.position.set(...targetPos);
      if (this.controls) {
        this.controls.target.set(...targetLookAt);
        this.controls.update();
      }
      return;
    }

    // Smooth GSAP Tweening
    gsap.to(this.camera.position, {
      x: targetPos[0],
      y: targetPos[1],
      z: targetPos[2],
      duration: duration,
      ease: 'power2.inOut'
    });

    if (this.controls) {
      gsap.to(this.controls.target, {
        x: targetLookAt[0],
        y: targetLookAt[1],
        z: targetLookAt[2],
        duration: duration,
        ease: 'power2.inOut',
        onUpdate: () => {
          this.controls.update();
          this.updateBioSignalsConnector();
        }
      });
    }
  }

  // --- Viewpoint Presets ---
  setViewpoint(viewName) {
    const views = {
      'anterior': { pos: [0, 0.15, 2.2], target: [0, 0.15, 0] },
      'posterior': { pos: [0, 0.15, -2.2], target: [0, 0.15, 0] },
      'left': { pos: [-2.2, 0.15, 0], target: [0, 0.15, 0] },
      'right': { pos: [2.2, 0.15, 0], target: [0, 0.15, 0] },
      'superior': { pos: [0, 1.8, 0.6], target: [0, 0.7, 0] }
    };

    const target = views[viewName];
    if (target) {
      this.transitionCamera(target.pos, target.target, 0.85);

      // Update button active state
      document.querySelectorAll('.viewpoint-btn').forEach(btn => {
        if (btn.getAttribute('data-view') === viewName) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }
  }

  // --- Visual Diagnostic Render Modes ---
  setVisualMode(mode) {
    this.currentVisualMode = mode;

    this.meshToOrganName.forEach((orgKey, mesh) => {
      const defaultCol = mesh.userData.defaultColor || 0xffffff;

      if (mode === 'xray') {
        // Luminous Diagnostic Hologram Mode
        mesh.material.transparent = true;
        mesh.material.opacity = 0.35;
        mesh.material.color.setHex(0x38bdf8);
        mesh.material.emissive.setHex(0x0284c7);
        mesh.material.emissiveIntensity = 0.45;
        mesh.material.wireframe = false;
      } else if (mode === 'ghost') {
        // Ghost skeleton mode
        if (mesh.userData.system === 'skeletal') {
          mesh.material.transparent = true;
          mesh.material.opacity = 0.18;
          mesh.material.emissiveIntensity = 0.0;
        } else {
          mesh.material.transparent = false;
          mesh.material.opacity = 1.0;
          mesh.material.color.setHex(defaultCol);
          mesh.material.emissive.setHex(defaultCol);
          mesh.material.emissiveIntensity = 0.25;
        }
      } else {
        // Standard Anatomical PBR
        mesh.material.transparent = false;
        mesh.material.opacity = 1.0;
        mesh.material.color.setHex(defaultCol);
        mesh.material.emissiveIntensity = (this.activeOrgan === orgKey) ? 0.45 : 0.0;
      }
    });

    // Update active button state
    document.querySelectorAll('.render-mode-btn').forEach(btn => {
      if (btn.getAttribute('data-mode') === mode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  // --- Dissection / Explode Feature ---
  setExplodeFactor(factor) {
    this.explodeFactor = Math.max(0.0, Math.min(1.0, factor));

    if (this.systems.digestive) {
      this.systems.digestive.position.x = this.explodeFactor * 0.16;
      this.systems.digestive.position.z = this.explodeFactor * 0.12;
    }
    if (this.systems.respiratory) {
      this.systems.respiratory.position.x = -this.explodeFactor * 0.16;
      this.systems.respiratory.position.z = this.explodeFactor * 0.08;
    }
    if (this.systems.cardiovascular) {
      this.systems.cardiovascular.position.z = this.explodeFactor * 0.18;
    }
    if (this.systems.renal) {
      this.systems.renal.position.z = -this.explodeFactor * 0.12;
    }
  }

  // --- Light/Dark Viewport Theme Switcher ---
  setTheme(theme) {
    this.currentTheme = theme;
    if (theme === 'dark') {
      this.scene.background = this.darkBgColor;
      this.container.classList.remove('light-mode');
    } else {
      this.scene.background = this.lightBgColor;
      this.container.classList.add('light-mode');
    }
  }

  toggleTheme() {
    this.setTheme(this.currentTheme === 'dark' ? 'light' : 'dark');
  }

  resetView() {
    this.activeOrgan = null;
    this.isIsolated = false;

    // Clear dynamic anchor & connector
    if (this.anchorMarker) this.anchorMarker.classList.add('opacity-0');
    if (this.connectorPath) this.connectorPath.setAttribute('d', '');

    // Restore all organ materials and full visibility
    this.meshToOrganName.forEach((orgKey, mesh) => {
      const defaultCol = mesh.userData.defaultColor || 0xffffff;
      mesh.visible = true;
      if (mesh.userData.isTranslucent) {
        mesh.material.transparent = true;
        mesh.material.opacity = mesh.userData.defaultOpacity || 0.40;
      } else {
        mesh.material.transparent = false;
        mesh.material.opacity = 1.0;
      }
      mesh.material.color.setHex(defaultCol);
      mesh.material.emissiveIntensity = mesh.userData.defaultEmissive || 0.0;
    });

    // Restore systems visibility
    Object.keys(this.systems).forEach((sysId) => {
      this.systems[sysId].visible = true;
      this.systems[sysId].traverse((child) => {
        if (child.isMesh) {
          child.visible = true;
          if (child.userData.isTranslucent) {
            child.material.transparent = true;
            child.material.opacity = child.userData.defaultOpacity || 0.40;
          } else if (child.userData.organName) {
            // Already handled in meshToOrganName
          } else {
            child.material.transparent = false;
            child.material.opacity = 1.0;
          }
        }
      });
    });

    if (this.bodyShell) {
      this.bodyShell.visible = this.bodyShellVisible;
      this.setBodyShellOpacity(this.bodyShellOpacity);
    }

    this.transitionCamera([this.defaultCameraPos.x, this.defaultCameraPos.y, this.defaultCameraPos.z],
                          [this.defaultCameraTarget.x, this.defaultCameraTarget.y, this.defaultCameraTarget.z], 1.0);

    const activePill = document.getElementById('active-organ-label');
    if (activePill) activePill.textContent = 'Whole Body (Interactive 3D)';

    const detailCard = document.getElementById('organ-detail-panel');
    if (detailCard) detailCard.classList.add('hidden');
  }

  toggleIsolation() {
    this.isIsolated = !this.isIsolated;
    if (this.activeOrgan) {
      this.selectOrgan(this.activeOrgan, false);
    }
  }

  toggleBodyShell(visible) {
    this.bodyShellVisible = visible !== undefined ? visible : !this.bodyShellVisible;
    if (this.bodyShell) {
      this.bodyShell.visible = this.bodyShellVisible;
    }
  }

  setBodyShellOpacity(opacityValue) {
    this.bodyShellOpacity = Math.max(0.0, Math.min(1.0, opacityValue));
    if (this.bodyShell) {
      this.bodyShell.traverse((child) => {
        if (child.isMesh && child.material) {
          child.material.opacity = this.bodyShellOpacity;
          child.material.transparent = this.bodyShellOpacity < 0.99;
          child.visible = this.bodyShellOpacity > 0.02;
        }
      });
    }
  }

  setSystemFilter(systemName) {
    this.activeSystemFilter = systemName;
    Object.keys(this.systems).forEach((sysId) => {
      const systemObj = this.systems[sysId];
      if (sysId === 'regional') {
        systemObj.visible = this.bodyShellVisible;
      } else {
        const match = (systemName === 'all' || sysId === systemName);
        systemObj.visible = match;
      }
    });
  }

  // --- 3D ANATOMICAL LAYERS ---
  setLayer(layerMode) {
    this.currentLayerMode = layerMode;

    // Update layer preset buttons in DOM
    ['full', 'organs', 'skeleton', 'individual'].forEach(mode => {
      const btn = document.getElementById(`layer-btn-${mode}`);
      if (btn) {
        if (mode === layerMode) {
          btn.className = 'layer-mode-btn active p-2.5 rounded-lg text-left bg-teal-500/20 text-teal-300 border border-teal-500/50 flex items-center justify-between';
        } else {
          btn.className = 'layer-mode-btn p-2.5 rounded-lg text-left bg-slate-900/60 text-slate-300 border border-slate-800 hover:border-slate-700 flex items-center justify-between';
        }
      }
    });

    if (layerMode === 'full') {
      // 1. Full Body: All organs visible + outer skin shell
      Object.keys(this.systems).forEach(sysId => {
        if (this.systems[sysId]) this.systems[sysId].visible = true;
      });
      this.meshToOrganName.forEach((orgKey, mesh) => {
        mesh.visible = true;
        if (mesh.userData.isTranslucent) {
          mesh.material.transparent = true;
          mesh.material.opacity = mesh.userData.defaultOpacity || 0.40;
        } else {
          mesh.material.transparent = false;
          mesh.material.opacity = 1.0;
        }
        mesh.material.color.setHex(mesh.userData.defaultColor || 0xffffff);
        mesh.material.emissiveIntensity = (this.activeOrgan === orgKey) ? 0.45 : 0.0;
      });
      if (this.bodyShell) {
        this.bodyShell.visible = true;
        this.setBodyShellOpacity(this.bodyShellOpacity || 0.45);
      }
    } else if (layerMode === 'organs') {
      // 2. Internal Organs: Soft organs visible, skeleton hidden, shell hidden
      Object.keys(this.systems).forEach(sysId => {
        if (this.systems[sysId]) {
          this.systems[sysId].visible = (sysId !== 'skeletal' && sysId !== 'regional');
        }
      });
      this.meshToOrganName.forEach((orgKey, mesh) => {
        if (mesh.userData.system === 'skeletal') {
          mesh.visible = false;
        } else {
          mesh.visible = true;
          mesh.material.transparent = false;
          mesh.material.opacity = 1.0;
          mesh.material.color.setHex(mesh.userData.defaultColor || 0xffffff);
          mesh.material.emissiveIntensity = (this.activeOrgan === orgKey) ? 0.45 : 0.0;
        }
      });
      if (this.bodyShell) this.bodyShell.visible = false;
    } else if (layerMode === 'skeleton') {
      // 3. Skeleton: Only bone structure visible, organs hidden, shell hidden
      Object.keys(this.systems).forEach(sysId => {
        if (this.systems[sysId]) {
          this.systems[sysId].visible = (sysId === 'skeletal');
        }
      });
      this.meshToOrganName.forEach((orgKey, mesh) => {
        if (mesh.userData.system === 'skeletal') {
          mesh.visible = true;
          mesh.material.transparent = false;
          mesh.material.opacity = 1.0;
          mesh.material.color.setHex(mesh.userData.defaultColor || 0xf8fafc);
        } else {
          mesh.visible = false;
        }
      });
      if (this.bodyShell) this.bodyShell.visible = false;
    } else if (layerMode === 'individual') {
      // 4. Individual Organ: Isolate selected organ, ghosting all others
      const targetOrgan = this.activeOrgan || 'Liver';
      this.isIsolated = true;
      Object.keys(this.systems).forEach(sysId => {
        if (this.systems[sysId]) this.systems[sysId].visible = true;
      });
      this.meshToOrganName.forEach((orgKey, mesh) => {
        if (orgKey === targetOrgan) {
          mesh.visible = true;
          mesh.material.transparent = false;
          mesh.material.opacity = 1.0;
          mesh.material.emissiveIntensity = 0.45;
        } else {
          mesh.visible = false;
        }
      });
      if (this.bodyShell) this.bodyShell.visible = false;
      this.selectOrgan(targetOrgan, true);
    }
  }

  // --- 3D INTERACTIVE EDUCATIONAL JOURNEYS (ALCOHOL & NUTRITION) ---
  startJourney(journeyType = 'alcohol') {
    this.activeJourneyType = journeyType;
    this.journeyStepIndex = 0;
    this.journeyIsPaused = false;
    clearTimeout(this.journeyTimer);

    // Update journey toggle button styles
    const alcBtn = document.getElementById('btn-journey-alcohol');
    const nutBtn = document.getElementById('btn-journey-nutrition');
    if (alcBtn && nutBtn) {
      if (journeyType === 'alcohol') {
        alcBtn.className = 'py-1.5 rounded text-xs font-bold text-center bg-amber-500/20 text-amber-300 border border-amber-500/40';
        nutBtn.className = 'py-1.5 rounded text-xs font-medium text-center text-slate-400 hover:text-white hover:bg-slate-800';
      } else {
        nutBtn.className = 'py-1.5 rounded text-xs font-bold text-center bg-teal-500/20 text-teal-300 border border-teal-500/40';
        alcBtn.className = 'py-1.5 rounded text-xs font-medium text-center text-slate-400 hover:text-white hover:bg-slate-800';
      }
    }

    if (journeyType === 'alcohol') {
      this.journeySteps = [
        {
          tag: 'Step 1 of 6',
          organ: null,
          title: 'Mouth & Esophagus',
          text: 'Alcohol enters through the mouth and esophagus. Around 5% can be absorbed directly through the mucosal lining into tiny blood vessels.',
          pos: [0, 0.65, 0.50],
          target: [0, 0.62, 0]
        },
        {
          tag: 'Step 2 of 6',
          organ: 'Stomach',
          title: 'Stomach (Gastric Wall)',
          text: 'About 20% of alcohol absorbs directly through the stomach wall into your bloodstream. Having food in your stomach slows this absorption significantly.',
          pos: [0.06, 0.35, 0.50],
          target: [0.04, 0.33, 0.04]
        },
        {
          tag: 'Step 3 of 6',
          organ: 'Intestines',
          title: 'Small Intestines',
          text: 'The remaining 75–80% of alcohol moves quickly into the small intestine, where it rapidly enters the portal vein traveling directly to the liver.',
          pos: [-0.05, 0.15, 0.58],
          target: [-0.06, 0.13, 0.00]
        },
        {
          tag: 'Step 4 of 6',
          organ: 'Liver',
          title: 'Liver (Main Clearance)',
          text: 'Your liver metabolizes over 90% of alcohol using enzymes. Constant heavy intake causes metabolic stress, reflected in elevated ALT and AST numbers.',
          pos: [-0.05, 0.38, 0.55],
          target: [-0.03, 0.35, 0.04]
        },
        {
          tag: 'Step 5 of 6',
          organ: 'Heart',
          title: 'Heart & Blood Vessels',
          text: 'Alcohol enters systemic circulation, temporarily raising heart rate and blood pressure, and influencing circulating lipids and triglycerides.',
          pos: [0.05, 0.45, 0.50],
          target: [0.04, 0.43, 0.03]
        },
        {
          tag: 'Step 6 of 6',
          organ: 'Brain',
          title: 'Brain & Nervous System',
          text: 'Alcohol easily crosses the blood-brain barrier, slowing nerve cell communication, affecting coordination, reaction time, and decision-making.',
          pos: [0.00, 0.80, 0.40],
          target: [0.00, 0.77, -0.01]
        }
      ];
    } else {
      this.journeySteps = [
        {
          tag: 'Step 1 of 5',
          organ: null,
          title: 'Mouth & Chewing',
          text: 'Digestion starts here! Chewing and salivary enzymes begin breaking down carbohydrates into simpler sugars.',
          pos: [0, 0.65, 0.50],
          target: [0, 0.62, 0]
        },
        {
          tag: 'Step 2 of 5',
          organ: 'Stomach',
          title: 'Stomach (Protein Breakdown)',
          text: 'Strong gastric acids and pepsin break proteins into amino acids. The stomach also releases intrinsic factor needed to absorb Vitamin B12.',
          pos: [0.06, 0.35, 0.50],
          target: [0.04, 0.33, 0.04]
        },
        {
          tag: 'Step 3 of 5',
          organ: 'Intestines',
          title: 'Small Intestines (Absorption)',
          text: 'Microscopic villi absorb vitamins, minerals (like iron and calcium), fatty acids, and glucose into the bloodstream.',
          pos: [-0.05, 0.15, 0.58],
          target: [-0.06, 0.13, 0.00]
        },
        {
          tag: 'Step 4 of 5',
          organ: 'Liver',
          title: 'Liver (Distribution & Storage)',
          text: 'The liver acts as your body\'s warehouse and chemical factory: sorting nutrients, balancing glucose, storing glycogen, and filtering waste.',
          pos: [-0.05, 0.38, 0.55],
          target: [-0.03, 0.35, 0.04]
        },
        {
          tag: 'Step 5 of 5',
          organ: 'Heart',
          title: 'Heart & 37 Trillion Cells',
          text: 'The heart pumps nutrient-rich, oxygenated blood to all 37 trillion cells in your body to fuel energy, tissue repair, and immunity.',
          pos: [0.05, 0.45, 0.50],
          target: [0.04, 0.43, 0.03]
        }
      ];
    }

    this.renderJourneyStep(0);
  }

  renderJourneyStep(index) {
    if (!this.journeySteps || index < 0 || index >= this.journeySteps.length) return;
    this.journeyStepIndex = index;
    const step = this.journeySteps[index];

    const tag = document.getElementById('journey-step-tag');
    const organTag = document.getElementById('journey-organ-tag');
    const text = document.getElementById('journey-step-text');
    const bar = document.getElementById('journey-progress-bar');

    if (tag) tag.textContent = step.tag;
    if (organTag) organTag.textContent = step.title;
    if (text) text.textContent = step.text;
    if (bar) {
      const pct = Math.round(((index + 1) / this.journeySteps.length) * 100);
      bar.style.width = `${pct}%`;
    }

    if (step.organ) {
      this.selectOrgan(step.organ, true);
    } else {
      this.transitionCamera(step.pos, step.target, 0.9);
    }

    // Auto Advance after 10s if not paused
    clearTimeout(this.journeyTimer);
    if (!this.journeyIsPaused) {
      this.journeyTimer = setTimeout(() => {
        this.nextJourneyStep();
      }, 10000);
    }
  }

  nextJourneyStep() {
    if (this.journeySteps && this.journeyStepIndex + 1 < this.journeySteps.length) {
      this.renderJourneyStep(this.journeyStepIndex + 1);
    } else {
      this.renderJourneyStep(0);
    }
  }

  prevJourneyStep() {
    if (this.journeySteps && this.journeyStepIndex > 0) {
      this.renderJourneyStep(this.journeyStepIndex - 1);
    }
  }

  toggleJourneyPlay() {
    this.journeyIsPaused = !this.journeyIsPaused;
    const btn = document.getElementById('journey-play-pause-btn');
    if (btn) btn.textContent = this.journeyIsPaused ? 'Play' : 'Pause';
    if (!this.journeyIsPaused) {
      this.nextJourneyStep();
    } else {
      clearTimeout(this.journeyTimer);
    }
  }

  resetJourney() {
    clearTimeout(this.journeyTimer);
    this.journeyIsPaused = true;
    const btn = document.getElementById('journey-play-pause-btn');
    if (btn) btn.textContent = 'Play';
    this.renderJourneyStep(0);
    this.resetView();
  }

  // --- MULTI-YEAR COMPARISON SPARKLINE & ENCOUNTER SWITCHER ---
  drawSparkline(canvasId, values, title) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const titleElem = document.getElementById('sparkline-title');
    if (titleElem && title) titleElem.textContent = title;

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    if (!values || values.length < 2) return;

    const min = Math.min(...values) * 0.85;
    const max = Math.max(...values) * 1.15;
    const range = (max - min) || 1;

    const paddingX = 35;
    const paddingY = 16;
    const drawW = width - (paddingX * 2);
    const drawH = height - (paddingY * 2);

    const points = values.map((v, i) => {
      const x = paddingX + (i / (values.length - 1)) * drawW;
      const y = height - paddingY - ((v - min) / range) * drawH;
      return { x, y, val: v };
    });

    // Draw baseline line
    ctx.strokeStyle = 'rgba(51, 65, 85, 0.4)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(paddingX, height - paddingY);
    ctx.lineTo(width - paddingX, height - paddingY);
    ctx.stroke();

    // Draw gradient area fill
    const grad = ctx.createLinearGradient(0, paddingY, 0, height - paddingY);
    grad.addColorStop(0, 'rgba(20, 184, 166, 0.35)');
    grad.addColorStop(1, 'rgba(20, 184, 166, 0.0)');

    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.lineTo(points[points.length - 1].x, height - paddingY);
    ctx.lineTo(points[0].x, height - paddingY);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // Draw line
    ctx.beginPath();
    ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i].x, points[i].y);
    }
    ctx.strokeStyle = '#14b8a6';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // Draw points and values
    points.forEach((p) => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#14b8a6';
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#0f172a';
      ctx.stroke();

      ctx.font = 'bold 9px monospace';
      ctx.fillStyle = '#f8fafc';
      ctx.textAlign = 'center';
      ctx.fillText(`${p.val}`, p.x, p.y - 6);
    });
  }

  switchEncounterYear(year) {
    const yrLabel = document.getElementById('organ-record-year');
    if (yrLabel) yrLabel.textContent = `${year} Report`;

    if (year === '2024') {
      this.verifiedBiomarkers['Liver'][0].val = 36;
      this.verifiedBiomarkers['Liver'][0].label = 'Normal';
      this.verifiedBiomarkers['Liver'][0].flag = 'normal';
      this.verifiedBiomarkers['Liver'][1].val = 28;
      this.verifiedBiomarkers['Liver'][1].label = 'Normal';
      this.verifiedBiomarkers['Liver'][1].flag = 'normal';
      this.drawSparkline('history-sparkline-canvas', [36, 48, 58], 'Liver: ALT (U/L) (Selected: 2024 Baseline)');
    } else if (year === '2025') {
      this.verifiedBiomarkers['Liver'][0].val = 48;
      this.verifiedBiomarkers['Liver'][0].label = 'Borderline';
      this.verifiedBiomarkers['Liver'][0].flag = 'high';
      this.verifiedBiomarkers['Liver'][1].val = 38;
      this.verifiedBiomarkers['Liver'][1].label = 'Borderline';
      this.verifiedBiomarkers['Liver'][1].flag = 'high';
      this.drawSparkline('history-sparkline-canvas', [36, 48, 58], 'Liver: ALT (U/L) (Selected: 2025 Follow-Up)');
    } else {
      this.verifiedBiomarkers['Liver'][0].val = 58;
      this.verifiedBiomarkers['Liver'][0].label = 'Mildly High';
      this.verifiedBiomarkers['Liver'][0].flag = 'high';
      this.verifiedBiomarkers['Liver'][1].val = 46;
      this.verifiedBiomarkers['Liver'][1].label = 'Mildly High';
      this.verifiedBiomarkers['Liver'][1].flag = 'high';
      this.drawSparkline('history-sparkline-canvas', [36, 48, 58], 'Liver: ALT (U/L) (Selected: 2026 Latest)');
    }

    if (this.activeOrgan) {
      this.updateOverlayUI(this.activeOrgan, this.organCatalog[this.activeOrgan]);
    }
  }

  // --- POPULATE BIOSIGNALS AND EXPANDABLE CLINICAL CARD ---
  updateOverlayUI(organName, config) {
    const labelElem = document.getElementById('active-organ-label');
    if (labelElem) labelElem.textContent = `${config.name.split(' (')[0]} (${config.latin || 'Anatomy'})`;

    const detailCard = document.getElementById('organ-detail-panel');
    if (!detailCard) return;

    detailCard.classList.remove('hidden');

    const title = document.getElementById('organ-title');
    if (title) title.textContent = config.name;

    const easyRole = document.getElementById('organ-easy-role');
    if (easyRole) easyRole.textContent = config.easyRole || `${config.name} • Clinical Analysis`;

    const role = document.getElementById('organ-role');
    if (role) role.textContent = config.role;

    const clinical = document.getElementById('organ-clinical');
    if (clinical) clinical.textContent = config.clinicalNote;

    const nutrition = document.getElementById('organ-nutrition');
    if (nutrition) nutrition.textContent = config.nutritionAdvice;

    const alcohol = document.getElementById('organ-alcohol');
    if (alcohol) alcohol.textContent = config.alcoholImpact;

    // Render BioSignals Cards for this Organ
    const biosignalsContainer = document.getElementById('organ-biomarkers-container');
    if (biosignalsContainer) {
      const markers = this.verifiedBiomarkers[organName] || [];
      if (markers.length === 0) {
        biosignalsContainer.innerHTML = `
          <div class="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-400">
            No abnormal findings flagged in current encounter for ${organName}.
          </div>
        `;
      } else {
        biosignalsContainer.innerHTML = markers.map((m, idx) => {
          let badgeClass = 'badge-normal';
          if (m.flag === 'high') badgeClass = 'badge-high';
          if (m.flag === 'urgent') badgeClass = 'badge-urgent';

          return `
            <div class="biosignal-card" onclick="window.anatomyInstance.toggleBiomarkerDrawer(${idx})">
              <div class="flex items-start justify-between gap-2">
                <div>
                  <div class="text-xs font-bold text-slate-100 flex items-center gap-1.5">
                    <span>${m.name}</span>
                    <span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-teal-300 font-mono">${m.conf}</span>
                  </div>
                  <div class="text-[11px] text-slate-400 mt-0.5">Reference: ${m.ref} ${m.unit} • ${m.page}</div>
                </div>
                <div class="text-right shrink-0">
                  <div class="text-sm font-extrabold text-white">${m.val} <span class="text-[10px] font-normal text-slate-400">${m.unit}</span></div>
                  <span class="${badgeClass} text-[10px] py-0 px-1.5 inline-block mt-0.5">${m.label}</span>
                </div>
              </div>
              <div id="biomarker-drawer-${idx}" class="hidden mt-2 pt-2 border-t border-slate-700/60 text-xs text-slate-300 leading-relaxed">
                <p><strong>Clinical Explanation:</strong> ${m.note}</p>
                <div class="mt-1.5 flex items-center gap-2 text-[10px] text-teal-300">
                  <span>Non-diagnostic educational finding.</span>
                </div>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    // Direct Action Bridges to Nutrition and Alcohol Modules
    const bridgesContainer = document.getElementById('organ-bridges-container');
    if (bridgesContainer) {
      bridgesContainer.innerHTML = `
        <div class="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-slate-800">
          <a href="/nutrition?focus=${encodeURIComponent(organName)}" class="px-2.5 py-1.5 rounded-lg bg-teal-950/80 hover:bg-teal-900 border border-teal-800 text-teal-300 text-xs font-semibold text-center transition-all flex items-center justify-center gap-1">
            <span>🌿 Fuel ${organName}</span>
          </a>
          <a href="/alcohol?focus=${encodeURIComponent(organName)}" class="px-2.5 py-1.5 rounded-lg bg-amber-950/80 hover:bg-amber-900 border border-amber-800 text-amber-300 text-xs font-semibold text-center transition-all flex items-center justify-center gap-1">
            <span>🍷 Alcohol Impact</span>
          </a>
        </div>
      `;
    }

    // Update connector immediately
    setTimeout(() => this.updateBioSignalsConnector(), 50);
  }

  toggleBiomarkerDrawer(index) {
    const drawer = document.getElementById(`biomarker-drawer-${index}`);
    if (drawer) {
      drawer.classList.toggle('hidden');
    }
  }

  // --- HEALTH STORY MODE ENGINE (CINEMATIC GUIDED TOUR) ---
  startHealthStory() {
    this.storyModeActive = true;
    this.storyStepIndex = 0;
    this.storyIsPaused = false;

    this.storyScenes = [
      {
        organ: null,
        title: "Patient Rohan Sharma (38M) — Clinical Trajectory",
        subtitle: "Comprehensive Multi-Panel Analysis Overview",
        body: "Analyzed 14 panels across 74 verified laboratory markers from three consecutive encounters (2024, 2025, 2026). The following guided tour highlights key physiological findings.",
        pos: [0, 0.15, 2.2],
        target: [0, 0.15, 0]
      },
      {
        organ: 'Liver',
        title: "Liver Tests & Cell Stress",
        subtitle: "ALT: 58 U/L (Mildly High) • AST: 46 U/L (Mildly High)",
        body: "Mild transaminase elevations indicate liver cells working under extra stress. Common causes include rich meals, metabolic workload, or alcohol. Key duct markers like bilirubin and alkaline phosphatase remain completely normal.",
        pos: [-0.05, 0.38, 0.55],
        target: [-0.03, 0.35, 0.04]
      },
      {
        organ: 'Kidneys',
        title: "Kidney Tests & Hydration Balance",
        subtitle: "eGFR: 88 mL/min • Creatinine: 1.05 mg/dL • BUN: 16 mg/dL",
        body: "Normal creatinine (1.05 mg/dL) shows strong, healthy kidney filtration. eGFR at 88 mL/min is well within normal range, showing good water and electrolyte balance.",
        pos: [0.00, 0.28, -0.55],
        target: [0.00, 0.26, -0.01]
      },
      {
        organ: 'Heart',
        title: "Heart & Cholesterol Levels",
        subtitle: "LDL: 142 mg/dL (Elevated) • ApoB: 104 mg/dL • Triglycerides: 165 mg/dL",
        body: "LDL ('bad') cholesterol at 142 mg/dL and ApoB at 104 mg/dL show more circulating cholesterol particles than ideal. Soluble oat fiber and brisk daily exercise can help balance these numbers.",
        pos: [0.05, 0.45, 0.50],
        target: [0.04, 0.43, 0.03]
      },
      {
        organ: 'Spine',
        title: "Bones & Vitamin D Levels",
        subtitle: "Vitamin D: 22.4 ng/mL (Needs Attention) • Calcium: 9.6 mg/dL",
        body: "Serum calcium is healthy (9.6 mg/dL), but Vitamin D is at 22.4 ng/mL (needs attention; healthy target is 30+ ng/mL). Vitamin D helps your bones stay strong. Safe sunlight and a D3 supplement can help.",
        pos: [0.00, 0.45, -0.65],
        target: [0.00, 0.44, -0.04]
      },
      {
        organ: null,
        title: "Whole-Food Nutrition & Physician Consultation",
        subtitle: "Targeted Indian Whole Foods & Clinician Talking Points",
        body: "Key lifestyle recommendations: emphasize amla and brassica greens for hepatic antioxidant support, oat beta-glucan for LDL, and discuss vitamin D3 supplementation with your primary physician.",
        pos: [0, 0.15, 2.2],
        target: [0, 0.15, 0]
      }
    ];

    this.renderStoryUI();
    this.goToStoryStep(0);
  }

  renderStoryUI() {
    let dock = document.getElementById('story-mode-dock');
    if (!dock) {
      dock = document.createElement('div');
      dock.id = 'story-mode-dock';
      dock.className = 'story-dock';
      this.container.appendChild(dock);
    }

    dock.innerHTML = `
      <div class="flex items-center gap-3">
        <span class="w-2.5 h-2.5 rounded-full bg-teal-400 animate-ping"></span>
        <div class="text-left">
          <div class="text-[10px] uppercase font-bold text-teal-400 tracking-wider">Health Story Mode</div>
          <div id="story-title-label" class="text-xs font-bold text-white">Scene 1 of 6</div>
        </div>
      </div>
      <div class="h-5 w-px bg-slate-700 mx-1"></div>
      <div class="flex items-center gap-1.5">
        <button onclick="window.anatomyInstance.prevStoryStep()" class="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 text-xs">
          ◀ Prev
        </button>
        <button id="story-play-btn" onclick="window.anatomyInstance.toggleStoryPlay()" class="px-2.5 py-1 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs">
          Pause
        </button>
        <button onclick="window.anatomyInstance.nextStoryStep()" class="p-1.5 rounded-lg hover:bg-slate-800 text-slate-300 text-xs">
          Next ▶
        </button>
        <button onclick="window.anatomyInstance.exitStory()" class="p-1.5 rounded-lg hover:bg-slate-800 text-rose-400 text-xs font-bold ml-1">
          ✕ Exit
        </button>
      </div>
    `;
    dock.classList.remove('hidden');
  }

  goToStoryStep(index) {
    if (!this.storyScenes || index < 0 || index >= this.storyScenes.length) {
      this.exitStory();
      return;
    }

    this.storyStepIndex = index;
    const scene = this.storyScenes[index];

    // Update Story Dock Label
    const titleLbl = document.getElementById('story-title-label');
    if (titleLbl) titleLbl.textContent = `${scene.title} (${index + 1}/${this.storyScenes.length})`;

    if (scene.organ) {
      this.selectOrgan(scene.organ, true);
    } else {
      this.resetView();
    }

    this.transitionCamera(scene.pos, scene.target, 1.1);

    // Auto Advance after 14 seconds if playing
    clearTimeout(this.storyTimer);
    if (!this.storyIsPaused) {
      this.storyTimer = setTimeout(() => {
        this.nextStoryStep();
      }, 14000);
    }
  }

  nextStoryStep() {
    if (this.storyStepIndex + 1 < this.storyScenes.length) {
      this.goToStoryStep(this.storyStepIndex + 1);
    } else {
      this.exitStory();
    }
  }

  prevStoryStep() {
    if (this.storyStepIndex > 0) {
      this.goToStoryStep(this.storyStepIndex - 1);
    }
  }

  toggleStoryPlay() {
    this.storyIsPaused = !this.storyIsPaused;
    const btn = document.getElementById('story-play-btn');
    if (btn) btn.textContent = this.storyIsPaused ? 'Play' : 'Pause';

    if (!this.storyIsPaused) {
      this.nextStoryStep();
    } else {
      clearTimeout(this.storyTimer);
    }
  }

  exitStory() {
    this.storyModeActive = false;
    clearTimeout(this.storyTimer);
    const dock = document.getElementById('story-mode-dock');
    if (dock) dock.classList.add('hidden');
    this.resetView();
  }

  // --- URL Query Parameter Deep-Linking ---
  checkForUrlParams() {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const focusOrgan = urlParams.get('focus');
      if (focusOrgan && this.organCatalog[focusOrgan]) {
        setTimeout(() => {
          this.selectOrgan(focusOrgan, true);
        }, 800);
      }
    } catch (e) {
      console.warn('URL param parse error:', e);
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    if (this.controls) {
      this.controls.update();
    }

    if (this.options.autoRotate && !this.activeOrgan && this.masterGroup) {
      this.masterGroup.rotation.y += 0.003;
    }

    // Physiological Cardiac Cycle (72 BPM Heartbeat Animation)
    const heartMeshes = this.organs['Heart'];
    if (heartMeshes && heartMeshes.length > 0) {
      const time = Date.now() * 0.0075;
      const cardiacPhase = Math.sin(time);
      if (cardiacPhase > 0.5) {
        const pulseScale = 1.0 + (cardiacPhase - 0.5) * 0.07;
        heartMeshes.forEach(mesh => {
          mesh.scale.set(pulseScale, pulseScale, pulseScale);
        });
      } else {
        heartMeshes.forEach(mesh => {
          mesh.scale.set(1.0, 1.0, 1.0);
        });
      }
    }

    // Update connector line on camera movement
    if (this.activeOrgan) {
      this.updateBioSignalsConnector();
    }

    this.renderer.render(this.scene, this.camera);
  }

  onWindowResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
    if (this.activeOrgan) {
      this.updateBioSignalsConnector();
    }
  }

  render2DFallback() {
    this.container.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full p-6 text-center bg-slate-900 border border-slate-700 rounded-xl text-white">
        <svg class="w-16 h-16 text-teal-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <h4 class="text-sm font-semibold text-white mb-1">Interactive 2D Anatomical Mode</h4>
        <p class="text-xs text-slate-300 max-w-sm mb-4">WebGL 3D hardware acceleration is unavailable on this device. Explore organs directly through our interactive clinical catalog below.</p>
        <div class="flex flex-wrap gap-1.5 justify-center">
          <button onclick="window.selectAnatomyOrgan && window.selectAnatomyOrgan('Liver')" class="px-2.5 py-1 text-xs rounded bg-slate-800 border border-slate-600 hover:border-teal-400 font-medium text-white">Liver</button>
          <button onclick="window.selectAnatomyOrgan && window.selectAnatomyOrgan('Heart')" class="px-2.5 py-1 text-xs rounded bg-slate-800 border border-slate-600 hover:border-teal-400 font-medium text-white">Heart</button>
          <button onclick="window.selectAnatomyOrgan && window.selectAnatomyOrgan('Kidneys')" class="px-2.5 py-1 text-xs rounded bg-slate-800 border border-slate-600 hover:border-teal-400 font-medium text-white">Kidneys</button>
          <button onclick="window.selectAnatomyOrgan && window.selectAnatomyOrgan('Pancreas')" class="px-2.5 py-1 text-xs rounded bg-slate-800 border border-slate-600 hover:border-teal-400 font-medium text-white">Pancreas</button>
        </div>
      </div>
    `;
  }
}

// Global initialization helper
window.AnatomyExplorer = AnatomyExplorer;
