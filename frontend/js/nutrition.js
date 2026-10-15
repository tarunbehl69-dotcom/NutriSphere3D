/**
 * NutriSphere 3D - Food-First Indian Nutrition & Recovery Client Controller
 * Features:
 * - Dietary Pattern Switching (Vegetarian, Vegan, Jain, Non-Vegetarian)
 * - Dynamic Multi-Select Allergy Filtering (Dairy, Gluten, Peanuts, Soy)
 * - Report-Linked Nutritional Guidance via /api/nutrition/context
 * - Culturally tailored whole-food Indian ingredients
 */

class NutritionModule {
  constructor() {
    this.currentDiet = 'vegetarian';
    this.currentAllergies = [];
    this.reportId = 'rep_demo_2026_001';

    this.initEventListeners();
    this.fetchGuidance();
  }

  initEventListeners() {
    // Diet Tabs
    const tabs = document.querySelectorAll('.diet-tab-btn');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => {
          t.classList.remove('bg-teal-500', 'text-slate-950', 'shadow-lg', 'shadow-teal-500/20');
          t.classList.add('bg-slate-900', 'text-slate-300', 'border', 'border-slate-700');
        });

        tab.classList.remove('bg-slate-900', 'text-slate-300', 'border', 'border-slate-700');
        tab.classList.add('bg-teal-500', 'text-slate-950', 'shadow-lg', 'shadow-teal-500/20');

