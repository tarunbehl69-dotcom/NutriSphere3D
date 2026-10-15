# NutriSphere 3D — Google Antigravity Vibe-Coding Prompts

## Goal
Build a REAL working immersive 3D medical-report explanation website, not a static mockup. Users upload a medical report, review the extraction, inspect a detailed breakdown of reported tests, compare previous reports, explore related anatomy, and receive cautious food-based educational suggestions and alcohol risk information.

## Stack (preserves the assignments’ core approach)
HTML + Tailwind CSS + JavaScript; Three.js as the 3D rendering addition; Python + FastAPI; SQLite for local demonstration; Postman; pytest. FastAPI serves both UI and API. Build one testable step at a time using Google Antigravity, run and inspect before proceeding.

## Clinical safety and honest scope
Support a broad, growing catalog of lab test types; do NOT promise every medical test or image can be analyzed. A laboratory reference interval is not a diagnosis, and normal values cannot rule out disease. Use lab-provided ranges and preserve original units, terminology, method, dates and reference conditions. Present suggestions as education, not medical advice; explain limitations and uncertainty. For urgently concerning findings, advise prompt clinical evaluation with symptom-aware escalation. Do not compute a “safe drinking allowance” from reports; no laboratory analysis can establish it. Real patient data requires stringent consent, security, clinical validation, and jurisdiction-specific legal review. Use synthetic data for class demo.

## Full coverage areas
CBC and differential, liver panel, kidney and electrolytes, blood sugar/diabetes, lipids, thyroid, vitamin and iron studies, metabolic and bone profiles, hormone panels, inflammation, coagulation, urine/urinalysis, cardiac biomarkers, select infectious and autoimmune serology, stool or microbiology report text, and narrative summaries of imaging/ECG reports. Textual reports only: analyzing raw radiology images, ECG waveforms, pathology slides or genomic test data needs separate specialist-grade modules and validation.

## User workflow
Landing → Consent → Secure upload → Text extraction/OCR → Human verification of ambiguous values → Structured biomarkers → Per-marker explanations and anomalies → Trends and 3D organ explainer → Nutrition suggestions and alcohol risk education → Export summary / delete data.

## Copy instructions
Paste one numbered prompt block into Antigravity at a time. After every step, ask Antigravity to run the app and tests, list changed files, and show what was verified. Never accept a claim that functionality works without a demo/test.

## Step 0 — Project setup

```text
Create nutrisphere3d/ with backend/{main.py,database.py,models.py,seed_data.py,services/{parser.py,normalizer.py,interpreter.py,nutrition.py,alcohol.py},tests/}, frontend/{index.html,upload.html,results.html,dashboard.html,css/styles.css,js/{app.js,upload.js,results.js,dashboard.js,anatomy.js}}, data/{test_catalog_seed.csv,demo_report.json}, requirements.txt, README.md. Keep HTML + Tailwind CSS + JavaScript, Python + FastAPI, SQLite, Postman; add Three.js for actual interactive 3D and PyMuPDF + Pillow + OCR adapter for reports. Use Python virtual environment. No patient data checked into git. Confirm scaffold and dependencies.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 1 — Test catalog and SQLite data model

```text
Create tables users (local demo account, never store plaintext password), reports (id,user_id,file_name,mime_type,uploaded_at,analysis_status), biomarkers (id,report_id,analyte_code,label,value_numeric,value_text,unit,reference_low,reference_high,reference_text,flag,collection_date,source_page,extraction_confidence), interpretations (biomarker_id,explanation,reasoning_limits,followup), medications (opt-in structured context), nutrition_preferences, audit_events. Make an extensive seed catalog with aliases and unit mappings across CBC, liver, kidney, lipid, glucose, thyroid, vitamins/minerals, iron, hormones, inflammatory, coagulation, urine, cardiac, metabolic, autoimmune, infectious and other panels. Test catalog is extensible; do not assert every test is supported. Seed only non-patient synthetic data and repeat safely.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 2 — Pydantic schemas and privacy

```text
Define ReportOut, AnalyteOut, InterpretationOut, UploadStatusOut, NutritionContextIn, AlcoholContextIn, ReportSummaryOut, ChartPoint and ErrorOut. Validate size, MIME type, numeric range, units and ownership; do not infer diagnosis from a value alone. Provide explicit consent before uploading and conspicuous deletion controls. Never log report content or biomarker values. Require authentication in any deployment with real patients; local demo may use synthetic samples only.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 3 — Upload and extraction API

```text
Implement POST /api/reports (multipart PDF/JPG/PNG), GET /api/reports, GET /api/reports/{id}, DELETE /api/reports/{id}, GET /api/reports/{id}/status. Enforce PDF/image validation, file-size and page limits, malware-aware handling, safe paths, owner authorization and clear 400/401/403/404/413/415/422 responses. Extract selectable text first; use OCR for scanned pages; record source page and confidence; never invent missing results. Show editable review screen for low-confidence fields prior to interpretation. Demo must work using synthetic report fixtures.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 4 — Units, reference intervals, and flagging

