/**
 * NutriSphere Quest — Journey Inside the Human Body
 * Full AAA Educational 3D Game Engine & Health Progression System
 * 
 * Features:
 * - 3D Body World Map Engine with authentic glTF anatomical meshes
 * - Floating 3D-to-2D Organ Beacons tracking anatomical coordinates
 * - Built-in Web Audio API Sound Synthesizer (Chimes, fanfares, pulses)
 * - 7 Signature Educational Health Missions with interactive challenges:
 *   1. The Liver Lab (Metabolic roles & ALT/AST cell enzyme matching)
 *   2. The Heart Station (72 BPM pulsating heart & 5-step circulation challenge)
 *   3. Kidney Control Room (Nephron filtration & hydration workload simulator)
 *   4. The Digestive Journey (Mouth-to-ileum nutrient absorption puzzle)
 *   5. The Nutrition Challenge (Interactive Indian balanced plate builder)
 *   6. Alcohol & The Body (Clearance science, math calculator & myth buster)
 *   7. Signature Mission: The Medical Report Detective (Rohan Sharma case investigation)
 * - Professor 90-second automated interactive demonstration walkthrough
 * - Dynamic REST API sync with SQLite backend (/api/game/*)
 */

// ==========================================
// 1. WEB AUDIO API SOUND SYNTHESIZER
// ==========================================
class SoundFX {
  constructor() {
    this.ctx = null;
    this.enabled = localStorage.getItem('quest_sound') !== 'false';
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

  playTone(freq, duration = 0.1, type = 'sine', gainVal = 0.15) {
    if (!this.enabled) return;
    try {
      this.init();
      if (!this.ctx) return;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.warn('Audio tone error:', e);
    }
  }

  playClick() {
    this.playTone(880, 0.05, 'triangle', 0.1);
  }

  playSuccessChime() {
    if (!this.enabled) return;
    // Ascending arpeggio C5 -> E5 -> G5 -> C6
    const notes = [523.25, 659.25, 783.99, 1046.50];
    notes.forEach((freq, idx) => {
      setTimeout(() => this.playTone(freq, 0.22, 'sine', 0.18), idx * 70);
    });
  }

  playFanfare() {
    if (!this.enabled) return;
    // Celebration fanfare C5, G5, C6, E6, G6
    const notes = [523.25, 783.99, 1046.50, 1318.51, 1567.98];
    notes.forEach((freq, idx) => {
      setTimeout(() => this.playTone(freq, 0.35, 'triangle', 0.22), idx * 90);
    });
  }

  playError() {
    this.playTone(180, 0.25, 'sawtooth', 0.15);
  }

  playOrganHum() {
    this.playTone(330, 0.18, 'sine', 0.12);
  }

  toggle() {
    this.enabled = !this.enabled;
    localStorage.setItem('quest_sound', this.enabled ? 'true' : 'false');
    return this.enabled;
  }
}

// ==========================================
// 2. THREE.JS 3D BODY WORLD MAP ENGINE
// ==========================================
class Quest3DWorldMap {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.container = document.getElementById('quest-viewport');
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.organs = {};
    this.autoRotate = true;
    this.skinGlassMode = true;
    this.heartMesh = null;
    this.animFrameId = null;

    // 3D Anchor coordinates for dynamic beacon projection
    this.anchors = {
      liver: new THREE.Vector3(0.08, 0.24, 0.06),
      heart: new THREE.Vector3(-0.06, 0.38, 0.07),
      kidneys: new THREE.Vector3(0.00, 0.20, -0.06),
      stomach: new THREE.Vector3(-0.06, 0.26, 0.05),
      brain: new THREE.Vector3(0.00, 0.74, 0.03),
      report: new THREE.Vector3(0.24, 0.38, 0.12)
    };

    this.defaultCamPos = new THREE.Vector3(0, 0.35, 1.85);
    this.defaultCamTarget = new THREE.Vector3(0, 0.30, 0);

    this.init();
  }

  init() {
    if (!this.canvas) return;

    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.background = null; // transparent to show radial gradient

    // 2. Camera
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 50);
    this.camera.position.copy(this.defaultCamPos);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputEncoding = THREE.sRGBEncoding;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.25;

    // 4. Controls
    if (typeof THREE.OrbitControls !== 'undefined') {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.target.copy(this.defaultCamTarget);
      this.controls.minDistance = 0.4;
      this.controls.maxDistance = 3.5;
      this.controls.maxPolarAngle = Math.PI * 0.90;
      this.controls.minPolarAngle = Math.PI * 0.10;
      this.controls.autoRotate = this.autoRotate;
      this.controls.autoRotateSpeed = 0.8;
    }

    // 5. Lighting
    this.setupLighting();

    // 6. Load Anatomical Models
    this.loadModels();

    // 7. Event Listeners
    window.addEventListener('resize', () => this.onResize());

