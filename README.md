# NutriSphere 3D — Medical Report Intelligence & Interactive 3D Anatomy

> **University Product Management Capstone Project (PM02)**  
> **Interactive 3D Medical Report Explanation & Culturally Grounded Lifestyle Intelligence Platform**  
> *Stack:* HTML5 + Tailwind CSS + JavaScript + Three.js + Chart.js + Python 3.14 + FastAPI + SQLite (WAL Mode) + PyMuPDF + Pillow + Pytest

[![Pytest Suite](https://img.shields.io/badge/pytest-100%2F100%20passing-10b981.svg)](backend/tests/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.14-38bdf8.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-14b8a6.svg)](https://fastapi.tiangolo.com)
[![Three.js](https://img.shields.io/badge/Three.js-r128-f59e0b.svg)](https://threejs.org)
[![License](https://img.shields.io/badge/Academic-Class%20Demonstration-8b5cf6.svg)]()

---

## 1. Executive Summary & Vision

Laboratory test reports are among the most common and vital medical artifacts patients receive, yet they remain notoriously difficult for laypeople to decipher. Patients are often confronted with intimidating acronyms, confusing units, reference ranges without clinical context, and isolated figures devoid of physiological perspective.

**NutriSphere 3D** resolves this health literacy gap. It transforms static laboratory PDFs and scanned slips into an immersive, interactive 3D human anatomy experience. By mapping 74 biomarkers across 14 clinical panels directly to biological organ systems, patients can intuitively visualize where in the body their tests originate, understand what the numbers indicate, track longitudinal health trajectories across multiple years, and explore culturally tailored Indian dietary suggestions—all backed by strict zero-hallucination clinical guardrails that firmly avoid diagnostic overreach or false "safe drinking allowances."

---

## 2. Architecture & Technology Stack

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Client Layer (Browser)                                │
│   • HTML5, Tailwind CSS, Vanilla Modern JS (ES6+)                               │
│   • Three.js r128 (Procedural 3D Organ Geometries, Raycasting, Breathing Sine)  │
│   • Chart.js (Longitudinal Trajectory Tracking & Weekly Ethanol Intake)         │
│   • Floating Grounded AI Assistant Drawer (/js/chat.js)                         │
│   • 10-Step Guided Academic Demo Walkthrough Tour (/js/presentation.js)         │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ HTTP / JSON / Multipart File Streams
┌──────────────────────────────────────▼──────────────────────────────────────────┐
│                           FastAPI Application Server                            │
│  ├── Static UI Page Mounts (/, /upload, /results, /dashboard, /alcohol, /nutr)  │
│  ├── Ingestion & OCR Pipeline (PyMuPDF vector parser + Pillow OCR engine)       │
│  ├── Clinical Test Catalog & Normalizer (74 Analytes Across 14 Clinical Panels) │
│  ├── Multi-Marker Cross-Analyte Clustering Engine (Hepatic, Renal, Metabolic)   │
│  ├── Pure Ethanol Biochemistry Calculator (Vol * ABV * 0.789 g/mL)             │
│  ├── Food-First Indian Nutrition Service (Vegetarian, Vegan, Jain, Non-Veg)     │
│  ├── Grounded AI Assistant Service (/api/chat/explain with strict lab citation) │
│  └── Conspicuous Privacy & Data Purge Controller (/api/reports/{id})            │
└──────────────────────────────────────┬──────────────────────────────────────────┘
                                       │ Direct Connection / WAL Journal Mode
┌──────────────────────────────────────▼──────────────────────────────────────────┐
│                     Local-First SQLite Database Engine                          │
│   nutrisphere3d.db (users, reports, biomarkers, medications, audit_events,       │
│   test_catalog, alcohol_intake_records)                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Feature Pillars

### A. Authentic 3D Anatomy Explorer (`/anatomy`, `/results`, `/`)
- **Authentic Anatomical glTF/GLB Models:** Replaced artificial geometric primitives with genuine anatomical meshes sourced from NIH 3D Print Exchange and BodyParts3D (CC BY 4.0), including:
  - `skin.glb` — Translucent human body shell with adjustable opacity
  - `brain.glb` — Cerebral cortex & cranial structure
  - `heart.glb` — Detailed 4-chamber cardiac anatomy & great vessels
  - `lungs.glb` — Bilateral pulmonary lobes & tracheobronchial arborization
  - `liver.glb` — Hepatic lobes and falciform structure
  - `kidneys.glb` — Bilateral renal anatomy and adrenal caps
  - `stomach.glb` — Gastric reservoir & curvature
  - `pancreas.glb` — Pancreatic head, body, and tail
  - `intestine.glb` — Enteric gastrointestinal tract
  - `spine.glb` — Vertebral column & axial musculoskeletal support
- **Clinical Interaction Engine:**
  - OrbitControls with smooth inertia damping, polar constraints, and intuitive pan/zoom
  - Raycaster organ picking with instant hover cursor feedback and interactive highlights
  - Smooth camera focusing and zoom tweening powered by GSAP
  - Organ isolation mode (fading peripheral structures) and body opacity toggle
  - Dedicated full-screen **3D Anatomy Explorer (`/anatomy`)** with 3-column clinical layout and verified biomarker sync.
- **Accessible 2D Fallback:** High-contrast SVG organ matrix for environments without WebGL hardware acceleration.

### B. Ingestion & Human Review Pipeline (`/upload`)
- Multi-format ingestion supporting vector PDFs, scanned documents, and image formats (JPG, PNG) up to 15MB.
- Explicit affirmative user consent enforcement prior to processing.
- Source-page traceability, extraction confidence scoring, and interactive human verification table.

### C. 74 Analytes Across 14 Clinical Panels
- Complete coverage: Hematology (CBC), Liver Function, Kidney & Electrolytes, Diabetes/Glycemia, Lipid Panel, Thyroid, Vitamins/Minerals, Cardiac, Inflammatory Markers, Urine Studies, Coagulation, Bone Profile, Metabolic, and Reproductive Hormones.
- Analyte synonym dictionary and unit normalization preserving laboratory-specific reference intervals.

### D. Multi-Year Longitudinal Health Dashboard (`/dashboard`)
- Multi-year trajectory analytics comparing 2024 baseline, 2025 follow-up, and 2026 latest reports.
- Interactive Chart.js trend curves for Hemoglobin, ALT, Fasting Glucose, Total Cholesterol, and Vitamin D3.
- Shaded laboratory reference bands, trajectory classification tags, and animated stat counters.

### E. Alcohol & Hepatic Health Module (`/alcohol`)
- Dedicated 3D Three.js Liver Model with organic lobular geometry, hepatic vessels, and click-to-zoom controls.
- Formula-based pure ethanol calculator:
  $$\text{Pure Ethanol (g)} = \text{Volume (mL)} \times \frac{\text{ABV}\%}{100} \times 0.789$$
- Dual standard drink equivalents: WHO Standard (10g ethanol) and US Standard (14g ethanol).
- Report transaminase cross-linking (ALT, AST, de Ritis $AST/ALT$ ratio, GGT, Bilirubin, MCV).
- Pharmacovigilance panel highlighting lethal drug interactions (Acetaminophen/NAPQI, Sedatives, Metformin).
- **Strict Clinical Guardrail:** Normal transaminases do NOT imply safe alcohol consumption; early steatosis occurs with standard enzymes.

### F. Food-First Indian Nutrition Guide (`/nutrition`)
- Dietary pattern tabs: Indian Vegetarian, Indian Vegan, Jain, and Non-Vegetarian.
- **Strict Jain Rules:** Excludes all underground root vegetables (potatoes, onions, garlic, carrots, beetroots); emphasizes sprouted moong, lauki, cumin, hing, and turmeric.
- Multi-select allergy filters (Dairy-Free, Gluten-Free, Peanut-Free, Soy-Free).
- Report-linked dietary adaptations (e.g., Amla + Palak for iron support; Ragi + Karela for glycemic regulation; Turmeric + Lauki for hepatic recovery).

### G. Zero-Hallucination Grounded AI Report Assistant
- Floating slide-out drawer accessible across all pages.
- Connected to `/api/chat/explain` with prompt constraints requiring explicit citation of verified lab numbers, units, and intervals.
- Resilient deterministic clinical knowledge fallback when external LLM APIs are offline.

### H. Professor Presentation Demo Mode
- Integrated 10-step academic tour walking evaluators through the entire architectural depth, technical decisions, and clinical safety measures.

---

## 4. Directory Structure

```text
nutrisphere3d/
├── backend/
│   ├── main.py                  # FastAPI server, UI routes, and REST API endpoints
│   ├── database.py              # SQLite connection (WAL mode, PRAGMAs, foreign keys)
│   ├── models.py                # Pydantic v2 data models and request/response schemas
│   ├── seed_data.py             # Fixture loader for test catalog and synthetic reports
│   ├── services/
│   │   ├── parser.py            # Vector PDF and Vision OCR ingestion engine
│   │   ├── normalizer.py        # 74-analyte synonym matching & unit normalization
│   │   ├── interpreter.py       # Evidence-linked non-diagnostic medical interpreter
│   │   ├── nutrition.py         # Food-first Indian nutrition & allergy filtering
│   │   ├── alcohol.py           # Ethanol physics, hepatic clearance, drug interactions
│   │   ├── ai_assistant.py      # Grounded AI report conversational Q&A service
│   │   └── auth.py              # Server-validated authentication & PBKDF2 hashing
│   └── tests/
│       ├── test_scaffold.py     # Initial scaffold and database tests (13 tests)
│       ├── test_step1_catalog_and_db.py       # Catalog & normalization suite (13 tests)
│       ├── test_step2_schemas_and_privacy.py  # Pydantic schemas & privacy suite (15 tests)
│       ├── test_step3_upload_pipeline.py      # Upload & extraction pipeline (16 tests)
│       ├── test_step4_interpreter.py          # Clinical interpretation engine (24 tests)
│       └── test_step5_master_suite.py         # Step 5 master product suite (19 tests)
├── frontend/
│   ├── index.html               # Medical SaaS landing page with 3D hero viewer
│   ├── anatomy.html             # Dedicated 3D Anatomical Explorer (3-column layout)
│   ├── upload.html              # Secure upload & interactive human review interface
│   ├── results.html             # Quest/Epic clinical table & synced 3D organ explorer
│   ├── dashboard.html           # Longitudinal trend graphs & multi-year comparison
│   ├── alcohol.html             # Dedicated Alcohol & Hepatic Health 3D module
│   ├── nutrition.html           # Dedicated Food-First Indian Nutrition Guide
│   ├── css/
│   │   └── styles.css           # Clinical Medical SaaS design tokens (Teal, Slate, White)
│   ├── models/                  # Authentic anatomical 3D assets (Binary glTF 2.0 / GLB)
│   │   ├── skin.glb, brain.glb, heart.glb, lungs.glb, liver.glb,
│   │   └── kidneys.glb, stomach.glb, pancreas.glb, intestine.glb, spine.glb
│   └── js/
│       ├── lib/                 # Local offline Three.js libraries (GLTFLoader, OrbitControls, GSAP)
│       ├── app.js               # Global client application, toast notifications
│       ├── anatomy.js           # GLTF loader, OrbitControls, Raycasting, and organ focus
│       ├── upload.js            # Ingestion dropzone, consent check, review table
│       ├── results.js           # Biomarker tables, organ filter sync, panic alerts
│       ├── dashboard.js         # Chart.js multi-year longitudinal trend graphs
│       ├── alcohol.js           # 3D liver model, pure ethanol calculator, intake log
│       ├── nutrition.js         # Diet pattern switcher, allergy filter, meal cards
│       ├── chat.js              # Floating grounded AI report assistant drawer
│       └── presentation.js      # 10-step academic demonstration walkthrough tour
├── data/
│   ├── test_catalog_seed.csv    # 74-analyte clinical catalog seed
│   ├── demo_report.json         # Synthetic patient fixture (rep_demo_2026_001)
│   ├── historical_reports.json  # Multi-year longitudinal series (2024, 2025, 2026)
│   └── sample_reports/          # Demonstration files for manual upload testing
├── nutrisphere3d.db             # Local SQLite database file
├── requirements.txt             # Python project dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # Product architecture & user manual
```

---

### 3D Model Provenance & Attribution (CC BY 4.0 & CC BY-SA 4.0)

All 3D anatomical models integrated into NutriSphere 3D are open-source scientific biomedical meshes utilized in compliance with their open licenses:

- **Full Human Skeleton & Master Visceral Assembly:**
  - **Source:** [BodyParts3D](http://lifesciencedb.jp/bp3d/), The Database Center for Life Science (DBCLS), Japan & [Z-Anatomy](https://www.z-anatomy.com/) (CC BY-SA 4.0 / CC BY-SA 2.1 JP).
  - **Nomenclature Standard:** Terminologia Anatomica 2 (TA2) clinical nomenclature.
  - **Integrated Master Systems:**
    - `skeletal_male.glb`: Full authentic human skeleton (Skull, Cranium, Spine, Ribcage, Pelvis, Femur, Tibia, Arms, Feet)
    - `cardiovascular_male.glb`: Heart (4 chambers, Atria, Ventricles, Ascending Aorta, Great Vessels)
    - `respiratory_male.glb`: Bilateral pulmonary lobes and tracheobronchial arborization
    - `digestive_male.glb`: Hepatic liver lobes, stomach, pancreas, and enteric intestinal tract
    - `renal_male.glb`: Bilateral kidneys, renal pelvis, ureters, and urinary bladder
    - `endocrine_male.glb`: Thyroid gland, adrenal glands, and pituitary
    - `nervous_male.glb`: Brain, cerebrum, cerebellum, and spinal cord
    - `regional_male.glb`: Translucent human body surface envelope
- **NIH 3D Print Exchange (NIH Visible Human Project):**
  - **Source:** [NIH 3D Print Exchange](https://3dprint.nih.gov/), National Institutes of Health / National Library of Medicine.
  - Dedicated models: `VH_M_Heart.glb` (NIH 3DPX-021000), `VH_M_Liver.glb` (NIH 3DPX-021007), `VH_M_Kidney_L.glb` (NIH 3DPX-021001), `realistic_stomach.glb` (NIH 3DPX-021124).
- **Decompression Acceleration:** Mesh data is decoded client-side using Google Draco WASM (`/draco/gltf/draco_decoder.wasm`) for smooth 60 FPS WebGL rendering without procedural primitives.
- **Public Attribution:** Displayed dynamically in the 3D viewport attribution pill on both `/anatomy` and `/` routes.

---

## 5. Quickstart & Installation

### Step A: Prerequisites
- **Python 3.10+** (Tested on Python 3.14.6)
- Modern web browser with WebGL support (Chrome, Safari, Firefox, Edge)

### Step B: Set Up Virtual Environment & Dependencies
```bash
cd nutrisphere3d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step C: Launch Application Server (Dedicated Port 8080)
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8080
```
> **Port Isolation:** NutriSphere 3D runs on port **8080** to maintain total network separation from other local projects (such as LMS / LearnLoop on 8000/8001).

### Step D: Access the Web Application
Open your browser to:
- **Landing Page & 3D Hero:** [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
- **Dedicated 3D Anatomy Explorer:** [http://127.0.0.1:8080/anatomy](http://127.0.0.1:8080/anatomy)
- **Medical Report Upload & Review:** [http://127.0.0.1:8080/upload](http://127.0.0.1:8080/upload)
- **Biomarkers & 3D Anatomy Table:** [http://127.0.0.1:8080/results](http://127.0.0.1:8080/results)
- **Longitudinal Dashboard & Trends:** [http://127.0.0.1:8080/dashboard](http://127.0.0.1:8080/dashboard)
- **Alcohol & Your Health Module:** [http://127.0.0.1:8080/alcohol](http://127.0.0.1:8080/alcohol)
- **Food-First Indian Nutrition Guide:** [http://127.0.0.1:8080/nutrition](http://127.0.0.1:8080/nutrition)
- **Interactive Swagger API Documentation:** [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

---

## 6. Automated Testing Verification (100% Passed)

NutriSphere 3D includes a 100-test automated verification suite covering schemas, database integrity, file validation, OCR parsing, clinical interpretations, longitudinal trends, alcohol mathematics, and cultural nutrition.

Run the complete test suite:
```bash
source .venv/bin/activate
pytest
```

### Test Suite Breakdown (100/100 Passing)
| Test Module | Coverage Area | Tests Passed | Status |
| :--- | :--- | :---: | :---: |
| `test_scaffold.py` | Initial setup, SQLite database connection, PRAGMA checks | 13 / 13 | Passed |
| `test_step1_catalog_and_db.py` | 74-analyte catalog, 14 panels, unit conversions, synonyms | 13 / 13 | Passed |
| `test_step2_schemas_and_privacy.py` | Pydantic v2 models, consent validation, password hashing | 15 / 15 | Passed |
| `test_step3_upload_pipeline.py` | Vector PDF parsing, OCR fallback, file size & type limits | 16 / 16 | Passed |
| `test_step4_interpreter.py` | Non-diagnostic explanations, panic values, multi-marker clusters | 24 / 24 | Passed |
| `test_step5_master_suite.py` | UI routes, pure ethanol physics, Jain diet rules, AI grounding | 19 / 19 | Passed |
| **Total** | **End-to-End System Verification** | **100 / 100** | **100% Passing** |

---

## 7. Clinical Safety, Ethics & Scope Disclosures

1. **Non-Diagnostic Health Literacy:** A laboratory reference interval is not a diagnosis. Normal values cannot rule out underlying conditions, and abnormal values do not confirm pathology. All system outputs are strictly educational.
2. **Preservation of Laboratory Ranges:** Reference ranges vary substantially between testing equipment, reagents, and regional labs. NutriSphere 3D strictly preserves original lab-provided ranges and does not flatten them into a universal standard.
3. **No Guaranteed Safe Alcohol Limits:** Medical research confirms that no laboratory test or mathematical formula can establish a universally safe drinking threshold. The tool provides ethanol density calculations and metabolic education only.
4. **Local-First Privacy Architecture:** No protected health information (PHI) is transmitted to third-party advertisers or external servers. Users retain complete control to purge uploaded files, extracted data, and account records at any time.
5. **Synthetic Academic Data:** All fixtures and demonstration reports contain strictly synthetic medical data created exclusively for academic evaluation.

---

## 8. University Product Management Walkthrough Script

When demonstrating to course instructors or evaluators:
1. Navigate to **[http://127.0.0.1:8080/](http://127.0.0.1:8080/)** and click the **"Demo Tour"** button in the header.
2. The 10-step guided tour will activate, explaining the architectural layers, tech stack decisions, and compliance standards.
3. Step through the tour or jump directly to:
   - **Upload (`/upload`):** Ingest `synthetic_lab_report_2026.pdf` to demonstrate vector parsing and human review.
   - **Results (`/results`):** Rotate the 3D human body, click on the **Liver** or **Kidneys**, and inspect the cross-analyte de Ritis ratio and renal clusters.
   - **Trends (`/dashboard`):** Demonstrate the multi-year trajectory graphs for Hemoglobin and ALT across 2024–2026.
   - **Alcohol (`/alcohol`):** Rotate the 3D liver model, calculate pure ethanol for 500 mL of beer (19.7g), and inspect the transaminase linkage.
   - **Nutrition (`/nutrition`):** Switch between Vegetarian, Vegan, and Jain diets, verifying the complete exclusion of underground root vegetables for Jain profiles.
   - **Grounded AI Assistant:** Click the floating **"Ask NutriSphere AI"** button at the bottom-right and ask *"Explain my ALT & AST liver enzymes"*. Observe how the assistant cites exact numerical values from the active report without hallucinating clinical diagnoses.
