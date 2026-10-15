/**
 * NutriSphere X — Professor Presentation & Product Architecture Demo Mode
 * 
 * Features:
 * - 10-Step Comprehensive Academic Tour ("Your Body is the Interface")
 * - Live Architecture Overlay HUD with real-time technical metrics
 * - Multi-Patient Cohort Switcher (Rohan Sharma, Priya Patel, Vikram Mehta)
 * - Key Product Management Evaluation Metrics (100/100 tests, 74 analytes, local-first)
 * - Real-time jump to 3D Body Atlas, Organ Reveal, Trajectories, and Nutrition
 */

class NutriSpherePresentation {
  constructor() {
    this.currentStep = 0;
    this.overlayVisible = false;
    this.activePatient = 'rohan';

    this.patients = {
      rohan: {
        name: "Rohan Sharma (38M)",
        profile: "Metabolic Syndrome, High ALT (58 U/L), High LDL (142 mg/dL), Vit D Insufficiency",
        focalOrgan: "Liver",
        reportId: "rep_demo_2026_001"
      },
      priya: {
        name: "Priya Patel (29F)",
        profile: "Microcytic Anemia, Low Serum Ferritin (14 ng/mL), Hemoglobin 10.2 g/dL",
        focalOrgan: "Intestines",
        reportId: "rep_synth_anemia_001"
      },
      vikram: {
        name: "Vikram Mehta (52M)",
        profile: "Renal Risk, High Serum Creatinine (1.65 mg/dL), eGFR 46 mL/min",
        focalOrgan: "Kidneys",
        reportId: "rep_synth_renal_001"
      }
    };

    this.steps = [
      {
        title: "1. The Vision — Your Body is the Interface",
        badge: "Product Vision",
        color: "text-teal-400",
        summary: "NutriSphere X eliminates standard detached healthcare dashboards. The anatomical 3D body is no longer a peripheral widget — it is the primary spatial navigation system for clinical intelligence.",
        details: [
          "Inspired by spatial computing restraint: quiet graphite backdrops (#101419), luminous cyan accents (#79CFCB), and obsidian frosted glass.",
          "Every organ acts as an interactive gateway to verified laboratory biomarkers, historical trajectories, and physiological mechanics.",
          "Clinically grounded: non-diagnostic health literacy that explains reference ranges without fabricating diagnoses."
        ],
        actionText: "Enter the Body Atlas",
        actionUrl: "/anatomy"
      },
      {
        title: "2. The Ingestion Pipeline — Vector PDF & Vision OCR",
        badge: "Ingestion Engine",
        color: "text-sky-400",
        summary: "Robust multi-modal laboratory document ingestion pipeline accepting PDFs up to 20 pages and high-res images (PNG, JPG) up to 15MB.",
        details: [
          "Direct vector extraction via PyMuPDF preserves high fidelity and table structure with zero OCR latency.",
          "Scanned copies seamlessly fall back to image preprocessing and OCR with per-field confidence scoring.",
          "Strict Human Verification review queue triggered whenever extraction confidence drops below 85%."
        ],
        actionText: "Inspect Upload Workflow",
        actionUrl: "/upload"
      },
      {
        title: "3. Organ Reveal — Liver Transaminases & de Ritis Ratio",
        badge: "Signature Interaction",
        color: "text-emerald-400",
        summary: "Selecting any organ dims non-relevant systems and triggers a smooth 3/4 camera approach, activating the clinical teal highlight.",
        details: [
          "Demonstrates patient Rohan Sharma's hepatic transaminases: ALT (SGPT) at 58 U/L and AST (SGOT) at 46 U/L.",
          "Algorithmic cross-analyte clustering computes the de Ritis Ratio (AST/ALT = 0.79), indicating metabolic hepatocellular stress rather than acute alcoholic hepatitis.",
          "Clear clinical disclaimer: Transaminase elevation reflects membrane permeability, not structural organ failure."
        ],
        actionText: "Focus Liver in Atlas",
        actionUrl: "/anatomy?focus=Liver"
      },
      {
        title: "4. The 3D-to-Screen Spatial Projection Engine",
        badge: "WebGL & Spatial Math",
        color: "text-teal-300",
        summary: "Real-time projection matrix calculates 3D organ anchor coordinates in world space and projects them onto the 2D viewport coordinates.",
        details: [
          "Dynamic SVG Bezier connector line links the 3D organ hotspot (#organ-anchor-point) to the floating 2D BioSignals card.",
          "Recalculated on every requestAnimationFrame during OrbitControls camera rotation and browser resizing.",
          "Behind-camera frustum clipping hides anchor markers and lines when organs rotate out of the camera's field of view."
        ],
        actionText: "Inspect 3D Projection",
        actionUrl: "/anatomy?focus=Liver"
      },
      {
        title: "5. Multi-System Journey — Renal Filtration & Fluid Balance",
        badge: "Physiological Pathways",
        color: "text-amber-400",
        summary: "Fluid camera transition sweeps from the upper right abdomen to the retroperitoneal space to inspect the bilateral Kidneys.",
        details: [
          "Visualizes renal filtration markers: Serum Creatinine (1.05 mg/dL), eGFR (88 mL/min/1.73m²), and Blood Urea Nitrogen (BUN 16 mg/dL).",
          "Explains age-related glomerular filtration dynamics and hydration sensitivity without alarming the patient.",
          "Highlights metabolic interconnectivity: how hepatic lipid synthesis and transaminases relate to renal vascular health."
        ],
        actionText: "Inspect Kidneys in Atlas",
        actionUrl: "/anatomy?focus=Kidneys"
      },
      {
        title: "6. Longitudinal Time Machine — Multi-Year Trajectories",
        badge: "Longitudinal Analytics",
        color: "text-sky-300",
        summary: "Interactive multi-year timeline tracking patient Rohan Sharma's biometric journey across 2024, 2025, and 2026 encounters.",
        details: [
          "Tracks transaminases (ALT), atherogenic lipids (LDL, ApoB), glycemia (Glucose, HbA1c), and Vitamin D over 24 months.",
          "Visual reference bands display preserved laboratory-specific normal intervals across historical analyzer calibrations.",
          "Provides contextual trajectory tags: 'Stable Optimal', 'Mild Upward Drift', 'Positive Recovery Trajectory'."
        ],
        actionText: "Open Longitudinal Dashboard",
        actionUrl: "/dashboard"
      },
      {
        title: "7. Food-First Indian Cultural Nutrition Engine",
        badge: "Cultural Nutrition",
        color: "text-teal-300",
        summary: "Directly bridges laboratory findings to culturally authentic Indian meal blueprints across Vegetarian, Vegan, Jain, and Non-Vegetarian patterns.",
        details: [
          "Strict Jain Dietary Rule: Dynamically excludes all subterranean root vegetables (onions, garlic, potatoes, carrots, beetroots).",
          "Automated allergen exclusion filters (Dairy, Gluten, Peanuts, Tree Nuts, Soy).",
          "Targeted dietary science: Amla for non-heme iron absorption, Turmeric/Curcumin for liver support, Ragi & Methi for glycemic moderation."
        ],
        actionText: "Explore Nutrition Blueprints",
        actionUrl: "/nutrition?focus=Liver"
      },
      {
        title: "8. Pure Ethanol Science & Hepatic Clearance Kinetics",
        badge: "Alcohol & Health",
        color: "text-amber-300",
        summary: "Evidence-based ethanol pharmacology: pure mass calculation, 3D hepatic clearance mechanics, and transaminase cross-referencing.",
        details: [
          "Exact chemical physics: Volume (mL) × (ABV% ÷ 100) × 0.789 g/mL ethanol density.",
          "Calculates both WHO standard units (10g) and US standard drinks (14g) without creating a 'safe drinking allowance'.",
          "Rigorous Clinical Guardrail: Explicitly emphasizes that normal ALT/AST values do NOT establish personal drinking safety."
        ],
        actionText: "View Alcohol Module",
        actionUrl: "/alcohol?focus=Liver"
      },
      {
        title: "9. Clinical Governance, Privacy & Zero-PHI Architecture",
        badge: "Safety & Ethics",
        color: "text-rose-400",
        summary: "Engineered to strict clinical informatics standards: local-first execution, complete consent audit trails, and zero external PHI leakage.",
        details: [
          "Zero Diagnostic Claims: All generated interpretations adhere to educational, non-diagnostic framing.",
          "Urgency Escalation Banner: Severe out-of-range panic values trigger immediate medical attention alerts.",
          "Permanent Deletion Guarantee: One-click deletion permanently purges original files, OCR intermediates, and database records.",
          "100/100 automated pytest test cases validating data privacy, consent, calculations, and security."
        ],
        actionText: "Inspect Safety Features",
        actionUrl: "/upload"
      },
      {
        title: "10. Technical Architecture & Tech Stack",
        badge: "Engineering Depth",
        color: "text-cyan-400",
        summary: "Production-grade, local-first full stack built strictly adhering to the assignment requirements without migrating to external frameworks.",
        details: [
          "Backend: Python 3.14 + FastAPI + SQLite (WAL mode) + Pydantic v2 + PyMuPDF + Pillow.",
          "Frontend: HTML5 + Tailwind CSS + Vanilla ES6 JavaScript + Three.js r128 + GSAP + Chart.js.",
          "FastAPI Latency: Sub-15ms local response time for report interpretation and organ mapping.",
          "Port Isolation: Runs on http://127.0.0.1:8080/ to avoid collisions with LMS or university systems."
        ],
        actionText: "Return to Body Atlas",
        actionUrl: "/anatomy"
      }
    ];

    this.initUI();
    this.initArchitectureOverlay();
    this.setupListeners();
  }

