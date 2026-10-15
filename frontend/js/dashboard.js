/**
 * NutriSphere 3D - Longitudinal Trends & Dashboard Controller
 * Features:
 * - Animated Stat Counters (Ease-out incrementation)
 * - Multi-Year Longitudinal Trajectory Graphing via Chart.js
 * - Reference Range Shaded Intervals
 * - Analyte Switching & Dynamic Trajectory Metrics
 */

class DashboardController {
  constructor() {
    this.chart = null;
    this.historicalData = {
      years: ['2024 Baseline', '2025 Follow-Up', '2026 Latest'],
      datasets: {
        'hemoglobin': {
          name: 'Hemoglobin',
          unit: 'g/dL',
          values: [14.2, 14.6, 14.8],
          minRef: 13.8,
          maxRef: 17.2,
          color: '#10b981',
          bg: 'rgba(16, 185, 129, 0.15)',
          trend: '+4.2% (Steady Optimal)',
          clinicalSummary: 'Robust erythropoiesis and iron storage consistency over 24 months.'
        },
        'alt': {
          name: 'ALT (SGPT)',
          unit: 'U/L',
          values: [32.0, 44.0, 58.0],
          minRef: 0,
          maxRef: 56.0,
          color: '#f59e0b',
          bg: 'rgba(245, 158, 11, 0.15)',
          trend: '+81.2% (Mild Upward Drift)',
          clinicalSummary: 'Mild hepatocellular transaminase elevation noted in 2026; lifestyle and dietary review recommended.'
        },
        'fasting_glucose': {
          name: 'Fasting Blood Glucose',
          unit: 'mg/dL',
          values: [89.0, 93.0, 98.0],
          minRef: 70.0,
          maxRef: 99.0,
          color: '#14b8a6',
          bg: 'rgba(20, 184, 166, 0.15)',
          trend: '+10.1% (High-Normal Shift)',
          clinicalSummary: 'Remains below pre-diabetes diagnostic cutoff (100 mg/dL). Complex carb optimization advised.'
        },
        'cholesterol_total': {
          name: 'Total Cholesterol',
          unit: 'mg/dL',
          values: [192.0, 198.0, 204.0],
          minRef: 125.0,
          maxRef: 200.0,
          color: '#f97316',
          bg: 'rgba(249, 115, 22, 0.15)',
          trend: '+6.2% (Crossed Borderline Threshold)',
          clinicalSummary: 'Slightly above standard 200 mg/dL desirable limit; soluble fiber and physical activity beneficial.'
        },
        'vitamin_d': {
          name: '25-OH Vitamin D',
          unit: 'ng/mL',
          values: [16.2, 19.2, 22.4],
          minRef: 30.0,
          maxRef: 100.0,
          color: '#38bdf8',
          bg: 'rgba(56, 189, 248, 0.15)',
          trend: '+38.3% (Positive Recovery Trajectory)',
          clinicalSummary: 'Progressive recovery from initial deficiency baseline toward 30 ng/mL sufficiency.'
        }
      }
    };

    this.currentAnalyte = 'hemoglobin';

    this.animateCounters();
    this.initChart();
    this.setupListeners();
  }

  animateCounters() {
    const counters = document.querySelectorAll('.stat-counter');
    counters.forEach(counter => {
      const target = parseInt(counter.dataset.target, 10) || 0;
      let current = 0;
      const step = Math.max(1, Math.floor(target / 30));
      const interval = setInterval(() => {
        current += step;
        if (current >= target) {
          counter.textContent = target;
          clearInterval(interval);
        } else {
          counter.textContent = current;
        }
      }, 35);
    });
  }

  initChart() {
    const canvas = document.getElementById('longitudinal-trend-chart');
    if (!canvas || typeof Chart === 'undefined') return;

    this.renderAnalyteChart(this.currentAnalyte);
  }

  renderAnalyteChart(analyteKey) {
    const canvas = document.getElementById('longitudinal-trend-chart');
    if (!canvas) return;

    const info = this.historicalData.datasets[analyteKey] || this.historicalData.datasets['hemoglobin'];

    if (this.chart) {
      this.chart.destroy();
    }

    this.chart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: this.historicalData.years,
        datasets: [
          {
            label: `${info.name} (${info.unit})`,
            data: info.values,
            borderColor: info.color,
            backgroundColor: info.bg,
            borderWidth: 2.5,
            pointBackgroundColor: info.color,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8,
            tension: 0.25,
            fill: true
          },
          {
            label: `Upper Reference Limit (${info.maxRef})`,
            data: [info.maxRef, info.maxRef, info.maxRef],
            borderColor: 'rgba(239, 68, 68, 0.65)',
            borderDash: [5, 5],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false
          },
          {
            label: info.minRef > 0 ? `Lower Reference Limit (${info.minRef})` : '',
            data: [info.minRef, info.minRef, info.minRef],
            borderColor: 'rgba(2, 132, 199, 0.5)',
            borderDash: [5, 5],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false
          }
        ].filter(ds => ds.label !== '')
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#334155',
              font: { size: 12, family: "'Inter', sans-serif" }
            }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} ${info.unit}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: '#f1f5f9' },
            ticks: { color: '#475569', font: { size: 11, weight: '500', family: "'Inter', sans-serif" } }
          },
          y: {
            grid: { color: '#f1f5f9' },
            ticks: { color: '#475569', font: { size: 11, family: "'Inter', sans-serif" } }
          }
        }
      }
    });

    this.renderSummaryStrip(info);
  }

  renderSummaryStrip(info) {
    const summaryEl = document.getElementById('analyte-trajectory-summary');
    if (!summaryEl) return;

    const latestVal = info.values[info.values.length - 1];
    const baselineVal = info.values[0];

    summaryEl.innerHTML = `
      <div class="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
        <span class="text-[10px] text-slate-500 uppercase tracking-wider block mb-0.5">Two-Year Net Drift</span>
        <div class="font-bold text-sm text-slate-900">${info.trend}</div>
        <div class="text-[11px] text-slate-600 mt-1">${baselineVal} ${info.unit} &rarr; ${latestVal} ${info.unit}</div>
      </div>

      <div class="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
        <span class="text-[10px] text-slate-500 uppercase tracking-wider block mb-0.5">Standard Laboratory Interval</span>
        <div class="font-bold text-sm text-teal-700 font-mono">${info.minRef > 0 ? `${info.minRef} - ` : '< '}${info.maxRef} ${info.unit}</div>
        <div class="text-[11px] text-slate-500 mt-1">Platform preserved interval bounds</div>
      </div>

      <div class="p-3.5 rounded-lg bg-slate-50 border border-slate-200">
        <span class="text-[10px] text-slate-500 uppercase tracking-wider block mb-0.5">Clinical Trajectory Context</span>
        <p class="text-[11px] text-slate-700 leading-relaxed">${info.clinicalSummary}</p>
      </div>
    `;
  }

  setupListeners() {
    const selectEl = document.getElementById('select-trend-analyte');
    if (selectEl) {
      selectEl.addEventListener('change', (e) => {
        this.currentAnalyte = e.target.value;
        this.renderAnalyteChart(this.currentAnalyte);
      });
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.DashboardController = new DashboardController();
});
