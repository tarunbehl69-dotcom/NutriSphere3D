/**
 * NutriSphere 3D - Alcohol & Hepatic Health Module
 * Features:
 * - Dedicated 3D Interactive Three.js Liver Anatomy with Lobular Highlights
 * - Pure Ethanol Density Calculator (Volume * ABV * 0.789)
 * - WHO & US Standard Drink Equivalents & Metabolic Clearance Time
 * - Chart.js Weekly Intake Tracking
 * - Correlated Report Biomarkers (ALT, AST, de Ritis, GGT, MCV)
 */

class AlcoholHealthModule {
  constructor() {
    this.container = document.getElementById('liver-3d-container');
    this.reportId = 'rep_demo_2026_001';
    this.records = [];
    this.chart = null;

    const urlParams = new URLSearchParams(window.location.search);
    this.focusOrgan = urlParams.get('focus');

    this.init3DLiver();
    this.initCalculator();
    this.initReportBiomarkers();
    this.loadIntakeHistory();
    this.setupEventListeners();
    this.checkFocusOrgan();
  }

  checkFocusOrgan() {
    if (!this.focusOrgan) return;
    const banner = document.getElementById('focus-organ-banner');
    const title = document.getElementById('focus-organ-title');
    const desc = document.getElementById('focus-organ-desc');
    if (banner && title && desc) {
      banner.classList.remove('hidden');
      title.textContent = `Alcohol Impact on ${this.focusOrgan}`;
      desc.textContent = `Examining ethanol biochemical breakdown, acetaldehyde formation, and physiological recovery mechanisms specifically for your ${this.focusOrgan.toLowerCase()}.`;
    }
  }

  // --- 1. Interactive 3D Three.js Liver Model ---
  init3DLiver() {
    if (!this.container || typeof THREE === 'undefined') return;

    const width = this.container.clientWidth || 600;
    const height = this.container.clientHeight || 340;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0f1d); // Dark clinical theater backdrop