```text
Normalize synonyms and units only with verified conversions. Retain exact original values, source text, units, lab-specific reference intervals and dates. Prefer report-provided interval, with fallback only if explicitly labeled generic and population-appropriate. Flag below/within/above/unknown or urgent-review using clinician-approved, separately configured rules; never treat all abnormal flags as clinical emergencies. Account for context where relevant (age, sex-related reference intervals, pregnancy, medication, fasting status). Validate the parser on at least 25 synthetic formats and tricky unit cases.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 5 — Explain reports without diagnosing

```text
For every extracted biomarker return: plain-English meaning, reported value/units, supplied reference range, potential associations phrased conditionally, factors affecting interpretation, related tests, source citation (report page), questions for a clinician, and a clear uncertainty indicator. For clusters, provide cautious cross-marker summaries with evidence source/version. Avoid definitive diagnoses, probability of disease, prescriptions, dosage changes and reassuring conclusions from incomplete tests. Show high-priority guidance where urgent symptoms or critical values appear without relying only on an AI model. Human review before real-world clinical use.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 6 — Nutrition knowledge and recommendations

```text
Create opt-in preferences (vegetarian, vegan, non-vegetarian, allergies, cultural restrictions, budget, age group, relevant clinician-verified conditions). Offer food-first Indian meal suggestions by nutrients, estimated servings, food sources, appropriate cautions, and optional 7-day menus. Clearly separate general nutritional education from clinical dietary prescriptions. Do not recommend supplements, calorie targets or restricted diets merely because one test was out of range. Screen contraindications such as kidney disease, medications and food allergies; abstain when uncertain.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 7 — Alcohol risk information

```text
Present alcohol education rather than calculated medically safe personal limits. Input frequency, typical standard-drink size, medication/pregnancy/liver history (optional). Explain that no lab panel proves a safe alcohol amount and avoiding alcohol is safest for health. Identify circumstances where alcohol should be avoided or medical advice sought; do not output “you can safely drink X drinks” based on biomarkers. Use medically reviewed educational references and show review date.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 8 — Interactive 3D anatomical interface

```text
Load Three.js from a pinned version; use a real licensed or original glTF human/organ model with attribution, not a fake 3D-looking 2D illustration. Build rotatable, zoomable, keyboard-accessible 3D anatomy with selectable liver, kidneys, heart, thyroid, pancreas, bones. Selecting an organ opens related marker cards with explanatory associations, but avoid suggesting the model represents a diagnosis. Reduced-motion option, low-power/mobile fallback to 2D illustration, and graceful loading/error states.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 9 — Frontend visual system and pages

```text
Create four responsive pages: landing (3D hero and privacy explanation), upload (drag-drop + consent + extraction progress), results (complete sortable/filterable marker table, summary, source citation, organ explorer), dashboard (trends across user-owned reports, nutrition and alcohol education). Visual direction: premium midnight navy, teal and soft ice-blue, subtle glass surfaces, readable typography, depth and parallax sparingly; high accessibility/contrast. No misleading “health score” or instant diagnosis claims. Include demo mode prominently.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 10 — Trend analysis and report comparisons

```text
Create GET /api/biomarkers/trends?analyte_code=... and GET /api/reports/{id}/summary. Only compare compatible measurements, units and methodologies. Display date-axis plots, uncertainty, change from prior result, and narrative explanations without claiming trends demonstrate causation. Missing or unrecognized tests remain visible as unclassified, not silently dropped.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 11 — Postman and integration tests

```text
Create nutrisphere3d-api.postman_collection.json plus pytest coverage: upload valid PDF, scanned image with mocked OCR, unsupported type 415, too large 413, missing file 400, wrong user 403/404, deleted report 404, ambiguous OCR needs manual review, invalid unit 422, nutrition allergies, alcohol non-guarantee, trend conversion, empty/error states. Include 2xx and 4xx screenshots/recordings for submission. Never test with actual personal health records.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Step 12 — Production safety, polish and handoff

```text
Write README with architecture (browser → FastAPI → SQLite), exact run commands, limits, demo-only warning, catalog provenance, safety constraints, how to add a test, retention and deletion policy, access control, encryption and regulatory review requirements for deployment. Use compiled Tailwind CSS for production rather than CDN; SQLite is suitable for local demonstration, evaluate production storage separately. Test mobile browsers, 3D fallback, restart persistence, accessibility and resilience. Provide reproducible synthetic examples.

After completing this step: show changed files, run relevant automated tests, and explain expected output and one negative test. Do not move to the next step automatically.
```

## Minimum acceptance criteria
- Parses a set of diverse synthetic reports including a PDF with selectable text and a scanned-image case.
- Reports all extracted tests including unknown ones and does not hallucinate absent results.
- Clearly flags uncertain OCR output for human correction.
- Stores user-approved values, allows deletion and blocks cross-user access.
- Explains markers with units, source page, lab-specific reference interval and uncertainty.
- Demonstrates a functioning rotate/zoom/select 3D anatomical model plus a 2D accessibility fallback.
- Returns medically cautious nutrition education and no purported personalized safe alcohol quota.
- Includes a documented API contract, Postman collection and negative validation tests.

## Suggested next phase (not required for MVP)
Clinician-reviewed knowledge base, multilingual report explanations, FHIR/LOINC coding, hospital integrations, audited clinical-grade inference, robust encrypted cloud database, structured regulatory assessment.