        this.currentDiet = tab.dataset.diet;
        this.updateDietNote();
        this.fetchGuidance();
      });
    });

    // Allergy Filter Checkboxes
    const checkboxes = document.querySelectorAll('.allergy-chip input[type="checkbox"]');
    checkboxes.forEach(cb => {
      cb.addEventListener('change', () => {
        this.currentAllergies = Array.from(checkboxes)
          .filter(c => c.checked)
          .map(c => c.value);

        // Highlight chip label
        const chip = cb.closest('.allergy-chip');
        if (cb.checked) {
          chip.classList.add('border-teal-500/60', 'bg-slate-800');
        } else {
          chip.classList.remove('border-teal-500/60', 'bg-slate-800');
        }

        this.fetchGuidance();
      });
    });

    // Sync Report Button
    const syncBtn = document.getElementById('btn-sync-nutrition');
    if (syncBtn) {
      syncBtn.addEventListener('click', () => {
        const sel = document.getElementById('nutrition-report-select');
        if (sel) {
          this.reportId = sel.value;
          this.fetchGuidance();
          NutriSphere.showToast(`Updated nutrition guidance for ${this.reportId}`, 'info');
        }
      });
    }
  }

  updateDietNote() {
    const noteEl = document.getElementById('diet-pattern-note');
    if (!noteEl) return;

    const notes = {
      'vegetarian': '<span class="font-bold text-teal-300">Indian Vegetarian:</span> Plant-rich pulses, vegetables, whole grains, nuts, and dairy (paneer, curd).',
      'vegan': '<span class="font-bold text-teal-300">Indian Vegan:</span> 100% plant-based pulses, soy/tofu, seeds, grains, coconut/sesame; strictly zero dairy/ghee.',
      'jain': '<span class="font-bold text-amber-300">Jain Tradition:</span> Strictly excludes all underground root vegetables (potatoes, onions, garlic, carrots, beetroots). Focuses on moong, lauki, cumin, hing, turmeric, and dairy/pulses.',
      'non-vegetarian': '<span class="font-bold text-teal-300">Non-Vegetarian:</span> Balanced inclusion of eggs, lean chicken, and omega-3 fish alongside whole dals, grains, and greens.'
    };

    noteEl.innerHTML = notes[this.currentDiet] || notes['vegetarian'];
  }

  async fetchGuidance() {
    try {
      const payload = {
        user_id: 'usr_demo_001',
        diet_pattern: this.currentDiet,
        allergies: this.currentAllergies,
        report_id: this.reportId
      };

      const res = await fetch('/api/nutrition/context', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...NutriSphere.getAuthHeaders()
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error('Failed to fetch nutrition context');
      }

      const data = await res.json();
      this.renderMealPlan(data);
      this.renderBiomarkerAdaptations(data);
    } catch (e) {
      console.error('Nutrition guidance fetch error:', e);
      NutriSphere.showToast('Unable to fetch nutrition recommendations.', 'error');
    }
  }

  renderMealPlan(data) {
    const container = document.getElementById('meal-cards-container');
    const badge = document.getElementById('plan-diet-badge');
    if (!container) return;

    const meals = data.meal_plans || data.meals || [];

    if (badge) {
      badge.textContent = `${this.currentDiet.toUpperCase()} PLAN (${meals.length} MEALS)`;
    }

    if (!meals || meals.length === 0) {
      container.innerHTML = `<div class="col-span-4 p-8 text-center text-slate-500 text-sm">No meals matching current allergen filters. Try removing allergy exclusions.</div>`;
      return;
    }

    const mealIcons = {
      'Breakfast': `<svg class="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>`,
      'Lunch': `<svg class="w-5 h-5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
      'Dinner': `<svg class="w-5 h-5 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>`,
      'Snack & Hydration': `<svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>`
    };

    container.innerHTML = meals.map(m => {
      const mealType = m.meal || m.meal_type || 'Lunch';
      const icon = mealIcons[mealType] || mealIcons['Lunch'];
      const nutrients = m.key_nutrients ? `<span class="inline-block px-2 py-0.5 rounded bg-slate-900 border border-slate-700/80 text-[11px] text-teal-300 font-mono">${m.key_nutrients}</span>` : '';

      return `
        <div class="glass-card p-5 flex flex-col justify-between border border-slate-800 hover:border-teal-500/40 transition-all">
          <div class="flex flex-col gap-3">
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
              <div class="flex items-center gap-2">
                ${icon}
                <span class="font-bold text-xs uppercase tracking-wider text-slate-300">${mealType}</span>
              </div>
              <span class="text-[10px] text-slate-500 font-mono">Nutrient Dense</span>
            </div>

            <div>
              <h4 class="font-bold text-slate-100 text-sm leading-snug">${m.title}</h4>
              <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">${m.description}</p>
            </div>

            <div class="pt-2">
              <span class="text-[10px] text-slate-500 uppercase tracking-wider font-semibold block mb-1">Key Nutritional Profile</span>
              <div>${nutrients}</div>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-800/80">
            <span class="text-[10px] text-teal-400 font-semibold block mb-0.5">Suitability</span>
            <p class="text-[11px] text-slate-300 leading-relaxed">${m.suitable_for || 'Supplies steady amino acids, micronutrients, and low glycemic load.'}</p>
          </div>
        </div>
      `;
    }).join('');
  }

  renderBiomarkerAdaptations(data) {
    const listEl = document.getElementById('biomarker-adaptations-list');
    if (!listEl) return;

    const rawLinks = data.biomarker_linked_guidance || data.biomarker_links || [];
    if (rawLinks.length > 0) {
      listEl.innerHTML = rawLinks.map(l => `
        <div class="p-3.5 rounded-xl bg-slate-900 border border-sky-500/40 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-slate-200 mb-1">
              <span>${l.biomarker || l.analyte}</span>
              <span class="font-mono text-teal-300">${l.observed_flag || l.value || ''}</span>
            </div>
            <p class="text-[11px] text-slate-400 leading-relaxed">${l.educational_guidance || l.recommendation}</p>
          </div>
        </div>
      `).join('');
      return;
    }

    const fallbackLinks = [
      {
        analyte: 'ALT (SGPT) Mild Elevation',
        value: '58.0 U/L',
        recommendation: 'Prioritize antioxidant-rich whole foods (Turmeric/Curcumin, Bottle Gourd/Lauki, leafy greens). Avoid ultra-processed oils and limit refined sugars.',
        color: 'border-amber-500/40'
      },
      {
        analyte: 'Fasting Blood Glucose',
        value: '98.0 mg/dL (High-Normal)',
        recommendation: 'Incorporate complex low-GI grains (Ragi, Jowar, Methi/fenugreek seeds) to promote smooth insulin response and blunt postprandial glucose surges.',
        color: 'border-teal-500/40'
      },
      {
        analyte: 'Hemoglobin & Iron Metabolism',
        value: '14.8 g/dL (Stable)',
        recommendation: 'Maintain non-heme iron stores with Sprouted Moong and Palak, enhanced by Vitamin C from fresh Amla (Indian gooseberry) to maximize bioaccessibility.',
        color: 'border-sky-500/40'
      }
    ];

    listEl.innerHTML = fallbackLinks.map(l => `
      <div class="p-3.5 rounded-xl bg-slate-900 border ${l.color} flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between text-[11px] font-bold text-slate-200 mb-1">
            <span>${l.analyte}</span>
            <span class="font-mono text-teal-300">${l.value}</span>
          </div>
          <p class="text-[11px] text-slate-400 leading-relaxed">${l.recommendation}</p>
        </div>
      </div>
    `).join('');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.NutritionModule = new NutritionModule();
});