    // 8. Animation loop
    this.animate();
  }

  setupLighting() {
    // Ambient Light
    const amb = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(amb);

    // Directional Key Light (Teal clinical hue)
    const keyLight = new THREE.DirectionalLight(0x2dd4bf, 1.3);
    keyLight.position.set(2.5, 4, 3);
    this.scene.add(keyLight);

    // Fill Light (Warm white)
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.9);
    fillLight.position.set(-2.5, 2, 2.5);
    this.scene.add(fillLight);

    // Cyan Rim Light (Spatial computing depth)
    const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.1);
    rimLight.position.set(0, 3, -3.5);
    this.scene.add(rimLight);
  }

  loadModels() {
    const dracoLoader = (typeof THREE.DRACOLoader !== 'undefined') ? new THREE.DRACOLoader() : null;
    if (dracoLoader) {
      dracoLoader.setDecoderPath('/draco/gltf/');
    }

    const gltfLoader = (typeof THREE.GLTFLoader !== 'undefined') ? new THREE.GLTFLoader() : null;
    if (!gltfLoader) {
      console.warn('GLTFLoader not available; building high-fidelity fallback world map.');
      this.createFallbackWorldMap();
      return;
    }

    if (dracoLoader) {
      gltfLoader.setDRACOLoader(dracoLoader);
    }

    // Master manifest of real anatomical models
    const modelManifest = [
      { id: 'skeletal', path: '/models/anatria/skeletal_male.glb', color: 0xf1f5f9, opacity: 0.95 },
      { id: 'cardiovascular', path: '/models/anatria/cardiovascular_male.glb', color: 0xef4444, opacity: 1.0 },
      { id: 'respiratory', path: '/models/anatria/respiratory_male.glb', color: 0x0ea5e9, opacity: 0.9 },
      { id: 'digestive', path: '/models/anatria/digestive_male.glb', color: 0xf97316, opacity: 1.0 },
      { id: 'renal', path: '/models/anatria/renal_male.glb', color: 0xe11d48, opacity: 1.0 },
      { id: 'nervous', path: '/models/anatria/nervous_male.glb', color: 0xa855f7, opacity: 1.0 },
      { id: 'regional', path: '/models/anatria/regional_male.glb', color: 0x38bdf8, opacity: 0.12, isSkin: true }
    ];

    let loadedCount = 0;
    modelManifest.forEach((item) => {
      gltfLoader.load(
        item.path,
        (gltf) => {
          const model = gltf.scene;
          model.name = item.id;
          
          if (item.isSkin) {
            this.skinMesh = model;
          }

          model.traverse((child) => {
            if (child.isMesh) {
              const nameLower = (child.name || '').toLowerCase();
              if (nameLower.includes('heart') || nameLower.includes('ventricle') || nameLower.includes('atrium')) {
                this.heartMesh = child;
              }
              if (item.isSkin) {
                child.material = new THREE.MeshPhysicalMaterial({
                  color: item.color,
                  transparent: true,
                  opacity: 0.12,
                  roughness: 0.2,
                  metalness: 0.1,
                  transmission: 0.7,
                  ior: 1.4
                });
              }
            }
          });

          this.scene.add(model);
          loadedCount++;
        },
        undefined,
        (err) => {
          // If specific regional file fails, attempt loading single-file fallback
          if (item.id === 'skeletal' && loadedCount === 0) {
            this.loadSingleAssembly(gltfLoader);
          }
        }
      );
    });
  }

  loadSingleAssembly(loader) {
    loader.load('/models/human_body.glb', (gltf) => {
      this.scene.add(gltf.scene);
    }, undefined, () => {
      this.createFallbackWorldMap();
    });
  }

  createFallbackWorldMap() {
    // Beautiful stylized anatomical nodes if glTF meshes fail to load
    const group = new THREE.Group();

    // Body Core Capsule
    const torsoGeo = new THREE.CylinderGeometry(0.18, 0.16, 0.7, 32);
    const torsoMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.4,
      metalness: 0.2,
      transparent: true,
      opacity: 0.2
    });
    const torso = new THREE.Mesh(torsoGeo, torsoMat);
    torso.position.set(0, 0.35, 0);
    group.add(torso);

    // Heart Sphere
    const heartGeo = new THREE.DodecahedronGeometry(0.06, 2);
    const heartMat = new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.3 });
    this.heartMesh = new THREE.Mesh(heartGeo, heartMat);
    this.heartMesh.position.copy(this.anchors.heart);
    group.add(this.heartMesh);

    // Liver Mesh
    const liverGeo = new THREE.CylinderGeometry(0.08, 0.05, 0.08, 16);
    const liverMat = new THREE.MeshStandardMaterial({ color: 0xf97316, roughness: 0.3 });
    const liver = new THREE.Mesh(liverGeo, liverMat);
    liver.position.copy(this.anchors.liver);
    group.add(liver);

    // Kidneys
    const kidneyGeo = new THREE.SphereGeometry(0.04, 16, 16);
    const kidneyMat = new THREE.MeshStandardMaterial({ color: 0xe11d48, roughness: 0.3 });
    const kLeft = new THREE.Mesh(kidneyGeo, kidneyMat);
    kLeft.position.set(-0.06, 0.20, -0.04);
    const kRight = new THREE.Mesh(kidneyGeo, kidneyMat);
    kRight.position.set(0.06, 0.20, -0.04);
    group.add(kLeft);
    group.add(kRight);

    // Brain
    const brainGeo = new THREE.SphereGeometry(0.09, 24, 24);
    const brainMat = new THREE.MeshStandardMaterial({ color: 0xa855f7, roughness: 0.3 });
    const brain = new THREE.Mesh(brainGeo, brainMat);
    brain.position.copy(this.anchors.brain);
    group.add(brain);

    this.scene.add(group);
  }

  animate() {
    this.animFrameId = requestAnimationFrame(() => this.animate());

    // 72 BPM Pulsing Heart Animation
    if (this.heartMesh) {
      const pulse = 1.0 + 0.05 * Math.sin(Date.now() * 0.0075);
      this.heartMesh.scale.set(pulse, pulse, pulse);
    }

    if (this.controls) {
      this.controls.update();
    }

    // Dynamic 3D-to-2D Anchor Projections for Beacons
    this.updateBeacons();

    this.renderer.render(this.scene, this.camera);
  }

  updateBeacons() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;

    const beaconMap = [
      { id: 'beacon-liver', pos: this.anchors.liver },
      { id: 'beacon-heart', pos: this.anchors.heart },
      { id: 'beacon-kidneys', pos: this.anchors.kidneys },
      { id: 'beacon-stomach', pos: this.anchors.stomach },
      { id: 'beacon-brain', pos: this.anchors.brain },
      { id: 'beacon-report', pos: this.anchors.report }
    ];

    const tempV = new THREE.Vector3();

    beaconMap.forEach((b) => {
      const el = document.getElementById(b.id);
      if (!el) return;

      tempV.copy(b.pos);
      tempV.project(this.camera);

      // Hide if behind camera
      if (tempV.z > 1.0) {
        el.style.display = 'none';
        return;
      }

      el.style.display = 'flex';
      const x = (tempV.x * 0.5 + 0.5) * width;
      const y = (-(tempV.y * 0.5) + 0.5) * height;

      el.style.left = `${x}px`;
      el.style.top = `${y}px`;
    });
  }

  flyTo(pos, target, duration = 1.2) {
    if (typeof gsap === 'undefined') {
      this.camera.position.set(pos[0], pos[1], pos[2]);
      if (this.controls) this.controls.target.set(target[0], target[1], target[2]);
      return;
    }

    gsap.to(this.camera.position, {
      x: pos[0],
      y: pos[1],
      z: pos[2],
      duration: duration,
      ease: 'power2.inOut'
    });

    if (this.controls) {
      gsap.to(this.controls.target, {
        x: target[0],
        y: target[1],
        z: target[2],
        duration: duration,
        ease: 'power2.inOut'
      });
    }
  }

  resetView() {
    this.flyTo([this.defaultCamPos.x, this.defaultCamPos.y, this.defaultCamPos.z],
               [this.defaultCamTarget.x, this.defaultCamTarget.y, this.defaultCamTarget.z], 1.0);
  }

  toggleAutoRotate() {
    this.autoRotate = !this.autoRotate;
    if (this.controls) {
      this.controls.autoRotate = this.autoRotate;
    }
    const lbl = document.getElementById('label-auto-rotate');
    if (lbl) lbl.textContent = `Rotate: ${this.autoRotate ? 'On' : 'Off'}`;
    return this.autoRotate;
  }

  toggleSkin() {
    this.skinGlassMode = !this.skinGlassMode;
    if (this.skinMesh) {
      this.skinMesh.visible = this.skinGlassMode;
    }
    const lbl = document.getElementById('label-skin-transparency');
    if (lbl) lbl.textContent = `Skin: ${this.skinGlassMode ? 'Glass' : 'Hidden'}`;
  }

  onResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }
}

// ==========================================
// 3. QUEST APP & MISSION LOGIC CONTROLLER
// ==========================================
class NutriSphereQuestApp {
  constructor() {
    this.sound = new SoundFX();
    this.world3D = null;

    // Player state
    this.player = {
      user_id: 'usr_demo_001',
      xp: 120,
      level: 2,
      level_title: 'Body Explorer',
      current_mission: 'liver_lab',
      completed_missions_count: 1,
      next_level_xp: 250,
      xp_to_next_level: 130,
      completed_missions: ['liver_lab'],
      unlocked_achievements: []
    };

    this.missionsCatalog = [];
    this.achievementsCatalog = [];
    this.activeMission = null;
    this.activeStage = 'intro'; // 'intro', 'tests', 'challenge', 'quiz'

    // Interactive Mini-Challenges State
    this.plateState = {
      veggies: [],
      protein: [],
      grains: [],
      fats: []
    };

    this.circulationOrder = [];
    this.hydrationLevel = 75; // 75% optimal
    this.alcoholVolume = 330; // 330 mL
    this.alcoholABV = 5.0; // 5%

    // Detective case clues solved
    this.detectiveSolved = {
      alt: false,
      ldl: false,
      vitd: false,
      creat: false
    };

    // Professor 90-second Demo Tour State
    this.tour = {
      active: false,
      paused: false,
      step: 0,
      timer: null,
      progressTimer: null,
      elapsedMs: 0
    };
  }

