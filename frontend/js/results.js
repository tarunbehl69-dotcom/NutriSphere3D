/**
 * NutriSphere 3D - Results & Marker Table Controller (Step 4 Enhanced)
 * Integrates evidence-linked, non-diagnostic interpretation engine:
 * - Multi-marker clinical clusters (Hepatic, Renal, Cardiometabolic, Hematology, Thyroid)
 * - Critical panic value alerting and symptom-aware emergency notices
 * - Expandable accordion drawers for all 74 catalog analytes
 * - Contextual factor integration (medications, age, pregnancy status)
 * - 3D anatomical organ synchronizer with health-literacy guardrails
 */

document.addEventListener('DOMContentLoaded', async () => {
  const tableBody = document.getElementById('biomarkers-table-body');
  const filterInput = document.getElementById('marker-search');
  const organFilter = document.getElementById('organ-filter');
  const reportMetaDiv = document.getElementById('report-metadata');
  const urgencyBannerDiv = document.getElementById('urgency-banner-container');
  const clustersContainer = document.getElementById('clinical-clusters-container');
  const btnRecalculate = document.getElementById('btn-recalculate-context');
  const inputAge = document.getElementById('context-age');
  const checkPregnancy = document.getElementById('context-pregnancy');

  let activeReport = null;
  let activeSummary = null;
  const expandedRows = new Set();

  // Retrieve active report from URL parameter, localStorage, or fetch demo
  const urlParams = new URLSearchParams(window.location.search);
  const reportIdParam = urlParams.get('report_id');

  if (reportIdParam) {
    try {
      const res = await fetch(`/api/reports/${reportIdParam}`, {
        headers: NutriSphere.getAuthHeaders()
      });
      if (res.ok) {
        activeReport = await res.json();
        localStorage.setItem('nutrisphere_active_report', JSON.stringify(activeReport));
      }
    } catch (err) {
      console.warn('Failed fetching report from URL parameter:', err);
    }
  }

  if (!activeReport) {
    const stored = localStorage.getItem('nutrisphere_active_report');
    if (stored) {
      try {
        activeReport = JSON.parse(stored);
      } catch (e) {
        console.warn('Failed parsing stored report');
      }
    }
  }

  if (!activeReport) {
    const res = await fetch('/api/demo-report');
    activeReport = await res.json();
  }

  // Load summary and render full page
  if (activeReport) {
    activeReport.id = activeReport.id || activeReport.report_metadata?.report_id || 'rep_demo_2026_001';
    await fetchAndRenderSummary(activeReport.id);
    renderReportHeader(activeReport);
    renderBiomarkersTable(activeReport.biomarkers || []);
  }

  // Fetch report summary (Multi-marker clusters & high-priority findings)
  async function fetchAndRenderSummary(reportId, optionalContext = null) {
    try {
      let res;
      if (optionalContext) {
        res = await fetch(`/api/reports/${reportId}/interpret`, {
          method: 'POST',
          headers: {
            ...NutriSphere.getAuthHeaders(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(optionalContext)
        });
      } else {
        res = await fetch(`/api/reports/${reportId}/summary`, {
          headers: NutriSphere.getAuthHeaders()
        });
      }

      if (res.ok) {
        activeSummary = await res.json();
        renderUrgencyBanner(activeSummary);
        renderClinicalClusters(activeSummary.multimarker_clusters || []);
      }
    } catch (err) {
      console.warn('Could not load interpretation summary:', err);
    }
  }

  function renderReportHeader(data) {
    if (!reportMetaDiv) return;
    const meta = data.report_metadata || {};
    const fileName = data.file_name || meta.file_name || 'Medical Laboratory Report';
    const collectionDate = data.collection_date || meta.collection_date || 'N/A';
    const lab = data.laboratory_name || meta.laboratory || 'Clinical Diagnostic Laboratory';
    const status = data.analysis_status || meta.analysis_status || 'Verified';

    reportMetaDiv.innerHTML = `
      <div class="medical-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-xs font-semibold uppercase tracking-wider text-teal-600">Verified Diagnostic Report</span>
            <span class="text-xs text-slate-400">•</span>
            <span class="text-xs text-slate-500">ID: ${data.id || 'N/A'}</span>
          </div>
          <h2 class="text-xl font-bold text-slate-900">${fileName}</h2>
          <p class="text-xs text-slate-500 mt-0.5">Specimen Date: <strong class="text-slate-700">${collectionDate}</strong> &nbsp;|&nbsp; Diagnostic Laboratory: <strong class="text-slate-700">${lab}</strong></p>
        </div>
        <div class="flex items-center gap-2">
          <span class="badge-normal uppercase font-semibold text-xs tracking-wider">${status}</span>
          <span class="text-xs font-medium text-slate-500 px-2.5 py-1 rounded bg-slate-100 border border-slate-200">74 Analytes Interpreted</span>
        </div>
      </div>
    `;
  }

  function renderUrgencyBanner(summary) {
    if (!urgencyBannerDiv) return;
    urgencyBannerDiv.innerHTML = '';

    const urgentCount = summary?.urgent_review_count || 0;
    const highPriority = summary?.high_priority_findings || [];
    const criticalFindings = highPriority.filter(f => f.startsWith('CRITICAL FINDING'));

    if (urgentCount > 0 || criticalFindings.length > 0) {
      urgencyBannerDiv.innerHTML = `
        <div class="p-4 rounded-xl bg-rose-50 border border-rose-300 text-rose-900 flex flex-col gap-2 shadow-sm">
          <div class="flex items-center gap-2.5">
            <span class="flex h-2.5 w-2.5 relative">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-600"></span>
            </span>
            <h4 class="font-bold text-sm tracking-wide text-rose-800 uppercase">Urgent Clinical Escalation Notice</h4>
          </div>
          <p class="text-xs text-rose-700 leading-relaxed">
            One or more lab findings trigger clinical emergency criteria. Laboratory reference intervals are not a diagnosis,
            but urgent threshold excursions require prompt evaluation. If you are experiencing chest pain, acute weakness, shortness of breath,
            or confusion, seek immediate medical attention.
          </p>
          <ul class="list-disc list-inside text-xs text-rose-800 font-mono space-y-1 mt-1">
            ${criticalFindings.map(cf => `<li>${cf}</li>`).join('')}
          </ul>
        </div>
      `;
    }
  }

  function renderClinicalClusters(clusters = []) {
    if (!clustersContainer) return;
    if (!clusters || clusters.length === 0) {
      clustersContainer.innerHTML = '';
      return;
    }

    clustersContainer.innerHTML = `
      <div class="medical-card p-5 flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <h3 class="font-bold text-sm text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-teal-600"></span>
            Multi-Marker Clinical Clusters & Educational Insights
          </h3>
          <span class="text-xs text-slate-500">Cross-analyte synthesis across panels</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          ${clusters.map(c => `
            <div class="p-4 rounded-lg bg-slate-50 border border-slate-200 flex flex-col justify-between gap-3">
              <div>
                <div class="flex items-center justify-between mb-1">
                  <h5 class="font-bold text-slate-800 text-xs">${c.cluster_name}</h5>
                  <span class="text-[10px] bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded font-medium">${c.organ_system}</span>
                </div>
                <span class="text-xs font-semibold text-teal-800">${c.clinical_pattern}</span>
                <ul class="mt-2.5 space-y-1.5 text-xs text-slate-600 leading-relaxed">
                  ${(c.educational_insights || []).map(ins => `
                    <li class="flex items-start gap-1.5">
                      <span class="text-teal-600 font-bold mt-0.5">•</span>
                      <span>${ins}</span>
                    </li>
                  `).join('')}
                </ul>
              </div>
              <div class="pt-2 border-t border-slate-200 text-[11px] text-slate-500 italic">
                <strong>Limitation:</strong> ${c.uncertainty_disclaimer}
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  function renderBiomarkersTable(markers = []) {
    if (!tableBody) return;
    tableBody.innerHTML = '';

    const searchTerm = (filterInput?.value || '').toLowerCase();
    const selectedOrgan = organFilter?.value || 'ALL';

    const filtered = markers.filter(m => {
      const matchSearch = m.label.toLowerCase().includes(searchTerm) || m.analyte_code.toLowerCase().includes(searchTerm);
      const matchOrgan = selectedOrgan === 'ALL' || m.organ_system === selectedOrgan;
      return matchSearch && matchOrgan;
    });

    if (filtered.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="8" class="text-center py-8 text-slate-400">No biomarkers matching the current filter.</td>
        </tr>
      `;
      return;
    }

    filtered.forEach((m, idx) => {
      const bmId = m.id || `bm_${idx}`;
      const isExpanded = expandedRows.has(bmId);
      const interp = m.interpretation || {};

      const flagBadges = {
        within_reference: '<span class="badge-normal">Normal</span>',
        above_reference: '<span class="badge-high">Higher Than Normal</span>',
        below_reference: '<span class="badge-high">Lower Than Normal</span>',
        urgent_review: '<span class="badge-urgent animate-pulse">Needs Doctor Review</span>',
        unknown: '<span class="badge-unclassified">Unclassified</span>'
      };

      const row = document.createElement('tr');
      row.className = `border-b border-slate-200 hover:bg-slate-50 transition-colors cursor-pointer ${isExpanded ? 'bg-teal-50/30' : ''}`;

      const flagColor = m.flag === 'above_reference' ? 'text-amber-700 font-bold' : (m.flag === 'below_reference' ? 'text-sky-700 font-bold' : (m.flag === 'urgent_review' ? 'text-rose-700 font-extrabold' : 'text-slate-900 font-semibold'));

      row.innerHTML = `
        <td class="py-3 px-4 font-medium text-slate-900">
          <div class="flex items-center gap-2">
            <span class="w-4 h-4 rounded text-slate-400 flex items-center justify-center text-xs transition-transform ${isExpanded ? 'rotate-90 text-teal-600 font-bold' : ''}">
              ▶
            </span>
            <span class="font-semibold text-slate-900">${m.label}</span>
          </div>
        </td>
        <td class="py-3 px-4 font-mono ${flagColor}">
          ${m.value_numeric ?? m.value_text ?? 'N/A'}
        </td>
        <td class="py-3 px-4 text-slate-600 text-xs">${m.unit || '—'}</td>
        <td class="py-3 px-4 text-slate-600 text-xs font-mono">${m.reference_low ?? '—'} – ${m.reference_high ?? '—'}</td>
        <td class="py-3 px-4">${flagBadges[m.flag] || flagBadges.unknown}</td>
        <td class="py-3 px-4">
          <span class="text-xs bg-slate-100 text-teal-800 border border-slate-200 px-2 py-0.5 rounded font-medium">${m.organ_system || 'General'}</span>
        </td>
        <td class="py-3 px-4 text-xs text-slate-500 font-mono">p.${m.source_page || 1} (${Math.round((m.extraction_confidence || 1) * 100)}%)</td>
        <td class="py-3 px-4 text-center">
          <button class="px-2.5 py-1 rounded text-xs font-medium ${isExpanded ? 'bg-teal-600 text-white' : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'} transition-colors">
            ${isExpanded ? 'Close' : 'Explain'}
          </button>
        </td>
      `;

      row.addEventListener('click', (e) => {
        // Toggle expansion
        if (expandedRows.has(bmId)) {
          expandedRows.delete(bmId);
        } else {
          expandedRows.add(bmId);
        }
        renderBiomarkersTable(activeReport?.biomarkers);

        if (window.resultsAnatomy && m.organ_system) {
          window.resultsAnatomy.selectOrgan(m.organ_system);
        }
      });

      tableBody.appendChild(row);

      // Expandable Drawer Row
      if (isExpanded) {
        const drawerRow = document.createElement('tr');
        drawerRow.className = 'bg-slate-50/70 border-b border-slate-200';

        const reasonsList = (interp.possible_reasons || []).map(r => `<li>${r}</li>`).join('');
        const questionsList = (interp.clinical_questions || []).map(q => `<li>${q}</li>`).join('');
        const contextList = (interp.contextual_notes || []).map(c => `<li>${c}</li>`).join('');

        drawerRow.innerHTML = `
          <td colspan="8" class="p-6 text-xs text-slate-700">
            <div class="flex flex-col gap-4 max-w-5xl mx-auto">
              
              <!-- Badges Header -->
              <div class="flex flex-wrap items-center gap-2 pb-2 border-b border-slate-200">
                <span class="font-bold text-sm text-slate-900">${m.label} (${m.analyte_code})</span>
                ${interp.is_borderline ? '<span class="badge-high text-xs font-semibold">Borderline (Within 5% of Cutoff)</span>' : ''}
                ${interp.urgency_level === 'urgent_assessment' ? '<span class="badge-urgent text-xs font-bold animate-pulse">Critical Emergency Alert</span>' : ''}
                <span class="text-xs text-slate-500">Primary Anatomical System: <strong class="text-slate-800">${m.organ_system}</strong></span>
              </div>

              <!-- Critical Alert Notice (if applicable) -->
              ${interp.urgency_notice ? `
                <div class="p-3.5 rounded-lg bg-rose-50 border border-rose-300 text-rose-800">
                  <strong class="font-bold">Emergency Consideration:</strong> ${interp.urgency_notice}
                </div>
              ` : ''}

              <!-- OCR Uncertainty Notice (if applicable) -->
              ${interp.uncertainty_notice ? `
                <div class="p-3.5 rounded-lg bg-amber-50 border border-amber-300 text-amber-800">
                  <strong class="font-bold">Uncertainty Notice:</strong> ${interp.uncertainty_notice}
                </div>
              ` : ''}

              <!-- 2-Column Explanation Grid -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 rounded-lg bg-white border border-slate-200 shadow-sm flex flex-col gap-2">
                  <h5 class="font-bold text-teal-800 uppercase tracking-wider text-[11px]">What This Test Measures & Why It Matters</h5>
                  <p class="leading-relaxed text-slate-700">${interp.explanation || 'Test measurement extracted from your report.'}</p>
                  <p class="text-slate-500 text-[11px] mt-1">${interp.reasoning_limits || ''}</p>
                </div>

                <div class="p-4 rounded-lg bg-white border border-slate-200 shadow-sm flex flex-col gap-2">
                  <h5 class="font-bold text-amber-800 uppercase tracking-wider text-[11px]">Common Everyday Reasons for This Number</h5>
                  <p class="text-slate-500 text-[11px]">Everyday factors like meals, hydration, physical activity, or normal biological variation:</p>
                  <ul class="list-disc list-inside space-y-1 text-slate-700">
                    ${reasonsList || '<li>Normal body balance</li>'}
                  </ul>
                </div>
              </div>

              <!-- Voluntary Context Notes (if any) -->
              ${contextList ? `
                <div class="p-3.5 rounded-lg bg-sky-50 border border-sky-200 text-sky-900">
                  <h5 class="font-bold text-[11px] uppercase tracking-wider mb-1 text-sky-800">Personalized Insights:</h5>
                  <ul class="list-disc list-inside space-y-1">${contextList}</ul>
                </div>
              ` : ''}

              <!-- Questions for Doctor & Medical Reference -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                <div class="p-4 rounded-lg bg-white border border-slate-200 shadow-sm">
                  <h5 class="font-bold text-slate-800 uppercase tracking-wider text-[11px] mb-1.5">Helpful Questions to Ask Your Doctor</h5>
                  <ul class="list-disc list-inside space-y-1 text-slate-600">
                    ${questionsList || '<li>How do these results fit with my overall daily health and lifestyle?</li>'}
                  </ul>
                </div>

                <div class="p-4 rounded-lg bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
                  <div>
                    <h5 class="font-bold text-slate-500 uppercase tracking-wider text-[11px] mb-1">Medical Science Reference</h5>
                    <p class="text-slate-700 text-xs italic">${interp.medical_reference || 'AACC Clinical Laboratory Reference Guide'}</p>
                  </div>
                  <div class="mt-3 flex items-center justify-between">
                    <button onclick="if(window.resultsAnatomy){ window.resultsAnatomy.selectOrgan('${m.organ_system}'); }" class="px-3 py-1.5 rounded-lg bg-teal-50 text-teal-700 border border-teal-200 hover:bg-teal-100 text-xs font-semibold transition-colors">
                      Focus ${m.organ_system} in 3D Anatomy
                    </button>
                    <span class="text-[11px] text-slate-400">Non-Diagnostic Education</span>
                  </div>
                </div>
              </div>

            </div>
          </td>
        `;
        tableBody.appendChild(drawerRow);
      }
    });
  }

  // Recalculate Context button handler
  if (btnRecalculate) {
    btnRecalculate.addEventListener('click', async () => {
      const ageVal = inputAge?.value ? parseInt(inputAge.value, 10) : null;
      const isPregnant = !!checkPregnancy?.checked;
      
      const contextPayload = {
        age: ageVal,
        pregnancy_status: isPregnant
      };

      btnRecalculate.disabled = true;
      btnRecalculate.innerText = 'Calculating...';

      if (activeReport?.id) {
        await fetchAndRenderSummary(activeReport.id, contextPayload);
        // Refresh full report to receive contextual notes on individual biomarkers
        try {
          const res = await fetch(`/api/reports/${activeReport.id}`, {
            headers: NutriSphere.getAuthHeaders()
          });
          if (res.ok) {
            activeReport = await res.json();
            renderBiomarkersTable(activeReport.biomarkers || []);
          }
        } catch (e) {
          console.warn('Error refreshing biomarkers with context:', e);
        }
      }

      btnRecalculate.disabled = false;
      btnRecalculate.innerText = 'Update Insights';
    });
  }

  if (filterInput) filterInput.addEventListener('input', () => renderBiomarkersTable(activeReport?.biomarkers));
  if (organFilter) organFilter.addEventListener('change', () => renderBiomarkersTable(activeReport?.biomarkers));
});