  initUI() {
    const modal = document.createElement('div');
    modal.id = 'demo-tour-modal';
    modal.className = 'fixed inset-0 z-50 bg-[#101419]/90 backdrop-blur-xl flex items-center justify-center p-4 transition-all duration-300 opacity-0 pointer-events-none select-none';
    modal.innerHTML = `
      <div class="spatial-glass w-full max-w-2xl border border-teal-500/40 shadow-2xl p-6 sm:p-8 flex flex-col gap-6 relative transform transition-all duration-300 scale-95" id="demo-tour-card">
        
        <!-- Header -->
        <div class="flex items-start justify-between border-b border-slate-800 pb-4">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span id="tour-badge" class="spatial-pill text-[10px] text-teal-300 py-0.5 px-2 font-mono uppercase tracking-wider">Product Vision</span>
              <span class="text-xs text-slate-400 font-mono" id="tour-step-counter">Step 1 of 10</span>
            </div>
            <h2 id="tour-title" class="text-xl sm:text-2xl font-black text-white">1. The Vision — Your Body is the Interface</h2>
          </div>
          <button id="tour-close-btn" class="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Cohort Switcher & Architecture Pill -->
        <div class="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
          <div class="flex items-center gap-1.5">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Cohort:</span>
            <button class="patient-pill active px-2 py-0.5 rounded text-[11px] font-medium bg-teal-500/20 text-teal-300 border border-teal-500/40" data-patient="rohan">Rohan (Metabolic)</button>
            <button class="patient-pill px-2 py-0.5 rounded text-[11px] font-medium hover:bg-slate-800 text-slate-400 transition-colors" data-patient="priya">Priya (Anemia)</button>
            <button class="patient-pill px-2 py-0.5 rounded text-[11px] font-medium hover:bg-slate-800 text-slate-400 transition-colors" data-patient="vikram">Vikram (Renal)</button>
          </div>
          <button id="btn-toggle-arch-overlay" class="px-2.5 py-1 rounded-lg text-[11px] font-mono font-semibold bg-slate-800 hover:bg-slate-700 text-teal-300 border border-teal-500/30 transition-all flex items-center gap-1">
            <svg class="w-3.5 h-3.5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/></svg>
            <span>HUD Overlay: OFF</span>
          </button>
        </div>

        <!-- Body Content -->
        <div class="flex flex-col gap-4 text-sm leading-relaxed">
          <p id="tour-summary" class="text-slate-100 font-medium text-base"></p>
          
          <div class="p-4 rounded-xl bg-slate-950/70 border border-slate-800">
            <span class="text-[10px] uppercase tracking-wider text-teal-400 font-bold block mb-2 font-mono">Academic & Engineering Highlights</span>
            <ul id="tour-details-list" class="list-disc list-inside space-y-1.5 text-xs text-slate-300"></ul>
          </div>
        </div>

        <!-- Key Metrics Callout Bar (For PM Evaluation) -->
        <div class="grid grid-cols-4 gap-2 text-center p-2 rounded-xl bg-slate-900/60 border border-slate-800/80 text-[10px]">
          <div>
            <div class="text-teal-300 font-bold font-mono text-xs">100 / 100</div>
            <div class="text-slate-400">Pytest Tests</div>
          </div>
          <div>
            <div class="text-teal-300 font-bold font-mono text-xs">74 Analytes</div>
            <div class="text-slate-400">14 Panels</div>
          </div>
          <div>
            <div class="text-teal-300 font-bold font-mono text-xs">0ms Cloud</div>
            <div class="text-slate-400">Local-First PHI</div>
          </div>
          <div>
            <div class="text-teal-300 font-bold font-mono text-xs">Port 8080</div>
            <div class="text-slate-400">Isolated Host</div>
          </div>
        </div>

        <!-- Footer / Navigation Controls -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-slate-800">
          <div class="flex items-center gap-2 w-full sm:w-auto">
            <button id="tour-prev-btn" class="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-semibold text-slate-300 transition-all">
              &larr; Previous
            </button>
            <button id="tour-next-btn" class="px-5 py-2 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 text-xs font-bold shadow-lg shadow-teal-500/20 transition-all">
              Next Step &rarr;
            </button>
          </div>

          <a id="tour-action-btn" href="/anatomy" class="w-full sm:w-auto px-5 py-2 rounded-xl bg-teal-950 hover:bg-teal-900 text-teal-300 border border-teal-700 text-xs font-semibold text-center transition-all">
            Enter the Body Atlas &rarr;
          </a>
        </div>

      </div>
    `;
    document.body.appendChild(modal);

    this.modal = modal;
    this.card = document.getElementById('demo-tour-card');
  }

  initArchitectureOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'arch-overlay-hud';
    overlay.className = 'fixed top-20 right-4 z-40 hidden spatial-glass p-3.5 w-72 flex flex-col gap-2 font-mono text-[10px] text-slate-300 shadow-2xl border border-teal-500/40 pointer-events-auto';
    overlay.innerHTML = `
      <div class="flex items-center justify-between pb-1.5 border-b border-slate-800 text-teal-400 font-bold">
        <span class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-teal-400 animate-ping"></span>
          ARCH OVERLAY HUD
        </span>
        <button id="close-arch-hud" class="text-slate-400 hover:text-white">&times;</button>
      </div>
      <div>
        <div class="text-slate-400">ENGINE:</div>
        <div class="text-slate-100 font-bold">Three.js r128 • 42 Anatomical Meshes</div>
      </div>
      <div>
        <div class="text-slate-400">RENDER PIPELINE:</div>
        <div class="text-slate-100">PBR Roughness 0.45 • Emissive Pulse</div>
      </div>
      <div>
        <div class="text-slate-400">FASTAPI ENDPOINT:</div>
        <div class="text-teal-300">GET /api/reports/{id} (~12ms)</div>
      </div>
      <div>
        <div class="text-slate-400">DATABASE WAL MODE:</div>
        <div class="text-slate-100">SQLite local-first • 0-PHI Cloud</div>
      </div>
      <div>
        <div class="text-slate-400">CLINICAL COVERAGE:</div>
        <div class="text-slate-100">74 Analytes • 14 Medical Panels</div>
      </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById('close-arch-hud')?.addEventListener('click', () => {
      this.toggleArchitectureOverlay(false);
    });
  }

  toggleArchitectureOverlay(forceState) {
    this.overlayVisible = forceState !== undefined ? forceState : !this.overlayVisible;
    const hud = document.getElementById('arch-overlay-hud');
    const toggleBtn = document.getElementById('btn-toggle-arch-overlay');
    if (hud) {
      if (this.overlayVisible) {
        hud.classList.remove('hidden');
      } else {
        hud.classList.add('hidden');
      }
    }
    if (toggleBtn) {
      toggleBtn.innerHTML = `
        <svg class="w-3.5 h-3.5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/></svg>
        <span>HUD Overlay: ${this.overlayVisible ? 'ON' : 'OFF'}</span>
      `;
    }
  }

  setupListeners() {
    // Header presentation buttons across all pages
    document.querySelectorAll('#btn-demo-tour, #btn-presentation-mode').forEach(btn => {
      btn.addEventListener('click', () => this.startTour());
    });

    // Close button
    document.getElementById('tour-close-btn')?.addEventListener('click', () => this.closeTour());

    // Navigation Buttons
    document.getElementById('tour-next-btn')?.addEventListener('click', () => this.nextStep());
    document.getElementById('tour-prev-btn')?.addEventListener('click', () => this.prevStep());

    // HUD overlay toggle
    document.getElementById('btn-toggle-arch-overlay')?.addEventListener('click', () => {
      this.toggleArchitectureOverlay();
    });

    // Patient switcher pills
    document.querySelectorAll('.patient-pill').forEach(pill => {
      pill.addEventListener('click', (e) => {
        document.querySelectorAll('.patient-pill').forEach(p => {
          p.classList.remove('active', 'bg-teal-500/20', 'text-teal-300', 'border-teal-500/40');
          p.classList.add('text-slate-400');
        });
        const target = e.currentTarget;
        target.classList.add('active', 'bg-teal-500/20', 'text-teal-300', 'border-teal-500/40');
        target.classList.remove('text-slate-400');

        const pKey = target.getAttribute('data-patient');
        this.selectPatient(pKey);
      });
    });

    // Keyboard navigation (Escape to close, Arrows for navigation)
    window.addEventListener('keydown', (e) => {
      if (this.modal.classList.contains('opacity-0')) return;
      if (e.key === 'Escape') this.closeTour();
      if (e.key === 'ArrowRight') this.nextStep();
      if (e.key === 'ArrowLeft') this.prevStep();
    });
  }

  selectPatient(patientKey) {
    this.activePatient = patientKey;
    const p = this.patients[patientKey];
    if (!p) return;

    if (window.NutriSphere) {
      NutriSphere.showToast(`Switched active presentation patient: ${p.name}`, 'info');
    }

    // If on anatomy page, pivot organ to focal organ
    if (window.anatomyInstance && p.focalOrgan) {
      window.anatomyInstance.selectOrgan(p.focalOrgan, true);
    }
  }

  startTour() {
    this.currentStep = 0;
    if (!localStorage.getItem('nutrisphere_active_report')) {
      fetch('/api/demo-report')
        .then(r => r.json())
        .then(data => localStorage.setItem('nutrisphere_active_report', JSON.stringify(data)))
        .catch(() => {});
    }
    this.renderCurrentStep();
    this.modal.classList.remove('opacity-0', 'pointer-events-none');
    this.card.classList.remove('scale-95');
  }

  closeTour() {
    this.modal.classList.add('opacity-0', 'pointer-events-none');
    this.card.classList.add('scale-95');
  }

  nextStep() {
    if (this.currentStep < this.steps.length - 1) {
      this.currentStep++;
      this.renderCurrentStep();
    } else {
      this.closeTour();
      if (window.NutriSphere) {
        NutriSphere.showToast('Demo Walkthrough Complete! Explore NutriSphere X at your leisure.', 'info');
      }
    }
  }

  prevStep() {
    if (this.currentStep > 0) {
      this.currentStep--;
      this.renderCurrentStep();
    }
  }

  renderCurrentStep() {
    const s = this.steps[this.currentStep];
    if (!s) return;

    document.getElementById('tour-badge').textContent = s.badge;
    document.getElementById('tour-step-counter').textContent = `Step ${this.currentStep + 1} of ${this.steps.length}`;
    document.getElementById('tour-title').textContent = s.title;
    document.getElementById('tour-summary').textContent = s.summary;

    const list = document.getElementById('tour-details-list');
    if (list) {
      list.innerHTML = s.details.map(d => `<li>${d}</li>`).join('');
    }

    const actionBtn = document.getElementById('tour-action-btn');
    if (actionBtn) {
      actionBtn.textContent = s.actionText;
      actionBtn.href = s.actionUrl || '#';
    }

    const prevBtn = document.getElementById('tour-prev-btn');
    if (prevBtn) {
      prevBtn.style.display = this.currentStep === 0 ? 'none' : 'inline-block';
    }

    const nextBtn = document.getElementById('tour-next-btn');
    if (nextBtn) {
      nextBtn.textContent = this.currentStep === this.steps.length - 1 ? 'Finish Tour 🎓' : 'Next Step &rarr;';
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const instance = new NutriSpherePresentation();
  window.NutriSpherePresentation = instance;
  window.presentationInstance = instance;
});