  async init() {
    // 1. Initialize 3D World Map
    this.world3D = new Quest3DWorldMap('quest-canvas');

    // 2. Fetch Progress & Data from Backend
    await this.fetchPlayerProgress();
    await this.fetchMissions();
    await this.fetchAchievements();

    // 3. Update HUD Display
    this.updateHUD();

    // 4. Bind Global Keys
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeMissionModal();
        this.closeAchievementsModal();
      }
    });

    console.log('⚡ NutriSphere Quest Initialized. Player:', this.player.level_title, `${this.player.xp} XP`);
  }

  // --- API Sync ---
  async fetchPlayerProgress() {
    try {
      const res = await fetch('/api/game/progress');
      if (res.ok) {
        this.player = await res.json();
      }
    } catch (e) {
      console.warn('Using local player state:', e);
    }
  }

  async fetchMissions() {
    try {
      const res = await fetch('/api/game/missions');
      if (res.ok) {
        this.missionsCatalog = await res.json();
        this.renderMissionsStatus();
      }
    } catch (e) {
      console.warn('Failed to fetch missions:', e);
    }
  }

  async fetchAchievements() {
    try {
      const res = await fetch('/api/game/achievements');
      if (res.ok) {
        this.achievementsCatalog = await res.json();
      }
    } catch (e) {
      console.warn('Failed to fetch achievements:', e);
    }
  }

  updateHUD() {
    // Level Badge & Title
    const lvlBadge = document.getElementById('hud-level-badge');
    const lvlTitle = document.getElementById('hud-level-title');
    if (lvlBadge) lvlBadge.textContent = `L${this.player.level}`;
    if (lvlTitle) lvlTitle.textContent = this.player.level_title;

    // XP Progress Fill
    const xpText = document.getElementById('hud-xp-text');
    const xpFill = document.getElementById('hud-xp-fill');
    if (xpText) xpText.textContent = `${this.player.xp} / ${this.player.next_level_xp} XP`;
    
    if (xpFill) {
      const pct = Math.min(100, Math.round((this.player.xp / this.player.next_level_xp) * 100));
      xpFill.style.width = `${pct}%`;
    }

    // Missions Count
    const countEl = document.getElementById('hud-missions-count');
    if (countEl) countEl.textContent = `${this.player.completed_missions_count || this.player.completed_missions.length} / 7 Done`;

    // Ach modal cards
    const achLvlBadge = document.getElementById('ach-level-badge');
    const achLvlTitle = document.getElementById('ach-level-title');
    const achLvlXp = document.getElementById('ach-level-xp');
    if (achLvlBadge) achLvlBadge.textContent = `L${this.player.level}`;
    if (achLvlTitle) achLvlTitle.textContent = this.player.level_title;
    if (achLvlXp) achLvlXp.textContent = `${this.player.xp} / ${this.player.next_level_xp} XP (${this.player.xp_to_next_level} XP to Next Tier)`;
  }

  renderMissionsStatus() {
    this.missionsCatalog.forEach((m) => {
      const checkEl = document.getElementById(`badge-done-${m.id}`);
      if (checkEl) {
        if (m.completed || this.player.completed_missions.includes(m.id)) {
          checkEl.classList.remove('hidden');
        } else {
          checkEl.classList.add('hidden');
        }
      }
    });
  }

  // --- Sound FX Controls ---
  toggleSound() {
    const isEnabled = this.sound.toggle();
    const iconOn = document.getElementById('icon-sound-on');
    const iconOff = document.getElementById('icon-sound-off');
    if (iconOn && iconOff) {
      if (isEnabled) {
        iconOn.classList.remove('hidden');
        iconOff.classList.add('hidden');
        this.sound.playClick();
      } else {
        iconOn.classList.add('hidden');
        iconOff.classList.remove('hidden');
      }
    }
  }

  // --- 3D World Map Actions ---
  resetCameraView() {
    this.sound.playClick();
    this.world3D.resetView();
    const title = document.getElementById('viewport-organ-title');
    const sub = document.getElementById('viewport-organ-sub');
    if (title) title.textContent = 'THE HUMAN BODY WORLD MAP';
    if (sub) sub.textContent = 'Select any organ beacon or dock mission below';
  }

  toggleAutoRotate() {
    this.sound.playClick();
    this.world3D.toggleAutoRotate();
  }

  toggleSkinVisibility() {
    this.sound.playClick();
    this.world3D.toggleSkin();
  }

  // --- Mission System ---
  openMission(missionId) {
    this.sound.playOrganHum();

    // Focus camera onto the corresponding organ
    const organCamMap = {
      liver_lab: { pos: [0.12, 0.28, 0.65], target: [0.08, 0.24, 0.06], name: 'Liver' },
      heart_station: { pos: [-0.08, 0.42, 0.60], target: [-0.06, 0.38, 0.07], name: 'Heart' },
      kidney_room: { pos: [0.00, 0.24, -0.65], target: [0.00, 0.20, -0.06], name: 'Kidneys' },
      digestive_journey: { pos: [-0.08, 0.30, 0.70], target: [-0.06, 0.26, 0.05], name: 'Stomach & Intestines' },
      nutrition_plate: { pos: [0.00, 0.35, 1.10], target: [0.00, 0.30, 0.00], name: 'Whole Body Nutrition' },
      alcohol_journey: { pos: [0.00, 0.65, 0.65], target: [0.00, 0.50, 0.05], name: 'Brain & Liver Pathway' },
      report_detective: { pos: [0.15, 0.38, 0.85], target: [0.10, 0.35, 0.05], name: 'Diagnostic Lab Case' }
    };

    const targetInfo = organCamMap[missionId];
    if (targetInfo) {
      this.world3D.flyTo(targetInfo.pos, targetInfo.target, 1.2);
      const title = document.getElementById('viewport-organ-title');
      const sub = document.getElementById('viewport-organ-sub');
      if (title) title.textContent = `TARGET: ${targetInfo.name.toUpperCase()}`;
      if (sub) sub.textContent = 'Mission Briefing Loaded • Click Continue to explore';
    }

    const mission = this.missionsCatalog.find((m) => m.id === missionId) || {
      id: missionId,
      title: `Mission: ${missionId.replace('_', ' ').toUpperCase()}`,
      badge: 'Active Station',
      organ: targetInfo ? targetInfo.name : 'Human Organ',
      xp_reward: 100,
      description: 'Explore this organ, learn how tests work, and solve interactive health puzzles.'
    };

    this.activeMission = mission;

    // Populate Modal Header
    const mIcon = document.getElementById('modal-m-icon');
    const mTitle = document.getElementById('modal-m-title');
    const mBadge = document.getElementById('modal-m-badge');
    const mOrgan = document.getElementById('modal-m-organ');
    const mXp = document.getElementById('modal-m-xp');

    const icons = {
      liver_lab: '🧪',
      heart_station: '❤️',
      kidney_room: '💧',
      digestive_journey: '🥗',
      nutrition_plate: '🍽️',
      alcohol_journey: '🍷',
      report_detective: '🕵️'
    };

    if (mIcon) mIcon.textContent = icons[missionId] || '⚡';
    if (mTitle) mTitle.textContent = mission.title;
    if (mBadge) mBadge.textContent = mission.badge;
    if (mOrgan) mOrgan.textContent = `Organ: ${mission.organ}`;
    if (mXp) mXp.textContent = `+${mission.xp_reward} XP`;

    // Open Modal and render Stage 1
    const modal = document.getElementById('modal-mission');
    if (modal) modal.classList.remove('hidden');

    this.setModalStage('intro');
  }

  closeMissionModal() {
    this.sound.playClick();
    const modal = document.getElementById('modal-mission');
    if (modal) modal.classList.add('hidden');
    this.activeMission = null;
  }

  setModalStage(stage) {
    this.activeStage = stage;
    this.sound.playClick();

    // Tab buttons styling
    const tabs = ['intro', 'tests', 'challenge', 'quiz'];
    tabs.forEach((t) => {
      const btn = document.getElementById(`tab-btn-${t}`);
      if (btn) {
        if (t === stage) {
          btn.className = 'px-3 py-1.5 rounded-lg font-semibold bg-teal-500 text-slate-950 transition-all';
        } else {
          btn.className = 'px-3 py-1.5 rounded-lg font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition-all';
        }
      }
    });

    // Prev / Next button states
    const btnPrev = document.getElementById('btn-modal-prev');
    const btnNext = document.getElementById('btn-modal-next');
    if (btnPrev) {
      if (stage === 'intro') btnPrev.classList.add('hidden');
      else btnPrev.classList.remove('hidden');
    }

    if (btnNext) {
      if (stage === 'quiz') {
        btnNext.textContent = 'Finish Mission & Earn XP 🎉';
      } else {
        btnNext.textContent = 'Continue &rarr;';
      }
    }

    // Render Stage Content
    this.renderStageContent();
  }

  prevStage() {
    const sequence = ['intro', 'tests', 'challenge', 'quiz'];
    const idx = sequence.indexOf(this.activeStage);
    if (idx > 0) {
      this.setModalStage(sequence[idx - 1]);
    }
  }

  nextStage() {
    const sequence = ['intro', 'tests', 'challenge', 'quiz'];
    const idx = sequence.indexOf(this.activeStage);
    if (idx < sequence.length - 1) {
      this.setModalStage(sequence[idx + 1]);
    } else {
      // Completed all stages!
      this.finishCurrentMission();
    }
  }

  renderStageContent() {
    const container = document.getElementById('modal-stage-body');
    if (!container || !this.activeMission) return;

    const mId = this.activeMission.id;

    if (this.activeStage === 'intro') {
      container.innerHTML = this.getIntroHtml(mId);
    } else if (this.activeStage === 'tests') {
      container.innerHTML = this.getTestsHtml(mId);
    } else if (this.activeStage === 'challenge') {
      container.innerHTML = this.getChallengeHtml(mId);
      this.postRenderChallenge(mId);
    } else if (this.activeStage === 'quiz') {
      container.innerHTML = this.getQuizHtml(mId);
    }
  }

  // --- STAGE 1: INTRO & 4 ROLES ---
  getIntroHtml(mId) {
    const intros = {
      liver_lab: `
        <div class="space-y-4">
          <div class="bg-teal-950/40 p-4 rounded-xl border border-teal-500/30">
            <h3 class="text-base font-bold text-teal-300 mb-1">Welcome to the Liver Lab!</h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              Weighing about 1.5 kilograms, the liver is your body's second-largest organ and its busiest biochemical laboratory.
              It performs over 500 vital jobs every single day.
            </p>
          </div>

          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">The 4 Core Superpowers of Your Liver</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">🛡️</div>
              <div class="font-bold text-white text-xs">1. Master Detox Filter</div>
              <p class="text-[11px] text-slate-400 mt-1">Filters every drop of blood from your stomach and intestines, breaking down alcohol, medicines, and toxins into safe waste.</p>
            </div>
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">🧪</div>
              <div class="font-bold text-white text-xs">2. Bile Factory</div>
              <p class="text-[11px] text-slate-400 mt-1">Produces green bile fluid, which is stored in the gallbladder and breaks down fats in your food so your body can absorb vitamins A, D, E, and K.</p>
            </div>
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">🔋</div>
              <div class="font-bold text-white text-xs">3. Energy Storage Battery</div>
              <p class="text-[11px] text-slate-400 mt-1">Converts glucose from meals into glycogen. When you are busy or sleeping, it releases steady fuel so your blood sugar never crashes.</p>
            </div>
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">🏗️</div>
              <div class="font-bold text-white text-xs">4. Protein Construction</div>
              <p class="text-[11px] text-slate-400 mt-1">Manufactures essential blood proteins like Albumin (keeps fluid inside blood vessels) and clotting factors (stops bleeding when you get a cut).</p>
            </div>
          </div>
        </div>
      `,
      heart_station: `
        <div class="space-y-4">
          <div class="bg-rose-950/40 p-4 rounded-xl border border-rose-500/30">
            <h3 class="text-base font-bold text-rose-300 mb-1">Welcome to the Heart Station!</h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              Your heart beats approximately 100,000 times each day, pumping roughly 7,500 liters of blood through an 96,000-kilometer vascular network.
            </p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">🫀</div>
              <div class="font-bold text-white text-xs">The 4 Powerful Chambers</div>
              <p class="text-[11px] text-slate-400 mt-1">Two receiving atria on top, and two muscular pumping ventricles below working in synchronized rhythm.</p>
            </div>
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">⚡</div>
              <div class="font-bold text-white text-xs">Natural Pacemaker (SA Node)</div>
              <p class="text-[11px] text-slate-400 mt-1">Generates tiny electrical sparks that trigger muscle contraction ~72 times per minute at resting state.</p>
            </div>
          </div>
        </div>
      `,
      kidney_room: `
        <div class="space-y-4">
          <div class="bg-amber-950/40 p-4 rounded-xl border border-amber-500/30">
            <h3 class="text-base font-bold text-amber-300 mb-1">Welcome to Kidney Operations!</h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              Your two bean-shaped kidneys each house roughly 1,000,000 microscopic filtering units called nephrons. Together, they filter 180 liters of blood every 24 hours.
            </p>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">🔬</div>
              <div class="font-bold text-white text-xs">Nephron Micro-Filters</div>
              <p class="text-[11px] text-slate-400 mt-1">High-pressure glomeruli sift out urea, toxins, and surplus water while keeping precious blood cells and proteins inside your body.</p>
            </div>
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="text-xl mb-1">⚖️</div>
              <div class="font-bold text-white text-xs">Blood Pressure & Electrolytes</div>
              <p class="text-[11px] text-slate-400 mt-1">Precisely balances sodium, potassium, and acid levels to maintain healthy arterial blood pressure.</p>
            </div>
          </div>
        </div>
      `,
      digestive_journey: `
        <div class="space-y-4">
          <div class="bg-emerald-950/40 p-4 rounded-xl border border-emerald-500/30">
            <h3 class="text-base font-bold text-emerald-300 mb-1">The 9-Meter Enteric Highway!</h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              From mouth to colon, food travels an intricate 9-meter route, extracting micronutrients and fueling all 37 trillion cells in your body.
            </p>
          </div>
        </div>
      `,
      nutrition_plate: `
        <div class="space-y-4">
          <div class="bg-lime-950/40 p-4 rounded-xl border border-lime-500/30">
            <h3 class="text-base font-bold text-lime-300 mb-1">The Balanced Plate Challenge!</h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              Learn how to build a culturally authentic, fiber-rich Indian meal plate that keeps blood sugar steady and nourishes every organ.
            </p>
          </div>
        </div>
      `,
      alcohol_journey: `
        <div class="space-y-4">
          <div class="bg-purple-950/40 p-4 rounded-xl border border-purple-500/30">
            <h3 class="text-base font-bold text-purple-300 mb-1">Alcohol & Human Physiology</h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              Follow the journey of alcohol from stomach to brain and liver, and discover scientific facts about clearance rates without myths.
            </p>
          </div>
        </div>
      `,
      report_detective: `
        <div class="space-y-4">
          <div class="bg-amber-950/40 p-4 rounded-xl border border-amber-500/30">
            <h3 class="text-base font-bold text-amber-300 mb-1">Signature Case: Rohan Sharma (Age 34)</h3>
            <p class="text-xs text-slate-300 leading-relaxed">
              Put on your detective hat! Analyze real laboratory test findings, understand reference intervals, and match clues to organs in 3D.
            </p>
          </div>
        </div>
      `
    };

    return intros[mId] || intros.liver_lab;
  }

  // --- STAGE 2: UNDERSTAND THE TESTS ---
  getTestsHtml(mId) {
    const testExplanations = {
      liver_lab: `
        <div class="space-y-4">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">How Doctors Read Liver Tests in Plain English</h4>
          
          <div class="space-y-3">
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">ALT (SGPT) — "The Liver Cell Guard"</span>
                <span class="text-[10px] font-mono text-teal-400 bg-teal-950 px-2 py-0.5 rounded">Normal: 10–49 U/L</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                ALT is an enzyme that lives almost exclusively inside liver cells. When liver cells experience temporary stress (from medications, heavy meals, or alcohol), tiny amounts leak into the bloodstream. A mild elevation is an early warning flag, not a disease diagnosis.
              </p>
            </div>

            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">AST (SGOT) — "The Metabolic Workhorse"</span>
                <span class="text-[10px] font-mono text-teal-400 bg-teal-950 px-2 py-0.5 rounded">Normal: 10–34 U/L</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                Found in both liver cells and heart muscle. When doctors compare AST to ALT, they look at the ratio (AST/ALT) to understand whether the stress is from metabolic factors or recent exercise.
              </p>
            </div>

            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">Albumin — "The Protein Strength Score"</span>
                <span class="text-[10px] font-mono text-teal-400 bg-teal-950 px-2 py-0.5 rounded">Normal: 3.5–5.0 g/dL</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                The main protein made by the liver. When Albumin is normal, it proves the liver's manufacturing factories are strong and functioning smoothly.
              </p>
            </div>
          </div>
        </div>
      `,
      heart_station: `
        <div class="space-y-4">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Demystifying Cholesterol & Heart Tests</h4>
          <div class="space-y-3">
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">LDL — "The Delivery Trucks"</span>
                <span class="text-[10px] font-mono text-rose-400 bg-rose-950 px-2 py-0.5 rounded">Goal: &lt; 100 mg/dL</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                Transports cholesterol from the liver to cells that need it. If there are too many trucks on the road for too long, excess cargo can get stuck on arterial walls.
              </p>
            </div>
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">HDL — "The Cleanup Crew"</span>
                <span class="text-[10px] font-mono text-teal-400 bg-teal-950 px-2 py-0.5 rounded">Goal: &gt; 40 mg/dL</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                Picks up extra cholesterol from the arteries and returns it safely back to the liver for recycling or disposal. Higher HDL is protective!
              </p>
            </div>
          </div>
        </div>
      `,
      kidney_room: `
        <div class="space-y-4">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Kidney Function Tests Simplified</h4>
          <div class="space-y-3">
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">Creatinine — "The Muscle Filter Check"</span>
                <span class="text-[10px] font-mono text-amber-400 bg-amber-950 px-2 py-0.5 rounded">Normal: 0.70–1.30 mg/dL</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                A natural byproduct of everyday muscle use. Healthy kidneys filter it out into urine at a steady speed. If blood levels stay low and steady, your filters are clear.
              </p>
            </div>
            <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">eGFR — "The Speedometer Score"</span>
                <span class="text-[10px] font-mono text-teal-400 bg-teal-950 px-2 py-0.5 rounded">Healthy: &gt; 90 mL/min</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1.5 leading-relaxed">
                Calculates how many milliliters of blood your kidneys filter every minute. An eGFR above 90 indicates normal high-efficiency filtration.
              </p>
            </div>
          </div>
        </div>
      `
    };

    return testExplanations[mId] || testExplanations.liver_lab;
  }

  // --- STAGE 3: INTERACTIVE MINI-CHALLENGES ---
  getChallengeHtml(mId) {
    if (mId === 'nutrition_plate') {
      return `
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider">Build a Culturally Balanced Indian Meal Plate</h4>
            <span class="text-[10px] text-teal-400 font-mono">Click foods below to fill your plate</span>
          </div>

          <!-- The Plate Visualizer -->
          <div class="relative w-64 h-64 mx-auto rounded-full bg-slate-950 border-4 border-slate-700 shadow-2xl p-2 grid grid-cols-2 grid-rows-2 gap-1.5 overflow-hidden">
            <!-- Top Half: Vegetables & Salad (50%) -->
            <div id="plate-veggies" class="plate-quarter col-span-2 bg-emerald-950/70 border border-emerald-500/40 rounded-t-full p-2 flex flex-col items-center justify-center text-center">
              <span class="text-[10px] font-bold text-emerald-300">½ Vegetables & Greens</span>
              <span id="plate-veggies-items" class="text-[9px] text-slate-300 mt-0.5">Empty (Need 2+ choices)</span>
            </div>
            <!-- Bottom Left: Protein (25%) -->
            <div id="plate-protein" class="plate-quarter bg-amber-950/70 border border-amber-500/40 rounded-bl-full p-2 flex flex-col items-center justify-center text-center">
              <span class="text-[10px] font-bold text-amber-300">¼ Protein (Dal/Paneer)</span>
              <span id="plate-protein-items" class="text-[9px] text-slate-300 mt-0.5">Empty</span>
            </div>
            <!-- Bottom Right: Whole Grains (25%) -->
            <div id="plate-grains" class="plate-quarter bg-yellow-950/70 border border-yellow-500/40 rounded-br-full p-2 flex flex-col items-center justify-center text-center">
              <span class="text-[10px] font-bold text-yellow-300">¼ Whole Grains</span>
              <span id="plate-grains-items" class="text-[9px] text-slate-300 mt-0.5">Empty</span>
            </div>
          </div>

          <!-- Food Choices Buttons -->
          <div>
            <div class="text-[11px] font-semibold text-slate-400 mb-1.5">Vegetables & Salads (Click to add/remove):</div>
            <div class="flex flex-wrap gap-1.5">
              <button onclick="QuestApp.togglePlateItem('veggies', 'Palak Paneer Gravy')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-900 text-[11px] text-slate-300 border border-slate-700">Palak (Spinach)</button>
              <button onclick="QuestApp.togglePlateItem('veggies', 'Bhindi Masala')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-900 text-[11px] text-slate-300 border border-slate-700">Bhindi (Okra)</button>
              <button onclick="QuestApp.togglePlateItem('veggies', 'Cucumber Tomato Kachumber')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-900 text-[11px] text-slate-300 border border-slate-700">Kachumber Salad</button>
              <button onclick="QuestApp.togglePlateItem('veggies', 'Amla Mint Chutney')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-900 text-[11px] text-slate-300 border border-slate-700">Amla (Vit C)</button>
            </div>

            <div class="text-[11px] font-semibold text-slate-400 mt-2.5 mb-1.5">Proteins:</div>
            <div class="flex flex-wrap gap-1.5">
              <button onclick="QuestApp.togglePlateItem('protein', 'Dal Tadka')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-amber-900 text-[11px] text-slate-300 border border-slate-700">Moong Dal</button>
              <button onclick="QuestApp.togglePlateItem('protein', 'Chana Masala')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-amber-900 text-[11px] text-slate-300 border border-slate-700">Chana (Chickpeas)</button>
              <button onclick="QuestApp.togglePlateItem('protein', 'Paneer / Tofu Cubes')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-amber-900 text-[11px] text-slate-300 border border-slate-700">Paneer / Tofu</button>
              <button onclick="QuestApp.togglePlateItem('protein', 'Boiled Eggs')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-amber-900 text-[11px] text-slate-300 border border-slate-700">Boiled Eggs</button>
            </div>

            <div class="text-[11px] font-semibold text-slate-400 mt-2.5 mb-1.5">Whole Grains:</div>
            <div class="flex flex-wrap gap-1.5">
              <button onclick="QuestApp.togglePlateItem('grains', 'Multigrain Roti')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-yellow-900 text-[11px] text-slate-300 border border-slate-700">Multigrain Roti</button>
              <button onclick="QuestApp.togglePlateItem('grains', 'Brown Basmati Rice')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-yellow-900 text-[11px] text-slate-300 border border-slate-700">Brown Rice</button>
              <button onclick="QuestApp.togglePlateItem('grains', 'Millet Chapati')" class="plate-choice-btn px-2.5 py-1 rounded bg-slate-800 hover:bg-yellow-900 text-[11px] text-slate-300 border border-slate-700">Jowar/Bajra Roti</button>
            </div>
          </div>

          <!-- Balance Validation Banner -->
          <div id="plate-eval-banner" class="bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex items-center justify-between">
            <div>
              <div id="plate-eval-status" class="text-xs font-bold text-amber-400">Plate Incomplete</div>
              <div id="plate-eval-desc" class="text-[11px] text-slate-400">Add at least 1 vegetable, 1 protein, and 1 whole grain.</div>
            </div>
            <button id="btn-validate-plate" onclick="QuestApp.submitPlateChallenge()" class="px-3.5 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow disabled:opacity-50" disabled>
              Check Balance & Claim +50 XP
            </button>
          </div>
        </div>
      `;
    }

    if (mId === 'heart_station') {
      return `
        <div class="space-y-4">
          <div class="bg-rose-950/40 p-3.5 rounded-xl border border-rose-500/30">
            <h4 class="text-xs font-bold text-rose-300 mb-1">Circulation Sequence Challenge!</h4>
            <p class="text-[11px] text-slate-300">
              Click the 5 stages in order to trace a single drop of blood as it returns from your body, recharges with oxygen in the lungs, and gets pumped back out!
            </p>
          </div>

          <div class="space-y-2" id="circulation-step-list">
            <button onclick="QuestApp.stepCirculation('step1', this)" class="w-full text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition-colors flex items-center justify-between">
              <span>A. Used blood from body tissues arrives in the Right Atrium</span>
              <span class="step-badge text-[10px] text-slate-500 font-mono">Click to choose</span>
            </button>
            <button onclick="QuestApp.stepCirculation('step2', this)" class="w-full text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition-colors flex items-center justify-between">
              <span>B. Right Ventricle pumps blood to the Lungs for fresh Oxygen</span>
              <span class="step-badge text-[10px] text-slate-500 font-mono">Click to choose</span>
            </button>
            <button onclick="QuestApp.stepCirculation('step3', this)" class="w-full text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition-colors flex items-center justify-between">
              <span>C. Oxygen-rich blood returns into the Left Atrium</span>
              <span class="step-badge text-[10px] text-slate-500 font-mono">Click to choose</span>
            </button>
            <button onclick="QuestApp.stepCirculation('step4', this)" class="w-full text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition-colors flex items-center justify-between">
              <span>D. Muscular Left Ventricle contracts with high pressure</span>
              <span class="step-badge text-[10px] text-slate-500 font-mono">Click to choose</span>
            </button>
            <button onclick="QuestApp.stepCirculation('step5', this)" class="w-full text-left p-3 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-800 text-xs text-slate-200 transition-colors flex items-center justify-between">
              <span>E. Aorta distributes oxygenated blood to Brain, Muscles, and Organs</span>
              <span class="step-badge text-[10px] text-slate-500 font-mono">Click to choose</span>
            </button>
          </div>

          <div id="circ-feedback" class="text-xs text-teal-400 font-mono text-center"></div>
        </div>
      `;
    }

    if (mId === 'kidney_room') {
      return `
        <div class="space-y-4">
          <div class="bg-amber-950/40 p-3.5 rounded-xl border border-amber-500/30">
            <h4 class="text-xs font-bold text-amber-300 mb-1">Nephron Hydration Workload Simulator</h4>
            <p class="text-[11px] text-slate-300">
              Drag the hydration slider to see how water intake directly influences renal filtration efficiency and urine concentration.
            </p>
          </div>

          <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-4">
            <div>
              <div class="flex justify-between items-center text-xs font-bold text-white mb-2">
                <span>Daily Hydration Level:</span>
                <span id="hyd-val-text" class="text-teal-400 font-mono">2.5 Liters (Optimal)</span>
              </div>
              <input type="range" min="1" max="5" step="0.5" value="2.5" oninput="QuestApp.onHydrationSlider(this.value)" class="w-full accent-teal-400 cursor-pointer">
              <div class="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                <span>1.0 L (Dehydrated)</span>
                <span>2.5 L (Healthy Target)</span>
                <span>5.0 L (High Intake)</span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800">
              <div>
                <div class="text-[10px] text-slate-400 font-medium">Urine Color / Concentration:</div>
                <div id="hyd-color-box" class="h-8 rounded-lg mt-1 bg-amber-400/80 border border-amber-300/40 flex items-center justify-center text-slate-950 font-bold text-xs transition-colors">
                  Pale Straw (Normal)
                </div>
              </div>
              <div>
                <div class="text-[10px] text-slate-400 font-medium">Glomerular Workload:</div>
                <div id="hyd-workload-box" class="h-8 rounded-lg mt-1 bg-teal-950 border border-teal-500/40 flex items-center justify-center text-teal-300 font-bold text-xs">
                  Smooth & Optimal
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    if (mId === 'alcohol_journey') {
      return `
        <div class="space-y-4">
          <div class="bg-purple-950/40 p-3.5 rounded-xl border border-purple-500/30">
            <h4 class="text-xs font-bold text-purple-300 mb-1">Scientific Pure Ethanol Intake Calculator</h4>
            <p class="text-[11px] text-slate-300">
              Exact scientific formula: Volume (mL) × (ABV% / 100) × 0.789 = Pure Ethanol (grams)
            </p>
          </div>

          <div class="bg-slate-950/80 p-4 rounded-xl border border-slate-800 space-y-4">
            <div>
              <div class="flex justify-between items-center text-xs font-bold text-white mb-1.5">
                <span>Beverage Volume:</span>
                <span id="alc-vol-text" class="text-purple-300 font-mono">330 mL (Standard Bottle)</span>
              </div>
              <input type="range" min="30" max="750" step="10" value="330" oninput="QuestApp.onAlcoholSlider(this.value, null)" class="w-full accent-purple-400 cursor-pointer">
            </div>

            <div>
              <div class="flex justify-between items-center text-xs font-bold text-white mb-1.5">
                <span>Alcohol By Volume (ABV):</span>
                <span id="alc-abv-text" class="text-purple-300 font-mono">5.0% (Lager)</span>
              </div>
              <input type="range" min="1" max="45" step="0.5" value="5.0" oninput="QuestApp.onAlcoholSlider(null, this.value)" class="w-full accent-purple-400 cursor-pointer">
            </div>

            <div class="bg-purple-950/40 p-3 rounded-xl border border-purple-800/40 flex items-center justify-between">
              <div>
                <div class="text-[11px] text-slate-400">Pure Alcohol Load:</div>
                <div id="alc-grams-text" class="text-base font-black text-white font-mono">13.0 grams of ethanol</div>
              </div>
              <div class="text-right">
                <div class="text-[10px] text-slate-400">Est. Liver Clearance Time:</div>
                <div id="alc-hours-text" class="text-xs font-bold text-purple-300 font-mono">~1.5 to 1.8 Hours</div>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    if (mId === 'report_detective') {
      return `
        <div class="space-y-4">
          <div class="bg-amber-950/40 p-3.5 rounded-xl border border-amber-500/30">
            <h4 class="text-xs font-bold text-amber-300 mb-1">Detective Case Clues: Patient Rohan Sharma</h4>
            <p class="text-[11px] text-slate-300">
              Investigate the 4 clue cards below. Match each lab finding to its organ and explain what it means.
            </p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div id="clue-alt" class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">Clue 1: ALT (SGPT) = 58 U/L</span>
                <span class="text-[10px] text-amber-400 font-mono">Ref: 10–49 U/L</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Mildly elevated liver enzyme.</p>
              <button onclick="QuestApp.solveClue('alt')" class="mt-2.5 w-full py-1.5 rounded bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 text-[11px] font-bold border border-teal-500/40">
                Match to Liver & Understand &rarr;
              </button>
            </div>

            <div id="clue-ldl" class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">Clue 2: LDL-C = 142 mg/dL</span>
                <span class="text-[10px] text-rose-400 font-mono">Goal: &lt; 100 mg/dL</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Atherogenic lipid particle count.</p>
              <button onclick="QuestApp.solveClue('ldl')" class="mt-2.5 w-full py-1.5 rounded bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 text-[11px] font-bold border border-rose-500/40">
                Match to Heart & Understand &rarr;
              </button>
            </div>

            <div id="clue-vitd" class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">Clue 3: Vitamin D = 22.4 ng/mL</span>
                <span class="text-[10px] text-amber-400 font-mono">Healthy: 30–100 ng/mL</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Bone mineral absorption cofactor.</p>
              <button onclick="QuestApp.solveClue('vitd')" class="mt-2.5 w-full py-1.5 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-[11px] font-bold border border-amber-500/40">
                Match to Spine & Bones &rarr;
              </button>
            </div>

            <div id="clue-creat" class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800">
              <div class="flex justify-between items-center">
                <span class="font-bold text-white text-xs">Clue 4: Creatinine = 1.05 mg/dL</span>
                <span class="text-[10px] text-teal-400 font-mono">Normal: 0.70–1.30 mg/dL</span>
              </div>
              <p class="text-[11px] text-slate-400 mt-1">Renal glomerular filtration index.</p>
              <button onclick="QuestApp.solveClue('creat')" class="mt-2.5 w-full py-1.5 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-[11px] font-bold border border-emerald-500/40">
                Match to Kidneys & Confirm &rarr;
              </button>
            </div>
          </div>
        </div>
      `;
    }

    // Default challenge
    return `
      <div class="space-y-4">
        <div class="bg-teal-950/40 p-4 rounded-xl border border-teal-500/30">
          <h4 class="text-xs font-bold text-teal-300 mb-1">Organ Exploration Challenge</h4>
          <p class="text-xs text-slate-300 leading-relaxed">
            Rotate the 3D model in the background, locate the ${this.activeMission.organ}, and verify its anatomical relationship to surrounding structures.
          </p>
        </div>
        <button onclick="QuestApp.claimExplorationXP()" class="w-full py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs shadow-lg shadow-teal-500/20">
          I Have Explored the Organ in 3D (+50 XP)
        </button>
      </div>
    `;
  }

  postRenderChallenge(mId) {
    if (mId === 'nutrition_plate') {
      this.updatePlateUI();
    }
  }

  // --- STAGE 4: QUIZ ---
  getQuizHtml(mId) {
    const questions = (this.activeMission && this.activeMission.questions) || [];
    if (!questions.length) {
      return `
        <div class="text-center py-8">
          <div class="text-3xl mb-2">🎉</div>
          <div class="text-sm font-bold text-white">All Stage Challenges Completed!</div>
          <div class="text-xs text-slate-400 mt-1">Click the button below to record your mission victory.</div>
        </div>
      `;
    }

    let qHtml = '<div class="space-y-5">';
    questions.forEach((q, qIdx) => {
      qHtml += `
        <div class="bg-slate-950/70 p-4 rounded-xl border border-slate-800 space-y-3" id="qcard-${q.id}">
          <div class="flex items-start gap-2">
            <span class="w-5 h-5 rounded-full bg-teal-500/20 text-teal-300 text-xs flex items-center justify-center font-bold shrink-0 mt-0.5">
              ${qIdx + 1}
            </span>
            <div class="font-bold text-white text-xs leading-snug">${q.question}</div>
          </div>

          <div class="space-y-1.5 pl-7">
            ${q.options.map((opt, oIdx) => `
              <button onclick="QuestApp.answerQuiz('${mId}', '${q.id}', ${oIdx}, this)" class="quiz-opt-btn w-full text-left p-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 transition-colors">
                ${String.fromCharCode(65 + oIdx)}. ${opt}
              </button>
            `).join('')}
          </div>

          <div id="qfeed-${q.id}" class="hidden text-xs pl-7 pt-2 border-t border-slate-800/80"></div>
        </div>
      `;
    });
    qHtml += '</div>';
    return qHtml;
  }

  async answerQuiz(quizId, questionId, selectedOption, btnEl) {
    this.sound.playClick();

    const parent = btnEl.closest('.space-y-1.5');
    if (!parent) return;

    // Disable all options in this question
    parent.querySelectorAll('button').forEach(b => b.disabled = true);

    try {
      const res = await fetch('/api/game/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          quiz_id: quizId,
          question_id: questionId,
          selected_option: selectedOption
        })
      });

      if (!res.ok) throw new Error('Quiz submit failed');
      const data = await res.json();

      const feedEl = document.getElementById(`qfeed-${questionId}`);
      if (feedEl) {
        feedEl.classList.remove('hidden');
        if (data.is_correct) {
          this.sound.playSuccessChime();
          btnEl.className = 'quiz-opt-btn w-full text-left p-2.5 rounded-lg bg-teal-950 border border-teal-500 text-xs text-teal-200 font-bold';
          feedEl.innerHTML = `
            <div class="text-teal-400 font-bold flex items-center gap-1.5 mb-1">
              <span>✓ Correct! +10 XP</span>
            </div>
            <div class="text-slate-300 leading-relaxed">${data.explanation}</div>
          `;
        } else {
          this.sound.playError();
          btnEl.className = 'quiz-opt-btn w-full text-left p-2.5 rounded-lg bg-rose-950 border border-rose-500 text-xs text-rose-200';
          feedEl.innerHTML = `
            <div class="text-rose-400 font-bold flex items-center gap-1.5 mb-1">
              <span>✕ Review the explanation below:</span>
            </div>
            <div class="text-slate-300 leading-relaxed">${data.explanation}</div>
          `;
        }
      }

      // Update XP in HUD
      if (data.total_xp) {
        this.player.xp = data.total_xp;
        this.updateHUD();
      }

    } catch (e) {
      console.warn('Quiz submit error:', e);
    }
  }

  async finishCurrentMission() {
    if (!this.activeMission) return;
    const mId = this.activeMission.id;

    try {
      const res = await fetch('/api/game/mission/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mission_id: mId, score: 100 })
      });

      if (res.ok) {
        const out = await res.json();
        this.player.xp = out.total_xp;
        this.player.level = out.level;
        this.player.level_title = out.level_title;
        if (!this.player.completed_missions.includes(mId)) {
          this.player.completed_missions.push(mId);
          this.player.completed_missions_count = this.player.completed_missions.length;
        }

        this.sound.playFanfare();
        this.showCelebrationToast(
          out.level_up ? `Level Up! ${out.level_title}` : 'Mission Accomplished!',
          out.message
        );
        this.updateHUD();
        this.renderMissionsStatus();
      }
    } catch (e) {
      console.warn('Mission complete error:', e);
    }

    this.closeMissionModal();
  }

  showCelebrationToast(title, msg) {
    const toast = document.getElementById('toast-celebration');
    const tTitle = document.getElementById('toast-title');
    const tMsg = document.getElementById('toast-msg');

    if (toast && tTitle && tMsg) {
      tTitle.textContent = title;
      tMsg.textContent = msg;
      toast.classList.remove('hidden');
      setTimeout(() => {
        toast.classList.add('hidden');
      }, 5000);
    }
  }

  // --- Interactive Mini-Challenges Logic ---
  togglePlateItem(category, item) {
    this.sound.playClick();
    const arr = this.plateState[category];
    const idx = arr.indexOf(item);
    if (idx >= 0) {
      arr.splice(idx, 1);
    } else {
      arr.push(item);
    }
    this.updatePlateUI();
  }

  updatePlateUI() {
    const vEl = document.getElementById('plate-veggies-items');
    const pEl = document.getElementById('plate-protein-items');
    const gEl = document.getElementById('plate-grains-items');

    if (vEl) vEl.textContent = this.plateState.veggies.length ? this.plateState.veggies.join(', ') : 'Empty';
    if (pEl) pEl.textContent = this.plateState.protein.length ? this.plateState.protein.join(', ') : 'Empty';
    if (gEl) gEl.textContent = this.plateState.grains.length ? this.plateState.grains.join(', ') : 'Empty';

    const hasVeggies = this.plateState.veggies.length >= 1;
    const hasProtein = this.plateState.protein.length >= 1;
    const hasGrains = this.plateState.grains.length >= 1;

    const isComplete = hasVeggies && hasProtein && hasGrains;
    const btn = document.getElementById('btn-validate-plate');
    const status = document.getElementById('plate-eval-status');
    const desc = document.getElementById('plate-eval-desc');

    if (btn) btn.disabled = !isComplete;

    if (status && desc) {
      if (isComplete) {
        status.textContent = 'Plate is Well Balanced!';
        status.className = 'text-xs font-bold text-teal-400';
        desc.textContent = 'Excellent! You have steady fiber from greens, cellular building blocks from protein, and sustained fuel from whole grains.';
      } else {
        status.textContent = 'Plate Incomplete';
        status.className = 'text-xs font-bold text-amber-400';
        desc.textContent = 'Add at least 1 vegetable, 1 protein, and 1 whole grain to balance your plate.';
      }
    }
  }

  async submitPlateChallenge() {
    this.sound.playSuccessChime();
    try {
      const res = await fetch('/api/game/challenge/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_id: 'nutrition_plate_balance',
          data: this.plateState
        })
      });
      if (res.ok) {
        const out = await res.json();
        this.player.xp = out.total_xp;
        this.updateHUD();
        this.showCelebrationToast('Balanced Plate Mastered!', '+50 XP awarded for crafting a culturally balanced Indian meal!');
      }
    } catch (e) {
      console.warn('Challenge submit error:', e);
    }
  }

  stepCirculation(step, btn) {
    this.sound.playClick();
    this.circulationOrder.push(step);
    btn.classList.add('bg-teal-950', 'border-teal-500');
    const badge = btn.querySelector('.step-badge');
    if (badge) {
      badge.textContent = `Selected #${this.circulationOrder.length}`;
      badge.className = 'step-badge text-[10px] text-teal-300 font-mono font-bold';
    }

    if (this.circulationOrder.length === 5) {
      const correct = JSON.stringify(this.circulationOrder) === JSON.stringify(['step1', 'step2', 'step3', 'step4', 'step5']);
      const feed = document.getElementById('circ-feedback');
      if (feed) {
        if (correct) {
          this.sound.playSuccessChime();
          feed.textContent = '✓ Perfect Cardiovascular Route! Blood circulation loop validated (+50 XP).';
          feed.className = 'text-xs text-teal-400 font-mono text-center font-bold';
        } else {
          this.sound.playError();
          feed.textContent = 'Circulation sequence out of order. Resetting steps to try again...';
          feed.className = 'text-xs text-rose-400 font-mono text-center font-bold';
          setTimeout(() => {
            this.circulationOrder = [];
            document.querySelectorAll('#circulation-step-list button').forEach((b) => {
              b.classList.remove('bg-teal-950', 'border-teal-500');
              const s = b.querySelector('.step-badge');
              if (s) {
                s.textContent = 'Click to choose';
                s.className = 'step-badge text-[10px] text-slate-500 font-mono';
              }
            });
            feed.textContent = '';
          }, 1500);
        }
      }
    }
  }

  onHydrationSlider(val) {
    this.hydrationLevel = parseFloat(val);
    const text = document.getElementById('hyd-val-text');
    const colorBox = document.getElementById('hyd-color-box');
    const workBox = document.getElementById('hyd-workload-box');

    if (!text || !colorBox || !workBox) return;

    if (val <= 1.5) {
      text.textContent = `${val} Liters (Dehydrated)`;
      text.className = 'text-amber-400 font-mono';
      colorBox.textContent = 'Dark Amber (Concentrated)';
      colorBox.className = 'h-8 rounded-lg mt-1 bg-amber-600 border border-amber-400 flex items-center justify-center text-slate-950 font-bold text-xs';
      workBox.textContent = 'High Glomerular Stress';
      workBox.className = 'h-8 rounded-lg mt-1 bg-rose-950 border border-rose-500/40 flex items-center justify-center text-rose-300 font-bold text-xs';
    } else if (val <= 3.5) {
      text.textContent = `${val} Liters (Optimal)`;
      text.className = 'text-teal-400 font-mono';
      colorBox.textContent = 'Pale Straw (Healthy)';
      colorBox.className = 'h-8 rounded-lg mt-1 bg-yellow-200 border border-yellow-300 flex items-center justify-center text-slate-950 font-bold text-xs';
      workBox.textContent = 'Smooth & Optimal';
      workBox.className = 'h-8 rounded-lg mt-1 bg-teal-950 border border-teal-500/40 flex items-center justify-center text-teal-300 font-bold text-xs';
    } else {
      text.textContent = `${val} Liters (High Volume)`;
      text.className = 'text-cyan-400 font-mono';
      colorBox.textContent = 'Completely Clear';
      colorBox.className = 'h-8 rounded-lg mt-1 bg-cyan-100 border border-cyan-200 flex items-center justify-center text-slate-950 font-bold text-xs';
      workBox.textContent = 'High Water Dilution';
      workBox.className = 'h-8 rounded-lg mt-1 bg-slate-900 border border-slate-700 flex items-center justify-center text-cyan-300 font-bold text-xs';
    }
  }

  onAlcoholSlider(vol, abv) {
    if (vol !== null) this.alcoholVolume = parseFloat(vol);
    if (abv !== null) this.alcoholABV = parseFloat(abv);

    const grams = (this.alcoholVolume * (this.alcoholABV / 100) * 0.789).toFixed(1);
    const clearanceHours = (grams / 8.5).toFixed(1); // average clearance ~8.5g/hr

    const volText = document.getElementById('alc-vol-text');
    const abvText = document.getElementById('alc-abv-text');
    const gramsText = document.getElementById('alc-grams-text');
    const hoursText = document.getElementById('alc-hours-text');

    if (volText) volText.textContent = `${this.alcoholVolume} mL`;
    if (abvText) abvText.textContent = `${this.alcoholABV}%`;
    if (gramsText) gramsText.textContent = `${grams} grams of ethanol`;
    if (hoursText) hoursText.textContent = `~${clearanceHours} Hours`;
  }

  solveClue(type) {
    this.sound.playSuccessChime();
    this.detectiveSolved[type] = true;
    const card = document.getElementById(`clue-${type}`);
    if (card) {
      card.className = 'bg-teal-950/60 p-3.5 rounded-xl border border-teal-500/60 transition-all';
      const btn = card.querySelector('button');
      if (btn) {
        btn.textContent = '✓ Matched to Organ & Explained';
        btn.className = 'mt-2.5 w-full py-1.5 rounded bg-teal-500 text-slate-950 text-[11px] font-black';
      }
    }

    const allSolved = Object.values(this.detectiveSolved).every(Boolean);
    if (allSolved) {
      this.sound.playFanfare();
      this.showCelebrationToast('Report Detective Solved!', 'You decoded all 4 clues and matched them to organs in 3D (+150 XP)!');
    }
  }

  async claimExplorationXP() {
    this.sound.playSuccessChime();
    try {
      const res = await fetch('/api/game/challenge/complete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          challenge_id: 'organ_explorer',
          data: { organ: this.activeMission.organ }
        })
      });
      if (res.ok) {
        const out = await res.json();
        this.player.xp = out.total_xp;
        this.updateHUD();
        this.showCelebrationToast('Organ Explored!', '+50 XP awarded for 3D anatomical examination!');
      }
    } catch (e) {
      console.warn('Challenge submit error:', e);
    }
  }

  // --- Achievements & Reset ---
  openAchievementsModal() {
    this.sound.playClick();
    const modal = document.getElementById('modal-achievements');
    const grid = document.getElementById('achievements-grid');

    if (grid) {
      grid.innerHTML = this.achievementsCatalog.map((ach) => `
        <div class="p-3 rounded-xl border flex items-center gap-3 ${ach.unlocked ? 'bg-teal-950/40 border-teal-500/40' : 'bg-slate-950/40 border-slate-800 opacity-60'}">
          <div class="text-2xl">${ach.icon}</div>
          <div>
            <div class="text-xs font-bold ${ach.unlocked ? 'text-teal-300' : 'text-slate-400'} flex items-center gap-1.5">
              <span>${ach.title}</span>
              ${ach.unlocked ? '<span class="text-[10px] bg-teal-500/20 text-teal-300 px-1.5 rounded font-mono font-bold">UNLOCKED</span>' : '<span class="text-[10px] text-slate-500 font-mono">LOCKED</span>'}
            </div>
            <div class="text-[11px] text-slate-400 mt-0.5">${ach.description}</div>
          </div>
        </div>
      `).join('');
    }

    if (modal) modal.classList.remove('hidden');
  }

  closeAchievementsModal() {
    this.sound.playClick();
    const modal = document.getElementById('modal-achievements');
    if (modal) modal.classList.add('hidden');
  }

  async resetDemoProgress() {
    this.sound.playClick();
    try {
      const res = await fetch('/api/game/reset', { method: 'POST' });
      if (res.ok) {
        this.player = await res.json();
        await this.fetchMissions();
        await this.fetchAchievements();
        this.updateHUD();
        this.renderMissionsStatus();
        this.openAchievementsModal();
        this.showCelebrationToast('Progress Reset', 'Game state cleared for a fresh academic demonstration.');
      }
    } catch (e) {
      console.warn('Reset error:', e);
    }
  }

  // ==========================================
  // 4. PROFESSOR 90-SECOND DEMO TOUR RUNNER
  // ==========================================
  startPresentationTour() {
    this.sound.playFanfare();
    this.closeMissionModal();
    this.closeAchievementsModal();

    this.tour.active = true;
    this.tour.paused = false;
    this.tour.step = 0;
    this.tour.elapsedMs = 0;

    const bar = document.getElementById('tour-control-bar');
    if (bar) bar.classList.remove('hidden');

    this.runTourStep(0);
  }

  stopPresentationTour() {
    this.sound.playClick();
    this.tour.active = false;
    clearTimeout(this.tour.timer);
    clearInterval(this.tour.progressTimer);

    const bar = document.getElementById('tour-control-bar');
    if (bar) bar.classList.add('hidden');

    this.resetCameraView();
  }

  toggleTourPause() {
    this.sound.playClick();
    this.tour.paused = !this.tour.paused;
    const btn = document.getElementById('btn-tour-pause');
    if (btn) btn.textContent = this.tour.paused ? 'Resume' : 'Pause';
  }

  skipTourStep() {
    this.sound.playClick();
    clearTimeout(this.tour.timer);
    this.runTourStep(this.tour.step + 1);
  }

  runTourStep(stepIdx) {
    const steps = [
      { name: '1/6: World Map & Navigation', duration: 15000, fn: () => this.tourStepWorldMap() },
      { name: '2/6: The Liver Lab & ALT Test', duration: 15000, fn: () => this.tourStepLiver() },
      { name: '3/6: The Heart Station & 72 BPM Pulse', duration: 15000, fn: () => this.tourStepHeart() },
      { name: '4/6: Kidney Operations & Nephron Filters', duration: 15000, fn: () => this.tourStepKidney() },
      { name: '5/6: Culturally Balanced Indian Meal', duration: 15000, fn: () => this.tourStepPlate() },
      { name: '6/6: Report Detective Case & Level Up', duration: 15000, fn: () => this.tourStepDetective() }
    ];

    if (stepIdx >= steps.length) {
      this.stopPresentationTour();
      this.showCelebrationToast('Professor Demo Completed!', '90-second educational tour finished successfully!');
      return;
    }

    this.tour.step = stepIdx;
    const cur = steps[stepIdx];

    const label = document.getElementById('tour-stage-name');
    if (label) label.textContent = cur.name;

    const fill = document.getElementById('tour-progress-bar');
    if (fill) fill.style.width = `${((stepIdx + 1) / steps.length) * 100}%`;

    cur.fn();

    this.tour.timer = setTimeout(() => {
      if (this.tour.active && !this.tour.paused) {
        this.runTourStep(stepIdx + 1);
      }
    }, cur.duration);
  }

  tourStepWorldMap() {
    this.world3D.resetView();
    const title = document.getElementById('viewport-organ-title');
    const sub = document.getElementById('viewport-organ-sub');
    if (title) title.textContent = 'PROFESSOR DEMO: 3D BODY WORLD MAP';
    if (sub) sub.textContent = 'Real anatomical glTF meshes, spatial lighting, and dynamic 3D beacons';
  }

  tourStepLiver() {
    this.openMission('liver_lab');
    setTimeout(() => {
      this.setModalStage('tests');
    }, 4000);
  }

  tourStepHeart() {
    this.openMission('heart_station');
    setTimeout(() => {
      this.setModalStage('challenge');
    }, 4000);
  }

  tourStepKidney() {
    this.openMission('kidney_room');
    setTimeout(() => {
      this.setModalStage('challenge');
      this.onHydrationSlider(2.5);
    }, 4000);
  }

  tourStepPlate() {
    this.openMission('nutrition_plate');
    setTimeout(() => {
      this.setModalStage('challenge');
      this.togglePlateItem('veggies', 'Palak Paneer Gravy');
      this.togglePlateItem('protein', 'Dal Tadka');
      this.togglePlateItem('grains', 'Multigrain Roti');
    }, 3000);
  }

  tourStepDetective() {
    this.openMission('report_detective');
    setTimeout(() => {
      this.setModalStage('challenge');
      this.solveClue('alt');
      this.solveClue('ldl');
    }, 3500);
  }
}

// Global App Instance
const QuestApp = new NutriSphereQuestApp();
window.QuestApp = QuestApp;

// Auto-boot on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  QuestApp.init();
});