    this.camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    this.camera.position.set(0, 0.2, 3.8);

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);

    // Clinical High-Contrast Studio Lighting
    const hemiLight = new THREE.HemisphereLight(0x38bdf8, 0x0f172a, 0.8);
    this.scene.add(hemiLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.4);
    keyLight.position.set(5, 8, 6);
    this.scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0xccfbf1, 0.6);
    fillLight.position.set(-5, -2, 3);
    this.scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0x38bdf8, 1.25);
    rimLight.position.set(0, -3, -5);
    this.scene.add(rimLight);

    // Build Detailed Liver Group
    this.liverGroup = new THREE.Group();
    this.scene.add(this.liverGroup);

    // Load Authentic 3D Liver GLB Model (NIH 3DPX-021007 Visible Human Male Liver)
    const loader = (typeof THREE.GLTFLoader !== 'undefined') ? new THREE.GLTFLoader() : null;
    if (loader) {
      loader.load('/models/nih/liver_nih.glb', (gltf) => {
        const model = gltf.scene;
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z) || 1;
        const scale = 2.4 / maxDim;

        model.scale.set(scale, scale, scale);
        model.position.sub(center.clone().multiplyScalar(scale));

        model.traverse((child) => {
          if (child.isMesh) {
            child.material = new THREE.MeshStandardMaterial({
              color: 0xf97316, // Vibrant high-contrast hepatic terracotta
              roughness: 0.35,
              metalness: 0.12,
              emissive: 0x431407,
              emissiveIntensity: 0.15
            });
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });

        this.liverMesh = model;
        this.liverGroup.add(model);
      }, undefined, (err) => {
        console.warn('Fallback procedural liver:', err);
        this.buildProceduralLiverMesh();
      });
    } else {
      this.buildProceduralLiverMesh();
    }

    // Mouse Interaction & OrbitControls
    this.setupLiverMouseControls();
    this.animate();

    window.addEventListener('resize', () => {
      if (!this.container || !this.renderer || !this.camera) return;
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      this.camera.aspect = w / h;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(w, h);
    });
  }

  buildProceduralLiverMesh() {
    const geo = new THREE.DodecahedronGeometry(1.2, 2);
    geo.scale(1.4, 0.8, 0.9);
    const mat = new THREE.MeshStandardMaterial({
      color: 0xf97316,
      roughness: 0.35,
      metalness: 0.12,
      emissive: 0x431407,
      emissiveIntensity: 0.15
    });
    this.liverMesh = new THREE.Mesh(geo, mat);
    this.liverGroup.add(this.liverMesh);
  }

  setupLiverMouseControls() {
    let isDragging = false;
    let prevMouse = { x: 0, y: 0 };
    const dom = this.renderer.domElement;

    dom.addEventListener('mousedown', (e) => {
      isDragging = true;
      prevMouse = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener('mouseup', () => { isDragging = false; });

    dom.addEventListener('mousemove', (e) => {
      if (isDragging && this.liverGroup) {
        const dx = e.clientX - prevMouse.x;
        const dy = e.clientY - prevMouse.y;
        this.liverGroup.rotation.y += dx * 0.008;
        this.liverGroup.rotation.x += dy * 0.008;
        prevMouse = { x: e.clientX, y: e.clientY };
      }
    });

    dom.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.camera.position.z = Math.min(Math.max(this.camera.position.z + e.deltaY * 0.005, 3.2), 8.5);
    }, { passive: false });
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    if (this.liverGroup) {
      this.liverGroup.rotation.y += 0.0025; // Slow gentle rotation
      const pulse = Math.sin(Date.now() * 0.002) * 0.02;
      this.liverGroup.scale.set(1 + pulse, 1 + pulse, 1 + pulse);
    }
    this.renderer.render(this.scene, this.camera);
  }

  resetLiverView() {
    if (!this.liverGroup || !this.camera) return;
    this.liverGroup.rotation.set(0, 0, 0);
    this.camera.position.set(0, 0.5, 5.2);
  }

  toggleLobules() {
    if (!this.lobuleParticles) return;
    this.lobuleParticles.visible = !this.lobuleParticles.visible;
    const btn = document.getElementById('btn-toggle-lobule');
    if (btn) {
      btn.textContent = this.lobuleParticles.visible ? 'Hide Lobules' : 'Highlight Lobules';
    }
  }

  // --- 2. Pure Ethanol Calculator ---
  initCalculator() {
    const volInput = document.getElementById('calc-volume');
    const abvInput = document.getElementById('calc-abv');
    const nameInput = document.getElementById('calc-beverage-name');

    const updateCalc = () => {
      const vol = parseFloat(volInput.value) || 0;
      const abv = parseFloat(abvInput.value) || 0;

      // Pure Ethanol formula: Vol (mL) * (ABV / 100) * 0.789 g/mL
      const pureGrams = vol * (abv / 100.0) * 0.789;
      const whoDrinks = pureGrams / 10.0;
      const usDrinks = pureGrams / 14.0;
      const clearanceHours = pureGrams / 10.0; // Approx 7-10g/hr clearance

      // Update Outputs
      document.getElementById('out-pure-grams').innerHTML = `${pureGrams.toFixed(1)} <span class="text-xs text-slate-400 font-normal">g</span>`;
      document.getElementById('out-who-drinks').innerHTML = `${whoDrinks.toFixed(1)} <span class="text-xs text-slate-400 font-normal">drinks</span>`;
      document.getElementById('out-us-drinks').innerHTML = `${usDrinks.toFixed(1)} <span class="text-xs text-slate-400 font-normal">drinks</span>`;
      document.getElementById('out-clearance-time').innerHTML = `~${clearanceHours.toFixed(1)} <span class="text-xs text-slate-400 font-normal">hrs</span>`;

      // Risk Tier assessment
      const badge = document.getElementById('out-risk-badge');
      const desc = document.getElementById('out-risk-desc');

      if (pureGrams <= 20) {
        badge.className = 'px-3 py-1 rounded-full text-xs font-semibold badge-teal';
        badge.textContent = 'Low Risk Tier (≤ 20g)';
        desc.textContent = 'Within standard single-session moderation guidelines.';
      } else if (pureGrams <= 40) {
        badge.className = 'px-3 py-1 rounded-full text-xs font-semibold badge-warning';
        badge.textContent = 'Moderate Risk Tier (21–40g)';
        desc.textContent = 'Substantial metabolic demand on hepatic enzymes; increased steatosis risk.';
      } else if (pureGrams <= 60) {
        badge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-orange-950 text-orange-300 border border-orange-700';
        badge.textContent = 'High Risk Tier (41–60g)';
        desc.textContent = 'Binge threshold: Significant hepatocellular stress and oxidative challenge.';
      } else {
        badge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-rose-950 text-rose-300 border border-rose-700';
        badge.textContent = 'Severe Risk Tier (> 60g)';
        desc.textContent = 'Acute hepatic and central nervous system intoxication warning.';
      }
    };

    if (volInput && abvInput) {
      volInput.addEventListener('input', updateCalc);
      abvInput.addEventListener('input', updateCalc);
      updateCalc();
    }

    // Preset button handlers
    document.querySelectorAll('.btn-preset').forEach(btn => {
      btn.addEventListener('click', () => {
        nameInput.value = btn.dataset.name;
        volInput.value = btn.dataset.vol;
        abvInput.value = btn.dataset.abv;
        updateCalc();
      });
    });

    // Log Intake Button
    const logBtn = document.getElementById('btn-log-intake');
    if (logBtn) {
      logBtn.addEventListener('click', async () => {
        const payload = {
          beverage_type: nameInput.value || 'Custom Drink',
          volume_ml: parseFloat(volInput.value) || 0,
          abv_percent: parseFloat(abvInput.value) || 0,
          drinking_days_per_week: 1
        };

        try {
          const res = await fetch('/api/alcohol/records', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...NutriSphere.getAuthHeaders()
            },
            body: JSON.stringify(payload)
          });

          if (res.ok) {
            NutriSphere.showToast(`Logged ${payload.beverage_type} successfully!`, 'info');
            this.loadIntakeHistory();
          } else {
            NutriSphere.showToast('Failed to log intake record.', 'error');
          }
        } catch (e) {
          NutriSphere.showToast('Error connecting to alcohol log API.', 'error');
        }
      });
    }
  }

  // --- 3. Weekly Intake History & Chart.js ---
  async loadIntakeHistory() {
    try {
      const res = await fetch('/api/alcohol/records', {
        headers: NutriSphere.getAuthHeaders()
      });
      if (!res.ok) return;

      const data = await res.json();
      this.records = data.records || [];
      this.renderIntakeList();
      this.renderIntakeChart();
    } catch (e) {
      console.error('Error fetching alcohol records:', e);
    }
  }

  renderIntakeList() {
    const listContainer = document.getElementById('intake-records-list');
    const totalGramsBadge = document.getElementById('total-week-grams');
    if (!listContainer) return;

    if (!this.records || this.records.length === 0) {
      listContainer.innerHTML = `<div class="text-xs text-slate-500 py-4 text-center">No intake records logged yet.</div>`;
      if (totalGramsBadge) totalGramsBadge.textContent = '0.0 g logged';
      return;
    }

    let totalGrams = 0;
    listContainer.innerHTML = this.records.map(r => {
      const grams = r.pure_alcohol_grams || r.pure_ethanol_grams || 0;
      totalGrams += grams;
      const bName = r.beverage_type || r.beverage_name || 'Drink';
      return `
        <div class="flex items-center justify-between p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs hover:border-slate-700 transition-colors">
          <div>
            <div class="font-bold text-slate-200">${bName}</div>
            <div class="text-[11px] text-slate-400">${r.volume_ml} mL @ ${r.abv_percent}% • <span class="text-teal-300 font-mono font-medium">${grams.toFixed(1)}g pure</span></div>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-[10px] text-slate-500 font-mono">${r.recorded_date || r.date || ''}</span>
            <button onclick="window.AlcoholModule.deleteRecord('${r.id}')" class="text-slate-500 hover:text-rose-400 transition-colors p-1" title="Delete entry">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
      `;
    }).join('');

    if (totalGramsBadge) {
      totalGramsBadge.textContent = `${totalGrams.toFixed(1)} g logged`;
    }
  }

  async deleteRecord(recordId) {
    try {
      const res = await fetch(`/api/alcohol/records/${recordId}`, {
        method: 'DELETE',
        headers: NutriSphere.getAuthHeaders()
      });
      if (res.ok) {
        NutriSphere.showToast('Intake entry deleted.', 'info');
        this.loadIntakeHistory();
      }
    } catch (e) {
      NutriSphere.showToast('Failed to delete entry.', 'error');
    }
  }

  renderIntakeChart() {
    const canvas = document.getElementById('alcohol-history-chart');
    if (!canvas || typeof Chart === 'undefined') return;

    // Aggregate by date
    const dateMap = {};
    // Seed last 5 days
    for (let i = 4; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const str = d.toISOString().split('T')[0];
      dateMap[str] = 0;
    }

    this.records.forEach(r => {
      dateMap[r.date] = (dateMap[r.date] || 0) + (r.pure_ethanol_grams || 0);
    });

    const labels = Object.keys(dateMap).slice(-7);
    const dataPoints = labels.map(l => dateMap[l]);

    if (this.chart) {
      this.chart.destroy();
    }

    this.chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels.map(l => l.slice(5)), // MM-DD
        datasets: [{
          label: 'Pure Ethanol (grams)',
          data: dataPoints,
          backgroundColor: dataPoints.map(v => v > 40 ? 'rgba(239, 68, 68, 0.7)' : (v > 20 ? 'rgba(245, 158, 11, 0.7)' : 'rgba(20, 184, 166, 0.7)')),
          borderColor: dataPoints.map(v => v > 40 ? '#ef4444' : (v > 20 ? '#f59e0b' : '#14b8a6')),
          borderWidth: 1.5,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.parsed.y.toFixed(1)} g pure ethanol`
            }
          }
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { color: '#94a3b8', font: { size: 10 } }
          },
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { size: 10 } },
            beginAtZero: true,
            suggestedMax: 50
          }
        }
      }
    });
  }

  // --- 4. Correlated Report Biomarkers ---
  async initReportBiomarkers() {
    try {
      const res = await fetch(`/api/alcohol/report-context/${this.reportId}`, {
        headers: NutriSphere.getAuthHeaders()
      });
      if (!res.ok) return;

      const data = await res.json();
      this.renderBiomarkerCards(data);
    } catch (e) {
      console.warn('Could not load report-context:', e);
    }
  }

  renderBiomarkerCards(data) {
    const grid = document.getElementById('biomarkers-alcohol-grid');
    const badge = document.getElementById('overall-liver-badge');
    const label = document.getElementById('report-label');
    if (label) label.textContent = data.report_id || this.reportId;

    const markers = data.evaluated_markers || data.markers || [];
    if (!markers || markers.length === 0) return;

    let elevatedCount = 0;
    grid.innerHTML = markers.map(m => {
      const isHigh = m.flag === 'above_reference' || m.flag === 'HIGH';
      if (isHigh) elevatedCount++;
      const valColor = isHigh ? 'text-amber-300' : 'text-slate-100';
      const flagColor = isHigh ? 'text-amber-400' : 'text-emerald-400';
      const labelText = m.label || m.name || m.analyte_code;
      const valText = m.measured_value ?? m.value ?? '--';

      return `
        <div class="p-3 rounded-lg bg-slate-900 border ${isHigh ? 'border-amber-500/30' : 'border-slate-800'}">
          <div class="text-[11px] text-slate-400 truncate" title="${labelText}">${labelText}</div>
          <div class="text-base font-bold ${valColor}">${valText} <span class="text-[10px] text-slate-400 font-normal">${m.unit || ''}</span></div>
          <div class="text-[10px] ${flagColor} mt-0.5 font-medium">${isHigh ? 'Elevated' : 'Within Range'}</div>
        </div>
      `;
    }).join('');

    // Add de Ritis ratio if present
    if (data.de_ritis_ratio) {
      grid.innerHTML += `
        <div class="p-3 rounded-lg bg-slate-900 border border-sky-500/30">
          <div class="text-[11px] text-slate-400">de Ritis Ratio (AST/ALT)</div>
          <div class="text-base font-bold text-sky-300">${data.de_ritis_ratio.toFixed(2)}</div>
          <div class="text-[10px] text-slate-400 mt-0.5">Ratio < 1.0 (Hepatocellular pattern)</div>
        </div>
      `;
    }

    if (badge) {
      if (elevatedCount > 0) {
        badge.className = 'badge-warning text-[10px] px-2 py-0.5 rounded font-mono';
        badge.textContent = `${elevatedCount} Marker(s) Elevated`;
      } else {
        badge.className = 'badge-teal text-[10px] px-2 py-0.5 rounded font-mono';
        badge.textContent = 'Enzymes Within Interval';
      }
    }
  }

  setupEventListeners() {
    const resetBtn = document.getElementById('btn-reset-liver-cam');
    if (resetBtn) resetBtn.addEventListener('click', () => this.resetLiverView());

    const toggleBtn = document.getElementById('btn-toggle-lobule');
    if (toggleBtn) toggleBtn.addEventListener('click', () => this.toggleLobules());

    const syncBtn = document.getElementById('btn-sync-report');
    if (syncBtn) {
      syncBtn.addEventListener('click', () => {
        const sel = document.getElementById('select-active-report');
        if (sel) {
          this.reportId = sel.value;
          this.initReportBiomarkers();
          NutriSphere.showToast(`Synced with ${this.reportId}`, 'info');
        }
      });
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.AlcoholModule = new AlcoholHealthModule();
});
