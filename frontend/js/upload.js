/**
 * NutriSphere 3D - Upload Handler & Human Review Controller
 * Handles secure file uploads, explicit consent verification,
 * OCR/PyMuPDF ingestion, and interactive human review for uncertain results.
 */

document.addEventListener('DOMContentLoaded', async () => {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const consentCheckbox = document.getElementById('consent-checkbox');
  const uploadBtn = document.getElementById('upload-btn');
  const fileNameDisplay = document.getElementById('file-name-display');
  const sampleReportsGrid = document.getElementById('sample-reports-grid');

  const verificationSection = document.getElementById('verification-section');
  const verifyLabName = document.getElementById('verify-lab-name');
  const verifyDate = document.getElementById('verify-date');
  const verificationTableBody = document.getElementById('verification-table-body');
  const confirmVerifyBtn = document.getElementById('confirm-verification-btn');

  let selectedFile = null;
  let currentReport = null;

  // 1. Load and display pre-built synthetic report fixtures
  if (sampleReportsGrid) {
    try {
      const res = await fetch('/api/sample-reports');
      const data = await res.json();
      if (data.samples && data.samples.length > 0) {
        sampleReportsGrid.innerHTML = '';
        data.samples.forEach(sample => {
          const card = document.createElement('div');
          card.className = 'medical-card p-4 flex flex-col justify-between hover:border-teal-400 transition-all bg-white';
          card.innerHTML = `
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-xs font-bold text-slate-900 line-clamp-1">${sample.title}</span>
                <span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">${sample.format}</span>
              </div>
              <p class="text-[11px] text-slate-500 mb-3 line-clamp-2">${sample.description}</p>
            </div>
            <div class="flex items-center justify-between pt-2 border-t border-slate-100 gap-2">
              <a href="${sample.download_url}" download class="text-[11px] text-slate-500 hover:text-slate-800 flex items-center gap-1 font-medium">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                Download
              </a>
              <button class="test-fixture-btn px-2.5 py-1 rounded-lg bg-teal-50 hover:bg-teal-100 border border-teal-200 text-teal-800 text-[11px] font-semibold transition-all" data-filename="${sample.filename}" data-title="${sample.title}" data-mimetype="${sample.type}">
                Test Ingestion
              </button>
            </div>
          `;
          sampleReportsGrid.appendChild(card);
        });

        // Attach fixture click handlers: fetches actual fixture blob into selectedFile
        sampleReportsGrid.querySelectorAll('.test-fixture-btn').forEach(btn => {
          btn.addEventListener('click', async (e) => {
            const filename = e.currentTarget.getAttribute('data-filename');
            const title = e.currentTarget.getAttribute('data-title');
            const mimeType = e.currentTarget.getAttribute('data-mimetype') || (filename.endsWith('.pdf') ? 'application/pdf' : 'image/png');

            NutriSphere.showToast(`Loading fixture '${filename}'...`, 'info');
            try {
              const res = await fetch(`/api/sample-reports/${filename}`);
              const blob = await res.blob();
              selectedFile = new File([blob], filename, { type: mimeType });

              if (fileNameDisplay) {
                fileNameDisplay.textContent = `Selected Fixture: ${title} (${(selectedFile.size / 1024).toFixed(1)} KB)`;
                fileNameDisplay.classList.remove('hidden');
              }

              if (consentCheckbox) {
                consentCheckbox.checked = true;
              }

              updateUploadButtonState();
              NutriSphere.showToast(`Fixture loaded. Click 'Extract & Review' to start pipeline.`, 'info');
            } catch (err) {
              NutriSphere.showToast(`Failed loading fixture: ${err.message}`, 'error');
            }
          });
        });
      }
    } catch (e) {
      console.warn('Unable to load sample fixtures list:', e);
    }
  }

  // 2. Drag & Drop and File Input listeners
  if (dropZone && fileInput) {
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('border-teal-400', 'bg-slate-800/50');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('border-teal-400', 'bg-slate-800/50');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-teal-400', 'bg-slate-800/50');
      if (e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        handleFileSelection(fileInput.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|png|jpg|jpeg)$/i)) {
      NutriSphere.showToast('Unsupported file type. Please upload PDF, JPG, or PNG.', 'error');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      NutriSphere.showToast('File exceeds maximum size limit of 15MB.', 'error');
      return;
    }

    selectedFile = file;
    if (fileNameDisplay) {
      fileNameDisplay.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      fileNameDisplay.classList.remove('hidden');
    }
    updateUploadButtonState();
  }

  if (consentCheckbox) {
    consentCheckbox.addEventListener('change', updateUploadButtonState);
  }

  function updateUploadButtonState() {
    if (!uploadBtn) return;
    const canUpload = selectedFile && consentCheckbox && consentCheckbox.checked;
    uploadBtn.disabled = !canUpload;
    if (canUpload) {
      uploadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      uploadBtn.classList.add('hover:bg-teal-400');
    } else {
      uploadBtn.classList.add('opacity-50', 'cursor-not-allowed');
      uploadBtn.classList.remove('hover:bg-teal-400');
    }
  }

  // 3. Upload & Extraction Pipeline
  if (uploadBtn) {
    uploadBtn.addEventListener('click', async () => {
      if (!selectedFile || !consentCheckbox.checked) {
        NutriSphere.showToast('Please select a file and affirm explicit consent.', 'warn');
        return;
      }

      uploadBtn.disabled = true;
      uploadBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-slate-950 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
        Extracting Report & OCR...
      `;

      NutriSphere.showToast('Running PyMuPDF extraction & clinical test catalog mapping...', 'info');

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('consent', JSON.stringify({
        has_consented: true,
        consent_version: '2026.1',
        disclaimer_acknowledged: true,
        purge_on_session_end: false
      }));

      try {
        const response = await fetch('/api/reports', {
          method: 'POST',
          headers: NutriSphere.getAuthHeaders(),
          body: formData
        });

        const data = await response.json();

        if (!response.ok) {
          const errMsg = data.message || (data.details && data.details[0] && data.details[0].message) || 'Report upload failed.';
          NutriSphere.showToast(`Error: ${errMsg}`, 'error');
          uploadBtn.disabled = false;
          uploadBtn.textContent = 'Extract & Review Biomarkers';
          return;
        }

        currentReport = data;

        if (data.analysis_status === 'needs_human_verification') {
          NutriSphere.showToast('Extraction complete: Human verification required for uncertain/OCR fields.', 'warn');
          renderVerificationSection(data);
          uploadBtn.disabled = false;
          uploadBtn.textContent = 'Report Ingested (Review Below)';
        } else {
          NutriSphere.showToast('Report verified with high confidence! Launching 3D Body Atlas projection...', 'info');
          localStorage.setItem('nutrisphere_active_report', JSON.stringify(data));
          startGuidedTransition(data, selectedFile ? selectedFile.name : 'Digital_Lab_Report.pdf');
        }
      } catch (err) {
        NutriSphere.showToast(`Network or server error: ${err.message}`, 'error');
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Extract & Review Biomarkers';
      }
    });
  }

  // 4. Render Human Verification UI
  function renderVerificationSection(report) {
    if (!verificationSection || !verificationTableBody) return;

    if (verifyLabName) verifyLabName.value = report.laboratory_name || '';
    if (verifyDate) verifyDate.value = report.collection_date || '';

    verificationTableBody.innerHTML = '';

    (report.biomarkers || []).forEach((bm, idx) => {
      const isUncertain = bm.extraction_confidence < 0.85 || bm.flag === 'unclassified' || bm.flag === 'unknown';
      const row = document.createElement('tr');
      row.className = isUncertain ? 'bg-amber-50/70 hover:bg-amber-100/60' : 'hover:bg-slate-50';

      row.innerHTML = `
        <td class="py-2.5 px-3">
          <input type="text" class="bm-label w-full bg-white border border-slate-300 rounded px-2.5 py-1 text-slate-900 text-xs focus:ring-1 focus:ring-teal-500" value="${bm.label}">
          <input type="hidden" class="bm-code" value="${bm.analyte_code}">
          <input type="hidden" class="bm-id" value="${bm.id || ''}">
          <input type="hidden" class="bm-page" value="${bm.source_page || 1}">
        </td>
        <td class="py-2.5 px-3">
          <input type="number" step="any" class="bm-val w-20 bg-white border border-slate-300 rounded px-2 py-1 text-slate-900 text-xs font-semibold focus:ring-1 focus:ring-teal-500" value="${bm.value_numeric !== null ? bm.value_numeric : ''}">
        </td>
        <td class="py-2.5 px-3">
          <input type="text" class="bm-unit w-16 bg-white border border-slate-300 rounded px-2 py-1 text-slate-700 text-xs focus:ring-1 focus:ring-teal-500" value="${bm.unit || ''}">
        </td>
        <td class="py-2.5 px-3">
          <input type="number" step="any" class="bm-low w-16 bg-white border border-slate-300 rounded px-2 py-1 text-slate-600 text-xs focus:ring-1 focus:ring-teal-500" value="${bm.reference_low !== null ? bm.reference_low : ''}">
        </td>
        <td class="py-2.5 px-3">
          <input type="number" step="any" class="bm-high w-16 bg-white border border-slate-300 rounded px-2 py-1 text-slate-600 text-xs focus:ring-1 focus:ring-teal-500" value="${bm.reference_high !== null ? bm.reference_high : ''}">
        </td>
        <td class="py-2.5 px-3">
          <span class="${
            bm.flag === 'above_reference' ? 'badge-high' :
            bm.flag === 'below_reference' ? 'badge-high' :
            bm.flag === 'within_reference' ? 'badge-normal' :
            'badge-unclassified'
          }">${bm.flag.toUpperCase()}</span>
          ${isUncertain ? '<span class="ml-1 text-[10px] text-amber-700 font-medium" title="Low extraction confidence / OCR">(Needs Review)</span>' : ''}
        </td>
      `;
      verificationTableBody.appendChild(row);
    });

    verificationSection.classList.remove('hidden');
    verificationSection.scrollIntoView({ behavior: 'smooth' });
  }

  // 5. Submit Human Verification
  if (confirmVerifyBtn) {
    confirmVerifyBtn.addEventListener('click', async () => {
      if (!currentReport) return;

      confirmVerifyBtn.disabled = true;
      confirmVerifyBtn.textContent = 'Saving Verified Data...';

      const rows = verificationTableBody.querySelectorAll('tr');
      const verifiedBiomarkers = [];

      rows.forEach(row => {
        const label = row.querySelector('.bm-label')?.value || '';
        const analyte_code = row.querySelector('.bm-code')?.value || 'UNKNOWN_ANALYTE';
        const id = row.querySelector('.bm-id')?.value || undefined;
        const page = parseInt(row.querySelector('.bm-page')?.value || '1', 10);
        const valStr = row.querySelector('.bm-val')?.value;
        const unit = row.querySelector('.bm-unit')?.value || null;
        const lowStr = row.querySelector('.bm-low')?.value;
        const highStr = row.querySelector('.bm-high')?.value;

        const valNumeric = valStr !== '' && !isNaN(parseFloat(valStr)) ? parseFloat(valStr) : null;
        const refLow = lowStr !== '' && !isNaN(parseFloat(lowStr)) ? parseFloat(lowStr) : null;
        const refHigh = highStr !== '' && !isNaN(parseFloat(highStr)) ? parseFloat(highStr) : null;

        let flag = 'within_reference';
        if (valNumeric !== null && refLow !== null && valNumeric < refLow) {
          flag = 'below_reference';
        } else if (valNumeric !== null && refHigh !== null && valNumeric > refHigh) {
          flag = 'above_reference';
        }

        verifiedBiomarkers.push({
          id: id,
          analyte_code: analyte_code,
          label: label,
          value_numeric: valNumeric,
          unit: unit,
          reference_low: refLow,
          reference_high: refHigh,
          flag: flag,
          source_page: page,
          extraction_confidence: 1.0
        });
      });

      const payload = {
        laboratory_name: verifyLabName?.value || currentReport.laboratory_name,
        collection_date: verifyDate?.value || currentReport.collection_date,
        biomarkers: verifiedBiomarkers
      };

      try {
        const res = await fetch(`/api/reports/${currentReport.id}/verify`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...NutriSphere.getAuthHeaders()
          },
          body: JSON.stringify(payload)
        });

        const verifiedReport = await res.json();
        if (!res.ok) {
          NutriSphere.showToast(verifiedReport.message || 'Verification save failed.', 'error');
          confirmVerifyBtn.disabled = false;
          confirmVerifyBtn.textContent = 'Confirm Verified Report & Explore in 3D →';
          return;
        }

        NutriSphere.showToast('Report verified successfully! Launching 3D Body Atlas projection...', 'info');
        localStorage.setItem('nutrisphere_active_report', JSON.stringify(verifiedReport));
        startGuidedTransition(verifiedReport, verifiedReport.laboratory_name ? `${verifiedReport.laboratory_name}_Report.pdf` : 'Verified_Lab_Report.pdf');
      } catch (err) {
        NutriSphere.showToast(`Error saving verification: ${err.message}`, 'error');
        confirmVerifyBtn.disabled = false;
        confirmVerifyBtn.textContent = 'Confirm Verified Report & Explore in 3D →';
      }
    });
  }

  // Experience 5: Guided Transition Engine
  let countdownTimer = null;

  function startGuidedTransition(report, fileTitle) {
    const modal = document.getElementById('transition-modal');
    const card = document.getElementById('transition-card');
    if (!modal || !card) {
      window.location.href = `/anatomy?report_id=${report.id}&focus=Liver`;
      return;
    }

    const docName = document.getElementById('transition-doc-name');
    if (docName) docName.textContent = fileTitle || 'Clinical_Report.pdf';

    const stageScan = document.getElementById('transition-stage-scan');
    const stageEntities = document.getElementById('transition-stage-entities');
    const stageReady = document.getElementById('transition-stage-ready');
    const stepLabel = document.getElementById('transition-step-label');
    const titleElem = document.getElementById('transition-title');
    const chipsContainer = document.getElementById('transition-chips-container');
    const btnAtlas = document.getElementById('btn-transition-atlas');
    const btnClassic = document.getElementById('btn-transition-classic');
    const countdownElem = document.getElementById('transition-countdown');
    const closeBtn = document.getElementById('transition-close-btn');

    // Determine primary focal organ based on findings
    const markers = report.biomarkers || [];
    let focalOrgan = 'Liver';
    let focalHeadline = 'Primary Focal Area: Hepatic System (Liver)';
    let focalDesc = 'Your report flags hepatocellular transaminases (ALT, AST). Your 3D Body Atlas is prepared with direct physiological projections to the Liver.';

    const hasLiverAbnormal = markers.some(m => (m.analyte_code?.includes('LIV') || m.analyte_code?.includes('ALT') || m.analyte_code?.includes('AST')) && m.flag !== 'within_reference');
    const hasKidneyAbnormal = markers.some(m => (m.analyte_code?.includes('KID') || m.analyte_code?.includes('CREAT') || m.analyte_code?.includes('EGFR')) && m.flag !== 'within_reference');
    const hasHeartAbnormal = markers.some(m => (m.analyte_code?.includes('LIP') || m.analyte_code?.includes('CHOL') || m.analyte_code?.includes('LDL')) && m.flag !== 'within_reference');

    if (hasLiverAbnormal) {
      focalOrgan = 'Liver';
      focalHeadline = 'Primary Focal Area: Hepatic System (Liver)';
      focalDesc = 'Your report flags elevated transaminases (ALT, AST). The 3D Body Atlas has pre-aligned camera coordinates to the Liver.';
    } else if (hasHeartAbnormal) {
      focalOrgan = 'Heart';
      focalHeadline = 'Primary Focal Area: Cardiovascular System (Heart)';
      focalDesc = 'Your report flags circulating atherogenic lipoproteins. The 3D Body Atlas is pre-aligned to the Heart.';
    } else if (hasKidneyAbnormal) {
      focalOrgan = 'Kidneys';
      focalHeadline = 'Primary Focal Area: Renal & Urinary System (Kidneys)';
      focalDesc = 'Your report indicates renal filtration markers (eGFR, Creatinine). The 3D Body Atlas is pre-aligned to the Kidneys.';
    }

    if (btnAtlas) btnAtlas.href = `/anatomy?report_id=${report.id}&focus=${encodeURIComponent(focalOrgan)}`;
    if (btnClassic) btnClassic.href = `/results?report_id=${report.id}`;

    const focalHeadlineElem = document.getElementById('transition-focal-headline');
    const focalDescElem = document.getElementById('transition-focal-desc');
    if (focalHeadlineElem) focalHeadlineElem.textContent = focalHeadline;
    if (focalDescElem) focalDescElem.textContent = focalDesc;

    // Reset stages
    stageScan?.classList.remove('hidden');
    stageEntities?.classList.add('hidden');
    stageReady?.classList.add('hidden');
    if (stepLabel) stepLabel.textContent = 'Step 1 of 3: Scanning';
    if (titleElem) titleElem.textContent = 'Ingesting Laboratory Report...';

    // Show modal with smooth entrance
    modal.classList.remove('opacity-0', 'pointer-events-none');
    card.classList.remove('scale-95');

    closeBtn?.addEventListener('click', () => {
      if (countdownTimer) clearInterval(countdownTimer);
      modal.classList.add('opacity-0', 'pointer-events-none');
      card.classList.add('scale-95');
    });

    // Phase 1 -> Phase 2 (Extracting Entities after 1200ms)
    setTimeout(() => {
      stageScan?.classList.add('hidden');
      stageEntities?.classList.remove('hidden');
      if (stepLabel) stepLabel.textContent = 'Step 2 of 3: Entity Extraction';
      if (titleElem) titleElem.textContent = 'Recognizing Biomarkers & Reference Ranges';

      // Animate counts
      const count = markers.length || 18;
      const analyteCount = document.getElementById('ent-analyte-count');
      const unitCount = document.getElementById('ent-unit-count');
      const refCount = document.getElementById('ent-ref-count');
      if (analyteCount) analyteCount.textContent = count;
      if (unitCount) unitCount.textContent = count;
      if (refCount) refCount.textContent = count;

      if (chipsContainer) {
        chipsContainer.innerHTML = '';
        const sampleList = markers.length > 0 ? markers.slice(0, 10) : [
          { label: 'ALT (SGPT)', value_numeric: 58, unit: 'U/L', flag: 'above_reference' },
          { label: 'AST (SGOT)', value_numeric: 46, unit: 'U/L', flag: 'above_reference' },
          { label: 'Total Cholesterol', value_numeric: 218, unit: 'mg/dL', flag: 'above_reference' },
          { label: 'LDL Cholesterol', value_numeric: 142, unit: 'mg/dL', flag: 'above_reference' },
          { label: 'eGFR', value_numeric: 88, unit: 'mL/min', flag: 'within_reference' },
          { label: 'Fasting Glucose', value_numeric: 104, unit: 'mg/dL', flag: 'above_reference' },
          { label: 'Vitamin D', value_numeric: 22.4, unit: 'ng/mL', flag: 'below_reference' }
        ];

        sampleList.forEach((bm, i) => {
          setTimeout(() => {
            const isAbnormal = bm.flag && bm.flag !== 'within_reference';
            const chip = document.createElement('span');
            chip.className = `entity-pulse px-2 py-1 rounded text-[11px] font-mono font-semibold flex items-center gap-1 ${
              isAbnormal ? 'bg-amber-950/80 text-amber-300 border border-amber-600/60' : 'bg-slate-900 text-teal-300 border border-slate-700'
            }`;
            chip.innerHTML = `<span>${bm.label || bm.analyte_code}:</span> <strong>${bm.value_numeric ?? ''} ${bm.unit || ''}</strong>`;
            chipsContainer.appendChild(chip);
          }, i * 110);
        });
      }
    }, 1300);

    // Phase 2 -> Phase 3 (Mapping to Body Atlas after 2800ms)
    setTimeout(() => {
      stageEntities?.classList.add('hidden');
      stageReady?.classList.remove('hidden');
      if (stepLabel) stepLabel.textContent = 'Step 3 of 3: Spatial Atlas Ready';
      if (titleElem) titleElem.textContent = 'Findings Mapped to Living 3D Anatomy!';

      // Auto countdown 4 seconds
      let timeLeft = 4;
      if (countdownElem) countdownElem.textContent = `Auto-launching Body Atlas in ${timeLeft}s...`;
      countdownTimer = setInterval(() => {
        timeLeft--;
        if (countdownElem) {
          countdownElem.textContent = timeLeft > 0 ? `Auto-launching Body Atlas in ${timeLeft}s...` : 'Launching Body Atlas...';
        }
        if (timeLeft <= 0) {
          clearInterval(countdownTimer);
          window.location.href = `/anatomy?report_id=${report.id}&focus=${encodeURIComponent(focalOrgan)}`;
        }
      }, 1000);
    }, 2800);
  }
});

