/**
 * NutriSphere Quest — Learn Your Body (3D Health Games)
 * Features:
 * - Isolated Three.js Engine with Authentic glTF Anatomical Models
 * - Web Audio API Synthesizer (Chimes, fanfares, audio cues)
 * - Game 1: Find the Organ (3D Raycasting Organ Click Challenge)
 * - Game 2: Match the Medical Test (Biomarker Matching + 3D Camera Zoom)
 * - Game 3: Explore Your Body (Interactive Body Cards & Badges)
 * - SQLite & LocalStorage Score Sync
 */

// ==========================================
// 1. SOUND SYNTHESIZER (WEB AUDIO API)
// ==========================================
class SoundFX {
  constructor() {
    this.ctx = null;
    this.enabled = localStorage.getItem('games_sound') !== 'false';
  }

  init() {
    if (!this.ctx && typeof (window.AudioContext || window.webkitAudioContext) !== 'undefined') {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playTone(freq, duration = 0.12, type = 'sine', gainVal = 0.15) {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.warn('Audio error:', e);
    }
  }

  playSuccess() {
    if (!this.enabled) return;
    // Pleasant ascending chord: C5 (523Hz), E5 (659Hz), G5 (784Hz), C6 (1046Hz)
    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((freq, idx) => {
      setTimeout(() => this.playTone(freq, 0.18, 'triangle', 0.18), idx * 75);
    });
  }

  playError() {
    if (!this.enabled) return;
    // Low double blip
    this.playTone(180, 0.15, 'sawtooth', 0.12);
    setTimeout(() => this.playTone(140, 0.20, 'sawtooth', 0.10), 120);
  }

  playClick() {
    this.playTone(480, 0.05, 'sine', 0.08);
  }

  playFanfare() {
    if (!this.enabled) return;
    const notes = [440, 554, 659, 880];
    notes.forEach((freq, idx) => {
      setTimeout(() => this.playTone(freq, 0.25, 'triangle', 0.2), idx * 100);
    });
  }
}

// ==========================================
// 2. ORGAN & MEDICAL TEST CATALOG
// ==========================================
const ORGAN_DATA = {
  'Liver': {
    name: 'Liver',
    easyRole: "Your Body's Master Chemical Filter & Energy Center",
    latin: 'Hepar',
    system: 'Digestive System',
    cameraPos: [-0.05, 0.38, 0.55],
    cameraTarget: [-0.03, 0.35, 0.04],
    color: 0xf97316,
    tests: ['ALT (SGPT)', 'AST (SGOT)', 'Bilirubin Total', 'Albumin', 'ALP (Alkaline Phosphatase)'],
    hint: "Located in the upper right quadrant of your abdomen, beneath the diaphragm.",
    funFact: "The liver performs over 500 vital functions and is the only internal organ that can regenerate itself!",
    role: "Filters chemicals and medications from your bloodstream, turns digested food into stored energy (glycogen), and makes bile to break down fats.",
    nutrition: "Eat antioxidant-rich Indian foods: amla (Indian gooseberry), turmeric, cruciferous vegetables, garlic, and lentils (dal).",
    alcohol: "Over 90% of alcohol is broken down here. Drinking too much overworks liver cells, leading to temporary cell stress and fat buildup."
  },
  'Heart': {
    name: 'Heart',
    easyRole: "Your Body's Life Pump",
    latin: 'Cor',
    system: 'Cardiovascular System',
    cameraPos: [0.05, 0.45, 0.50],
    cameraTarget: [0.04, 0.43, 0.03],
    color: 0xef4444,
    tests: ['Total Cholesterol', 'LDL Cholesterol', 'HDL Cholesterol', 'Triglycerides', 'ApoB', 'Troponin I'],
    hint: "Located in the center of your chest, tilted slightly towards your left side.",
    funFact: "Your heart pumps about 2,000 gallons of blood every single day through 60,000 miles of blood vessels!",
    role: "Beats about 100,000 times a day to pump fresh oxygen and nutrients through your blood vessels to every part of your body.",
    nutrition: "Choose heart-healthy foods: oats (rich in beta-glucan soluble fiber), walnuts, chia seeds, flaxseeds, and low-sodium home-cooked meals.",
    alcohol: "Heavy drinking raises blood pressure and can cause irregular heartbeats. Cutting back helps blood vessels relax."
  },
  'Kidneys': {
    name: 'Kidneys',
    easyRole: "Your Natural Water & Salt Filters",
    latin: 'Renes',
    system: 'Renal / Urinary System',
    cameraPos: [0.00, 0.28, -0.55],
    cameraTarget: [0.00, 0.26, -0.01],
    color: 0xe11d48,
    tests: ['Serum Creatinine', 'eGFR', 'Blood Urea Nitrogen (BUN)', 'Uric Acid'],
    hint: "Located towards the back of your abdominal wall, just below your rib cage on either side of the spine.",
    funFact: "Your two kidneys filter about 200 quarts of fluid daily, balancing water, salts, and clearing metabolic waste through urine!",
    role: "Filter fluid constantly, balancing essential electrolytes like sodium and potassium while removing metabolic wastes.",
    nutrition: "Drink plenty of water, avoid excess sodium in snacks and processed food, and enjoy fresh fruits like apples, berries, and watermelon.",
    alcohol: "Alcohol is a diuretic that forces your kidneys to lose fluids rapidly, leading to dehydration and temporary electrolyte imbalance."
  },
  'Lungs': {
    name: 'Lungs',
    easyRole: "Your Oxygen Exchange Center",
    latin: 'Pulmones',
    system: 'Respiratory System',
    cameraPos: [0.00, 0.48, 0.65],
    cameraTarget: [0.01, 0.46, -0.01],
    color: 0x0ea5e9,
    tests: ['Hemoglobin', 'Hematocrit (PCV)', 'RBC Count', 'Oxygen Saturation'],
    hint: "Fill most of your chest cavity, resting safely inside your rib cage on both sides of the heart.",
    funFact: "The total surface area inside both lungs is roughly equal to half a tennis court (~70 square meters)!",
    role: "Take in fresh oxygen when you breathe in and release carbon dioxide when you breathe out, keeping your whole body energized.",
    nutrition: "Support lung tissue with vitamin C-rich foods: citrus fruits, amla, bell peppers, tomatoes, and plenty of water.",
    alcohol: "Heavy alcohol use weakens the natural defense of airway cells against airborne microbes."
  },
  'Pancreas': {
    name: 'Pancreas',
    easyRole: "Your Blood Sugar & Digestive Juice Factory",
    latin: 'Pancreas',
    system: 'Endocrine & Digestive System',
    cameraPos: [0.01, 0.30, 0.45],
    cameraTarget: [0.01, 0.28, 0.02],
    color: 0xf59e0b,
    tests: ['Fasting Blood Glucose', 'HbA1c', 'Serum Insulin', 'Serum Amylase', 'Serum Lipase'],
    hint: "Tucked deep in the upper abdomen behind your stomach.",
    funFact: "The pancreas produces insulin to regulate blood sugar and releases over 1 liter of digestive enzymes every single day!",
    role: "Produces insulin to keep blood sugar balanced, along with powerful digestive enzymes that break down proteins, fats, and carbohydrates.",
    nutrition: "Emphasize high-fiber foods: whole wheat roti, oats, fenugreek (methi) seeds, chickpeas, and green leafy vegetables.",
    alcohol: "Heavy alcohol can irritate pancreatic ducts and cause painful inflammation (pancreatitis). Moderation is key."
  },
  'Stomach': {
    name: 'Stomach',
    easyRole: "Your Main Food Breakdown Chamber",
    latin: 'Gaster',
    system: 'Digestive System',
    cameraPos: [0.06, 0.35, 0.50],
    cameraTarget: [0.04, 0.33, 0.04],
    color: 0xfb923c,
    tests: ['Vitamin B12', 'Serum Gastrin', 'Pepsinogen'],
    hint: "Located in the upper left side of your abdomen, connecting the esophagus to the small intestine.",
    funFact: "Your stomach lining secretes hydrochloric acid strong enough to dissolve metal, but secretes a mucus shield to protect itself!",
    role: "Uses natural stomach acids and churning motions to break down protein and produce Intrinsic Factor needed to absorb Vitamin B12.",
    nutrition: "Include fermented curd/yogurt, lentils, fortified foods, and avoid overly greasy late-night meals.",
    alcohol: "Alcohol irritates the stomach lining and increases stomach acid, which can cause heartburn or gastritis if taken on an empty stomach."
  },
  'Intestines': {
    name: 'Intestines',
    easyRole: "Your Nutrient Absorption Highway",
    latin: 'Intestinum',
    system: 'Digestive System',
    cameraPos: [-0.05, 0.15, 0.58],
    cameraTarget: [-0.06, 0.13, 0.00],
    color: 0xec4899,
    tests: ['Serum Ferritin', 'Serum Iron', 'Fecal Calprotectin'],
    hint: "Coiled in the central and lower abdomen beneath the stomach and liver.",
    funFact: "Your small intestine is over 20 feet long and covered in millions of microscopic finger-like villi that absorb nutrients!",
    role: "Absorbs water, vitamins, minerals, iron, and glucose into the blood while housing trillions of beneficial gut bacteria.",
    nutrition: "Feed beneficial gut flora with prebiotics and fiber: oats, bananas, garlic, onions, buttermilk, and dal.",
    alcohol: "Frequent alcohol can loosen gut barriers and cause temporary bloating or digestive discomfort."
  },
  'Brain': {
    name: 'Brain',
    easyRole: "Your Master Control Center",
    latin: 'Encephalon',
    system: 'Nervous System',
    cameraPos: [0.00, 0.80, 0.40],
    cameraTarget: [0.00, 0.77, -0.01],
    color: 0x8b5cf6,
    tests: ['Serum Folate', 'Homocysteine', 'Vitamin B12'],
    hint: "Enclosed safely inside your skull at the top of the body.",
    funFact: "Your brain generates about 20 watts of electrical power and consumes 20% of your body's total energy!",
    role: "Controls thinking, memories, emotions, movements, balance, and automatic bodily functions like breathing.",
    nutrition: "Nourish brain cells with walnuts, spinach, seeds, whole grains, and omega-3 rich foods.",
    alcohol: "Alcohol slows brain signaling, blunting reflexes and impairing memory formation and restful sleep."
  },
  'Spine': {
    name: 'Spine & Bones',
    easyRole: "Your Body's Strong Bone Framework",
    latin: 'Columna Vertebralis',
    system: 'Skeletal System',
    cameraPos: [0.00, 0.45, -0.65],
    cameraTarget: [0.00, 0.44, -0.04],
    color: 0xf8fafc,
    tests: ['Serum Calcium', '25-OH Vitamin D', 'Alkaline Phosphatase (Bone)'],
    hint: "Runs down the center of your back from the base of your skull to your tailbone.",
    funFact: "The adult spinal column consists of 33 vertebrae cushioning nerves that connect your brain to every organ!",
    role: "Provides structural support, protects your spinal cord, allows movement, and stores calcium and minerals.",
    nutrition: "Boost bone strength with sesame seeds (til), ragi (finger millet), curd/milk, and vitamin D3 with K2.",
    alcohol: "Chronic alcohol reduces bone-building cell activity and interferes with vitamin D activation."
  },
  'Thyroid': {
    name: 'Thyroid',
    easyRole: "Your Body's Energy & Metabolism Governor",
    latin: 'Glandula Thyroidea',
    system: 'Endocrine System',
    cameraPos: [0.00, 0.62, 0.35],
    cameraTarget: [0.00, 0.60, 0.02],
    color: 0xeab308,
    tests: ['TSH (Thyroid Stimulating Hormone)', 'Free T4 (Thyroxine)', 'Free T3'],
    hint: "Butterfly-shaped gland located in the lower front of your neck, just below your Adam's apple.",
    funFact: "The thyroid produces hormones that regulate the metabolic rate and temperature of nearly every cell in your body!",
    role: "Releases thyroid hormones (T3 and T4) that govern how quickly your cells burn calories and produce energy.",
    nutrition: "Include iodized salt, curd, eggs, seeds, and legumes to provide the building blocks for thyroid hormones.",
    alcohol: "Heavy alcohol can disrupt thyroid hormone synthesis and regulation by the pituitary gland."
  }
};

const MEDICAL_TEST_QUESTIONS = [
  {
    testName: "ALT (SGPT)",
    correctOrgan: "Liver",
    options: ["Liver", "Heart", "Kidneys", "Pancreas"],
    questionDesc: "Which organ releases this enzyme into your blood when its cells are irritated or processing medicines?",
    explanation: "ALT (Alanine Aminotransferase) lives inside liver cells. When liver cells experience metabolic stress or clear toxins, ALT leaks into the bloodstream, alerting doctors to look at diet or lifestyle."
  },
  {
    testName: "Serum Creatinine & eGFR",
    correctOrgan: "Kidneys",
    options: ["Kidneys", "Liver", "Lungs", "Brain"],
    questionDesc: "Which organ filters creatinine out of your blood 24/7 to determine your glomerular filtration rate?",
    explanation: "Creatinine is a natural muscle breakdown product. Healthy kidneys continuously filter it into urine. High creatinine or low eGFR indicates your kidneys are working extra hard."
  },
  {
    testName: "LDL & Total Cholesterol",
    correctOrgan: "Heart",
    options: ["Heart", "Pancreas", "Kidneys", "Spine"],
    questionDesc: "Which organ's arteries are most directly affected by circulating LDL particles that cause plaque buildup?",
    explanation: "LDL transports cholesterol through the blood. When levels are too high, particles can deposit along coronary arteries supplying your heart muscle. Soluble fiber helps clear excess LDL."
  },
  {
    testName: "Fasting Blood Glucose & HbA1c",
    correctOrgan: "Pancreas",
    options: ["Pancreas", "Heart", "Lungs", "Stomach"],
    questionDesc: "Which gland produces insulin to regulate your blood sugar and keep your HbA1c in a healthy range?",
    explanation: "Beta cells in your pancreas secrete insulin. When cells become resistant to insulin, blood sugar and HbA1c rise, signaling pre-diabetes or diabetes."
  },
  {
    testName: "TSH (Thyroid Stimulating Hormone)",
    correctOrgan: "Thyroid",
    options: ["Thyroid", "Liver", "Kidneys", "Intestines"],
    questionDesc: "Which butterfly-shaped gland responds to TSH to regulate your cellular metabolic burn rate?",
    explanation: "Your pituitary gland releases TSH to command the thyroid to produce energy hormones (T3 and T4). If the thyroid is sluggish, TSH goes up to urge it forward."
  },
  {
    testName: "Vitamin B12 & Intrinsic Factor",
    correctOrgan: "Stomach",
    options: ["Stomach", "Heart", "Spine", "Brain"],
    questionDesc: "Which organ's parietal cells must secrete Intrinsic Factor so Vitamin B12 can be absorbed?",
    explanation: "Your stomach produces hydrochloric acid and Intrinsic Factor. Without this special gastric protein, Vitamin B12 cannot be absorbed downstream in the small intestine."
  },
  {
    testName: "Serum Ferritin & Iron Absorption",
    correctOrgan: "Intestines",
    options: ["Intestines", "Lungs", "Heart", "Thyroid"],
    questionDesc: "Where does dietary iron pass through microscopic villi to enter the bloodstream and build ferritin stores?",
    explanation: "Your small intestine is lined with millions of tiny villi that absorb iron, vitamins, and minerals from food into the bloodstream."
  },
  {
    testName: "Serum Calcium & 25-OH Vitamin D",
    correctOrgan: "Spine",
    options: ["Spine", "Liver", "Heart", "Kidneys"],
    questionDesc: "Which structural framework stores 99% of your body's calcium and relies on Vitamin D for mineral density?",
    explanation: "Your bones and spine store calcium and phosphorus. Vitamin D is essential for absorbing calcium from food into bone tissue to prevent osteopenia."
  }
];

const ACHIEVEMENTS_DATA = [
  { id: "first_organ", title: "First Organ Found", desc: "Correctly identified your first organ in 3D!", icon: "🎯", points: 50 },
  { id: "organ_master", title: "Organ Master", desc: "Found all 10 organs in Game 1!", icon: "🔬", points: 200 },
  { id: "lab_detective", title: "Lab Detective", desc: "Matched 5 medical tests to their correct organs in Game 2!", icon: "🧪", points: 100 },
  { id: "body_explorer", title: "Body Explorer", desc: "Explored all body cards in Game 3!", icon: "🧭", points: 150 },
  { id: "grand_champion", title: "3D Health Champion", desc: "Accumulated over 400 total points in health games!", icon: "👑", points: 300 }
];

// ==========================================
// 3. THREE.JS 3D ENGINE
// ==========================================
class GameAnatomyEngine {
  constructor(canvasId, containerId, onOrganClicked) {
    this.canvas = document.getElementById(canvasId);
    this.container = document.getElementById(containerId);
    this.onOrganClicked = onOrganClicked;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();

    this.organMeshes = new Map(); // mesh -> organName
    this.systems = {};
    this.skinMesh = null;
    this.highlightedMesh = null;
    this.autoRotate = false;
    this.isSkinGlass = true;

    this.init();
  }

  init() {
    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0c131d);

    // 2. Camera
    const aspect = this.container.clientWidth / this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(40, aspect, 0.1, 100);
    this.camera.position.set(0, 0.45, 1.4);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputEncoding = THREE.sRGBEncoding;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.25;

    // 4. Lighting
    this.setupLighting();

    // 5. OrbitControls
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.target.set(0, 0.4, 0);
    this.controls.minDistance = 0.25;
    this.controls.maxDistance = 3.5;
    this.controls.maxPolarAngle = Math.PI * 0.85;

    // 6. Event Listeners
    this.setupEvents();

    // 7. Load 3D Models
    this.loadModels();

    // 8. Animation Loop
    this.animate();
  }

  setupLighting() {
    const ambient = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambient);

    const dirFront = new THREE.DirectionalLight(0xffffff, 1.2);
    dirFront.position.set(2, 4, 3);
    this.scene.add(dirFront);

    const dirBack = new THREE.DirectionalLight(0x38bdf8, 0.7);
    dirBack.position.set(-2, 2, -3);
    this.scene.add(dirBack);

    const bottomGlow = new THREE.DirectionalLight(0x14b8a6, 0.4);
    bottomGlow.position.set(0, -3, 1);
    this.scene.add(bottomGlow);
  }

  setupEvents() {
    window.addEventListener('resize', () => {
      if (!this.container || !this.renderer) return;
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });

    const tooltip = document.getElementById('game-organ-tooltip');

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      this.raycaster.setFromCamera(this.mouse, this.camera);
      const meshes = Array.from(this.organMeshes.keys());
      const hits = this.raycaster.intersectObjects(meshes, false);

      if (hits.length > 0) {
        this.canvas.style.cursor = 'pointer';
        const hit = hits[0].object;
        const organ = this.organMeshes.get(hit);
        if (organ && tooltip) {
          tooltip.innerText = organ;
          tooltip.style.left = `${e.clientX - rect.left + 15}px`;
          tooltip.style.top = `${e.clientY - rect.top - 15}px`;
          tooltip.classList.remove('hidden');
        }
      } else {
        this.canvas.style.cursor = 'default';
        if (tooltip) tooltip.classList.add('hidden');
      }
    });

    this.canvas.addEventListener('pointerdown', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      this.raycaster.setFromCamera(this.mouse, this.camera);
      const meshes = Array.from(this.organMeshes.keys());
      const hits = this.raycaster.intersectObjects(meshes, false);

      if (hits.length > 0) {
        const hit = hits[0].object;
        const organ = this.organMeshes.get(hit);
        if (organ && this.onOrganClicked) {
          this.onOrganClicked(organ);
        }
      }
    });
  }

  loadModels() {
    let dracoLoader = null;
    if (typeof THREE.DRACOLoader !== 'undefined') {
      dracoLoader = new THREE.DRACOLoader();
      dracoLoader.setDecoderPath('/draco/gltf/');
    }

    const loader = (typeof THREE.GLTFLoader !== 'undefined') ? new THREE.GLTFLoader() : null;
    if (!loader) {
      console.warn('GLTFLoader not available. Building fallback shapes.');
      this.buildFallbackScene();
      return;
    }

    if (dracoLoader) {
      loader.setDRACOLoader(dracoLoader);
    }

    const manifests = [
      { id: 'skeletal', file: '/models/anatria/skeletal_male.glb', defaultOrgan: 'Spine', color: 0xf8fafc },
      { id: 'cardiovascular', file: '/models/anatria/cardiovascular_male.glb', defaultOrgan: 'Heart', color: 0xef4444 },
      { id: 'respiratory', file: '/models/anatria/respiratory_male.glb', defaultOrgan: 'Lungs', color: 0x0ea5e9 },
      { id: 'digestive', file: '/models/anatria/digestive_male.glb', defaultOrgan: 'Liver', color: 0xea580c },
      { id: 'renal', file: '/models/anatria/renal_male.glb', defaultOrgan: 'Kidneys', color: 0xe11d48 },
      { id: 'endocrine', file: '/models/anatria/endocrine_male.glb', defaultOrgan: 'Thyroid', color: 0xeab308 },
      { id: 'nervous', file: '/models/anatria/nervous_male.glb', defaultOrgan: 'Brain', color: 0x8b5cf6 },
      { id: 'regional', file: '/models/anatria/regional_male.glb', isSkin: true, color: 0x38bdf8 }
    ];

    let loaded = 0;
    manifests.forEach((m) => {
      loader.load(
        m.file,
        (gltf) => {
          const model = gltf.scene;
          this.systems[m.id] = model;

          if (m.isSkin) {
            this.skinMesh = model;
          }

          model.traverse((child) => {
            if (child.isMesh) {
              const nameLower = (child.name || '').toLowerCase();
              let organ = m.defaultOrgan;

              if (nameLower.includes('liver')) organ = 'Liver';
              else if (nameLower.includes('heart') || nameLower.includes('ventricle') || nameLower.includes('atrium') || nameLower.includes('aorta')) organ = 'Heart';
              else if (nameLower.includes('kidney') || nameLower.includes('renal')) organ = 'Kidneys';
              else if (nameLower.includes('lung') || nameLower.includes('bronch')) organ = 'Lungs';
              else if (nameLower.includes('stomach')) organ = 'Stomach';
              else if (nameLower.includes('pancreas')) organ = 'Pancreas';
              else if (nameLower.includes('colon') || nameLower.includes('ileum') || nameLower.includes('duodenum')) organ = 'Intestines';
              else if (nameLower.includes('brain') || nameLower.includes('cerebr')) organ = 'Brain';
              else if (nameLower.includes('vertebra') || nameLower.includes('spine')) organ = 'Spine';
              else if (nameLower.includes('thyroid')) organ = 'Thyroid';

              if (m.isSkin) {
                child.material = new THREE.MeshPhysicalMaterial({
                  color: m.color,
                  transparent: true,
                  opacity: 0.12,
                  roughness: 0.2,
                  metalness: 0.05,
                  transmission: 0.65
                });
              } else if (organ) {
                this.organMeshes.set(child, organ);
                child.userData.organ = organ;
                child.userData.origMaterial = child.material.clone();
              }
            }
          });

          this.scene.add(model);
          loaded++;
        },
        undefined,
        () => {
          if (m.id === 'skeletal' && loaded === 0) {
            this.buildFallbackScene();
          }
        }
      );
    });
  }

  buildFallbackScene() {
    // Stylized interactive nodes for all 10 organs if glb files are missing
    const group = new THREE.Group();

    Object.entries(ORGAN_DATA).forEach(([organName, info]) => {
      const geo = new THREE.SphereGeometry(0.05, 24, 24);
      const mat = new THREE.MeshStandardMaterial({
        color: info.color,
        roughness: 0.3,
        metalness: 0.1
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(info.cameraTarget[0], info.cameraTarget[1], info.cameraTarget[2]);
      mesh.userData.organ = organName;
      mesh.userData.origMaterial = mat.clone();
      this.organMeshes.set(mesh, organName);
      group.add(mesh);
    });

    this.scene.add(group);
  }

  zoomToOrgan(organName) {
    const info = ORGAN_DATA[organName];
    if (!info) return;

    if (window.gsap) {
      window.gsap.to(this.camera.position, {
        x: info.cameraPos[0],
        y: info.cameraPos[1],
        z: info.cameraPos[2],
        duration: 1.2,
        ease: 'power2.out'
      });
      window.gsap.to(this.controls.target, {
        x: info.cameraTarget[0],
        y: info.cameraTarget[1],
        z: info.cameraTarget[2],
        duration: 1.2,
        ease: 'power2.out'
      });
    } else {
      this.camera.position.set(info.cameraPos[0], info.cameraPos[1], info.cameraPos[2]);
      this.controls.target.set(info.cameraTarget[0], info.cameraTarget[1], info.cameraTarget[2]);
    }

    this.highlightOrgan(organName);
  }

  highlightOrgan(organName, colorHex = null) {
    // Reset prior highlights
    this.organMeshes.forEach((name, mesh) => {
      if (mesh.userData.origMaterial) {
        mesh.material = mesh.userData.origMaterial.clone();
      }
    });

    const organInfo = ORGAN_DATA[organName];
    const highlightColor = colorHex !== null ? colorHex : (organInfo ? organInfo.color : 0x4fe0d3);

    this.organMeshes.forEach((name, mesh) => {
      if (name === organName) {
        mesh.material = new THREE.MeshStandardMaterial({
          color: highlightColor,
          emissive: highlightColor,
          emissiveIntensity: 0.55,
          roughness: 0.25,
          metalness: 0.2
        });
      }
    });
  }

  pulseCorrect(organName) {
    this.highlightOrgan(organName, 0x22c55e); // Bright emerald green
    setTimeout(() => {
      this.highlightOrgan(organName);
    }, 1500);
  }

  pulseError(organName) {
    this.highlightOrgan(organName, 0xf97316); // Orange warning
    setTimeout(() => {
      this.highlightOrgan(organName);
    }, 1200);
  }

  resetCamera() {
    if (window.gsap) {
      window.gsap.to(this.camera.position, { x: 0, y: 0.45, z: 1.4, duration: 1.0, ease: 'power2.out' });
      window.gsap.to(this.controls.target, { x: 0, y: 0.4, z: 0, duration: 1.0, ease: 'power2.out' });
    } else {
      this.camera.position.set(0, 0.45, 1.4);
      this.controls.target.set(0, 0.4, 0);
    }
  }

  toggleAutoRotate() {
    this.autoRotate = !this.autoRotate;
    this.controls.autoRotate = this.autoRotate;
    this.controls.autoRotateSpeed = 2.0;
    const label = document.getElementById('label-rotate');
    if (label) label.innerText = this.autoRotate ? 'Rotate: On' : 'Rotate: Off';
  }

  toggleSkinOpacity() {
    if (!this.skinMesh) return;
    this.isSkinGlass = !this.isSkinGlass;
    const targetOpacity = this.isSkinGlass ? 0.12 : 0.0;
    this.skinMesh.traverse((child) => {
      if (child.isMesh && child.material) {
        child.material.opacity = targetOpacity;
        child.visible = targetOpacity > 0;
      }
    });
    const label = document.getElementById('label-skin');
    if (label) label.innerText = this.isSkinGlass ? 'Skin: Glass' : 'Skin: Hidden';
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    if (this.controls) this.controls.update();
    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }
}

// ==========================================
// 4. MAIN HEALTH GAMES CONTROLLER
// ==========================================
class HealthGamesController {
  constructor() {
    this.audio = new SoundFX();
    this.engine = null;
    this.activeMode = 'game1'; // 'game1', 'game2', 'game3'

    // Player State
    this.score = parseInt(localStorage.getItem('games_score') || '0', 10);
    this.streak = 0;
    this.unlockedBadges = JSON.parse(localStorage.getItem('games_badges') || '[]');
    this.exploredOrgans = JSON.parse(localStorage.getItem('games_explored') || '[]');

    // Game 1 State
    this.game1Targets = Object.keys(ORGAN_DATA);
    this.game1Index = 0;
    this.game1Completed = new Set(JSON.parse(localStorage.getItem('game1_completed') || '[]'));

    // Game 2 State
    this.game2Questions = [...MEDICAL_TEST_QUESTIONS];
    this.game2Index = 0;

    // Game 3 State
    this.selectedCardOrgan = 'Liver';

    this.init();
  }

  init() {
    this.engine = new GameAnatomyEngine('game-canvas', 'viewport-container', (organ) => {
      this.handleOrganClick(organ);
    });

    this.updateHUD();
    this.renderGame1Checklist();
    this.loadGame1Question();
    this.renderGame2Question();
    this.renderGame3Buttons();
    this.renderGame3BodyCard('Liver');

    // Fetch progress from backend if available
    this.syncWithBackend();
  }

  // --- AUDIO & SETTINGS ---
  toggleSound() {
    this.audio.enabled = !this.audio.enabled;
    localStorage.setItem('games_sound', this.audio.enabled ? 'true' : 'false');
    const onIcon = document.getElementById('icon-sound-on');
    const offIcon = document.getElementById('icon-sound-off');
    if (this.audio.enabled) {
      onIcon.classList.remove('hidden');
      offIcon.classList.add('hidden');
      this.audio.playTone(600, 0.1);
    } else {
      onIcon.classList.add('hidden');
      offIcon.classList.remove('hidden');
    }
  }

  updateHUD() {
    const scoreEl = document.getElementById('game-score-display');
    if (scoreEl) scoreEl.innerText = `${this.score} Points`;

    // Level calculation: Tier 1 (0-150), Tier 2 (150-300), Tier 3 (300-500), Tier 4 (500+)
    let lvl = 1;
    let title = "Body Explorer";
    if (this.score >= 500) { lvl = 4; title = "Master Health Champion"; }
    else if (this.score >= 300) { lvl = 3; title = "Anatomy Specialist"; }
    else if (this.score >= 150) { lvl = 2; title = "Organ Investigator"; }

    const badgeEl = document.getElementById('game-level-badge');
    if (badgeEl) badgeEl.innerText = `L${lvl}`;

    const titleEl = document.getElementById('game-level-title');
    if (titleEl) titleEl.innerText = title;

    const streakEl = document.getElementById('canvas-hud-streak');
    if (streakEl) streakEl.innerText = `Streak: ${this.streak} 🔥`;

    localStorage.setItem('games_score', this.score.toString());
  }

  addScore(pts) {
    this.score += pts;
    this.updateHUD();
    this.checkBadges();
  }

  // --- MODE SWITCHING ---
  switchMode(mode) {
    this.activeMode = mode;
    this.audio.playClick();

    // Toggle Tab Buttons
    ['game1', 'game2', 'game3'].forEach((m) => {
      const tab = document.getElementById(`tab-${m}`);
      const panel = document.getElementById(`panel-${m}`);
      if (tab) {
        if (m === mode) {
          tab.classList.add('active', 'text-white');
          tab.classList.remove('text-[#B8C9DD]');
        } else {
          tab.classList.remove('active', 'text-white');
          tab.classList.add('text-[#B8C9DD]');
        }
      }
      if (panel) {
        if (m === mode) panel.classList.remove('hidden');
        else panel.classList.add('hidden');
      }
    });

    const hudTitle = document.getElementById('canvas-hud-mode-title');
    const hudPrompt = document.getElementById('canvas-hud-prompt');

    if (mode === 'game1') {
      if (hudTitle) hudTitle.innerText = "Game 1: Find the Organ";
      if (hudPrompt) hudPrompt.innerText = `Locate and click on the ${this.game1Targets[this.game1Index]}!`;
      this.engine.resetCamera();
    } else if (mode === 'game2') {
      if (hudTitle) hudTitle.innerText = "Game 2: Match the Test";
      const q = this.game2Questions[this.game2Index];
      if (hudPrompt) hudPrompt.innerText = `Match test: Where does ${q.testName} belong?`;
      this.engine.resetCamera();
    } else if (mode === 'game3') {
      if (hudTitle) hudTitle.innerText = "Game 3: Explore Your Body";
      if (hudPrompt) hudPrompt.innerText = "Click any organ to unlock its full anatomical guide card.";
      this.engine.zoomToOrgan(this.selectedCardOrgan);
    }
  }

  // --- 3D CANVAS ORGAN CLICK DISPATCHER ---
  handleOrganClick(organName) {
    this.audio.playClick();

    if (this.activeMode === 'game1') {
      this.verifyGame1Click(organName);
    } else if (this.activeMode === 'game2') {
      this.verifyGame2OrganChoice(organName);
    } else if (this.activeMode === 'game3') {
      this.renderGame3BodyCard(organName);
      this.engine.zoomToOrgan(organName);
    }
  }

  // ==========================================
  // GAME 1 LOGIC: FIND THE ORGAN
  // ==========================================
  loadGame1Question() {
    const targetOrgan = this.game1Targets[this.game1Index];
    const organInfo = ORGAN_DATA[targetOrgan];

    const roundBadge = document.getElementById('game1-round-badge');
    if (roundBadge) roundBadge.innerText = `Question ${this.game1Index + 1} of ${this.game1Targets.length}`;

    const heading = document.getElementById('game1-question-heading');
    if (heading) {
      heading.innerHTML = `Can you find the <span class="text-teal-300 underline decoration-teal-400/50 underline-offset-4">${targetOrgan}</span>?`;
    }

    const hint = document.getElementById('game1-question-hint');
    if (hint) {
      hint.innerText = `Hint: ${organInfo.hint}`;
    }

    const hudPrompt = document.getElementById('canvas-hud-prompt');
    if (hudPrompt && this.activeMode === 'game1') {
      hudPrompt.innerText = `Locate and click on the ${targetOrgan}!`;
    }

    const banner = document.getElementById('game1-feedback-banner');
    if (banner) banner.classList.add('hidden');
  }

  verifyGame1Click(clickedOrgan) {
    const targetOrgan = this.game1Targets[this.game1Index];
    const banner = document.getElementById('game1-feedback-banner');
    const iconEl = document.getElementById('game1-feedback-icon');
    const titleEl = document.getElementById('game1-feedback-title');
    const factEl = document.getElementById('game1-feedback-fact');

    if (clickedOrgan === targetOrgan) {
      // Correct!
      this.audio.playSuccess();
      this.engine.pulseCorrect(targetOrgan);
      this.streak++;
      this.addScore(50);

      this.game1Completed.add(targetOrgan);
      localStorage.setItem('game1_completed', JSON.stringify(Array.from(this.game1Completed)));
      this.renderGame1Checklist();

      if (banner) {
        banner.className = "p-4 rounded-2xl border border-emerald-500/50 bg-emerald-950/40 glow-success transition-all duration-300";
        if (iconEl) iconEl.innerText = "🎉";
        if (titleEl) {
          titleEl.className = "font-extrabold text-sm mb-1 text-emerald-300";
          titleEl.innerText = `Brilliant! That's the ${targetOrgan}! (+50 Points)`;
        }
        if (factEl) {
          factEl.innerText = ORGAN_DATA[targetOrgan].funFact;
        }
        banner.classList.remove('hidden');
      }

      // Sync challenge with backend
      this.postBackendChallenge('organ_recognition', { organ: targetOrgan, score: 50 });

    } else {
      // Incorrect - friendly retry
      this.audio.playError();
      this.engine.pulseError(clickedOrgan);
      this.streak = 0;
      this.updateHUD();

      if (banner) {
        banner.className = "p-4 rounded-2xl border border-amber-500/50 bg-amber-950/40 glow-alert transition-all duration-300";
        if (iconEl) iconEl.innerText = "🔍";
        if (titleEl) {
          titleEl.className = "font-extrabold text-sm mb-1 text-amber-300";
          titleEl.innerText = `That's the ${clickedOrgan}! Try again!`;
        }
        if (factEl) {
          factEl.innerText = `The ${targetOrgan} is located ${ORGAN_DATA[targetOrgan].hint.toLowerCase()}`;
        }
        banner.classList.remove('hidden');
      }
    }
  }

  nextGame1Target() {
    this.game1Index = (this.game1Index + 1) % this.game1Targets.length;
    this.loadGame1Question();
    this.engine.resetCamera();
  }

  skipGame1Target() {
    this.streak = 0;
    this.updateHUD();
    this.nextGame1Target();
  }

  renderGame1Checklist() {
    const container = document.getElementById('game1-organ-pills');
    if (!container) return;

    container.innerHTML = '';
    this.game1Targets.forEach((org) => {
      const isDone = this.game1Completed.has(org);
      const pill = document.createElement('button');
      pill.onclick = () => {
        this.game1Index = this.game1Targets.indexOf(org);
        this.loadGame1Question();
      };
      pill.className = `px-2 py-1 rounded-md text-[10px] font-bold transition-all ${
        isDone
          ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-600/60'
          : 'bg-[#162232] text-[#91A6BC] border border-slate-700 hover:text-white'
      }`;
      pill.innerText = `${isDone ? '✓ ' : ''}${org}`;
      container.appendChild(pill);
    });

    const ratioEl = document.getElementById('game1-completed-ratio');
    if (ratioEl) {
      ratioEl.innerText = `${this.game1Completed.size} / ${this.game1Targets.length} Mastered`;
    }
  }

  // ==========================================
  // GAME 2 LOGIC: MATCH THE MEDICAL TEST
  // ==========================================
  renderGame2Question() {
    const q = this.game2Questions[this.game2Index];

    const roundBadge = document.getElementById('game2-round-badge');
    if (roundBadge) roundBadge.innerText = `Test ${this.game2Index + 1} of ${this.game2Questions.length}`;

    const nameEl = document.getElementById('game2-biomarker-name');
    if (nameEl) nameEl.innerText = q.testName;

    const descEl = document.getElementById('game2-biomarker-desc');
    if (descEl) descEl.innerText = q.questionDesc;

    // Build 4 option buttons
    const container = document.getElementById('game2-options-container');
    if (container) {
      container.innerHTML = '';
      q.options.forEach((opt) => {
        const btn = document.createElement('button');
        btn.id = `btn-g2-${opt.toLowerCase().replace(/\s+/g, '-')}`;
        btn.onclick = () => this.verifyGame2Option(opt);
        btn.className = "w-full py-3 px-4 rounded-xl font-bold text-sm bg-[#162232] hover:bg-slate-700 text-[#F5F8FF] border border-slate-700/80 flex items-center justify-between transition-colors shadow-sm";
        btn.innerHTML = `
          <span>${opt}</span>
          <span class="text-xs text-[#91A6BC]">Select &rarr;</span>
        `;
        container.appendChild(btn);
      });
    }

    const expCard = document.getElementById('game2-explanation-card');
    if (expCard) expCard.classList.add('hidden');

    const nextBtn = document.getElementById('btn-game2-next');
    if (nextBtn) nextBtn.classList.add('hidden');
  }

  verifyGame2Option(selectedOrgan) {
    const q = this.game2Questions[this.game2Index];
    const expCard = document.getElementById('game2-explanation-card');
    const expText = document.getElementById('game2-explanation-text');
    const nextBtn = document.getElementById('btn-game2-next');

    if (selectedOrgan === q.correctOrgan) {
      // Correct!
      this.audio.playSuccess();
      this.addScore(25);
      this.streak++;
      this.updateHUD();

      // Zoom camera directly to organ in 3D!
      this.engine.zoomToOrgan(q.correctOrgan);
      this.engine.pulseCorrect(q.correctOrgan);

      // Highlight the correct button
      const optBtn = document.getElementById(`btn-g2-${selectedOrgan.toLowerCase().replace(/\s+/g, '-')}`);
      if (optBtn) {
        optBtn.className = "w-full py-3 px-4 rounded-xl font-bold text-sm bg-emerald-950/80 text-emerald-300 border border-emerald-500/80 flex items-center justify-between shadow-lg glow-success";
        optBtn.innerHTML = `<span>✓ ${selectedOrgan} (Correct!)</span><span class="text-xs font-mono">+25 XP</span>`;
      }

      // Reveal explanation card
      if (expCard && expText) {
        expText.innerText = q.explanation;
        expCard.classList.remove('hidden');
      }

      // Show Next button
      if (nextBtn) nextBtn.classList.remove('hidden');

      // Post quiz answer to backend
      this.postBackendQuiz(q.testName, selectedOrgan);

    } else {
      // Incorrect
      this.audio.playError();
      this.streak = 0;
      this.updateHUD();

      const optBtn = document.getElementById(`btn-g2-${selectedOrgan.toLowerCase().replace(/\s+/g, '-')}`);
      if (optBtn) {
        optBtn.className = "w-full py-3 px-4 rounded-xl font-bold text-sm bg-amber-950/60 text-amber-300 border border-amber-600/80 flex items-center justify-between";
        optBtn.innerHTML = `<span>✗ ${selectedOrgan}</span><span class="text-xs text-amber-400">Not here • Try another</span>`;
      }
    }
  }

  verifyGame2OrganChoice(organName) {
    const q = this.game2Questions[this.game2Index];
    if (q.options.includes(organName)) {
      this.verifyGame2Option(organName);
    }
  }

  nextGame2Question() {
    this.game2Index = (this.game2Index + 1) % this.game2Questions.length;
    this.renderGame2Question();
    this.engine.resetCamera();
  }

  // ==========================================
  // GAME 3 LOGIC: EXPLORE YOUR BODY
  // ==========================================
  renderGame3Buttons() {
    const container = document.getElementById('game3-organ-buttons');
    if (!container) return;

    container.innerHTML = '';
    Object.keys(ORGAN_DATA).forEach((org) => {
      const isExplored = this.exploredOrgans.includes(org);
      const btn = document.createElement('button');
      btn.onclick = () => {
        this.renderGame3BodyCard(org);
        this.engine.zoomToOrgan(org);
      };
      btn.className = `px-2.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 ${
        isExplored
          ? 'bg-teal-950/80 text-[#4FE0D3] border border-teal-500/50'
          : 'bg-[#162232] text-[#B8C9DD] border border-slate-700 hover:text-white'
      }`;
      btn.innerHTML = `${isExplored ? '<span class="text-teal-400">✓</span>' : ''}${org}`;
      container.appendChild(btn);
    });
  }

  renderGame3BodyCard(organName) {
    this.selectedCardOrgan = organName;
    const info = ORGAN_DATA[organName];
    if (!info) return;

    if (!this.exploredOrgans.includes(organName)) {
      this.exploredOrgans.push(organName);
      localStorage.setItem('games_explored', JSON.stringify(this.exploredOrgans));
      this.addScore(15);
      this.renderGame3Buttons();
    }

    const nameEl = document.getElementById('card-organ-name');
    if (nameEl) nameEl.innerText = info.name;

    const sysEl = document.getElementById('card-organ-system');
    if (sysEl) sysEl.innerText = info.system;

    const latinEl = document.getElementById('card-organ-latin');
    if (latinEl) latinEl.innerText = `${info.latin} • ${info.easyRole}`;

    const roleEl = document.getElementById('card-organ-role');
    if (roleEl) roleEl.innerText = info.role;

    const nutEl = document.getElementById('card-organ-nutrition');
    if (nutEl) nutEl.innerText = info.nutrition;

    const alcEl = document.getElementById('card-organ-alcohol');
    if (alcEl) alcEl.innerText = info.alcohol;

    const testsContainer = document.getElementById('card-organ-tests');
    if (testsContainer) {
      testsContainer.innerHTML = '';
      info.tests.forEach((t) => {
        const pill = document.createElement('span');
        pill.className = "px-2.5 py-1 rounded-lg bg-[#162232] text-xs text-[#B8C9DD] border border-slate-700/80 font-mono";
        pill.innerText = t;
        testsContainer.appendChild(pill);
      });
    }

    const badgesRatio = document.getElementById('game3-badges-ratio');
    if (badgesRatio) {
      badgesRatio.innerText = `🏆 Badges: ${this.unlockedBadges.length} / ${ACHIEVEMENTS_DATA.length}`;
    }
  }

  // --- ACHIEVEMENTS & MODAL ---
  checkBadges() {
    ACHIEVEMENTS_DATA.forEach((b) => {
      if (!this.unlockedBadges.includes(b.id)) {
        let earned = false;
        if (b.id === 'first_organ' && this.game1Completed.size >= 1) earned = true;
        if (b.id === 'organ_master' && this.game1Completed.size >= 10) earned = true;
        if (b.id === 'lab_detective' && this.score >= 100) earned = true;
        if (b.id === 'body_explorer' && this.exploredOrgans.length >= 10) earned = true;
        if (b.id === 'grand_champion' && this.score >= 400) earned = true;

        if (earned) {
          this.unlockedBadges.push(b.id);
          localStorage.setItem('games_badges', JSON.stringify(this.unlockedBadges));
          this.audio.playFanfare();
        }
      }
    });
  }

  openBadgesModal() {
    this.audio.playClick();
    const modal = document.getElementById('badges-modal');
    const list = document.getElementById('badges-list');
    if (!modal || !list) return;

    list.innerHTML = '';
    ACHIEVEMENTS_DATA.forEach((b) => {
      const isUnlocked = this.unlockedBadges.includes(b.id);
      const card = document.createElement('div');
      card.className = `p-3.5 rounded-2xl border flex items-center gap-3 ${
        isUnlocked
          ? 'bg-teal-950/40 border-teal-500/50 glow-teal'
          : 'bg-[#111c29] border-slate-800 opacity-60'
      }`;
      card.innerHTML = `
        <span class="text-2xl">${b.icon}</span>
        <div class="flex-1">
          <div class="flex items-center justify-between">
            <h5 class="text-xs font-bold text-white">${b.title}</h5>
            <span class="text-[10px] font-mono text-[#4FE0D3] font-bold">+${b.points} pts</span>
          </div>
          <p class="text-[11px] text-[#B8C9DD] leading-tight mt-0.5">${b.desc}</p>
          <span class="text-[9px] font-bold uppercase tracking-wider mt-1 block ${isUnlocked ? 'text-teal-400' : 'text-slate-500'}">
            ${isUnlocked ? '✓ Unlocked' : 'Locked'}
          </span>
        </div>
      `;
      list.appendChild(card);
    });

    modal.classList.remove('hidden');
  }

  closeBadgesModal() {
    this.audio.playClick();
    const modal = document.getElementById('badges-modal');
    if (modal) modal.classList.add('hidden');
  }

  resetProgress() {
    if (confirm('Are you sure you want to reset your game points, badges, and checklist?')) {
      localStorage.removeItem('games_score');
      localStorage.removeItem('games_badges');
      localStorage.removeItem('games_explored');
      localStorage.removeItem('game1_completed');
      location.reload();
    }
  }

  // --- BACKEND API SYNC ---
  async syncWithBackend() {
    try {
      const res = await fetch('/api/game/progress');
      if (res.ok) {
        const data = await res.json();
        if (data && data.total_xp && data.total_xp > this.score) {
          this.score = data.total_xp;
          this.updateHUD();
        }
      }
    } catch (e) {
      console.warn('Backend progress sync offline (using localStorage):', e);
    }
  }

  async postBackendChallenge(challengeId, payload) {
    try {
      await fetch('/api/game/challenge/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ challenge_id: challengeId, payload: payload })
      });
    } catch (e) {
      console.warn('Backend challenge log offline:', e);
    }
  }

  async postBackendQuiz(testName, selectedOrgan) {
    try {
      await fetch('/api/game/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quiz_id: 'match_test',
          question_id: testName,
          selected_option: 0
        })
      });
    } catch (e) {
      console.warn('Backend quiz submit offline:', e);
    }
  }

  resetCamera() {
    if (this.engine) this.engine.resetCamera();
  }

  toggleAutoRotate() {
    if (this.engine) this.engine.toggleAutoRotate();
  }

  toggleSkinOpacity() {
    if (this.engine) this.engine.toggleSkinOpacity();
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  window.HealthGames = new HealthGamesController();
});
