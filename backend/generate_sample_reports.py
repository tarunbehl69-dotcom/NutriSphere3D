"""
NutriSphere 3D - Synthetic Report Generation Utility
Generates realistic non-patient sample reports:
1. Multi-page PDF with selectable text (CBC, CMP, Lipids, Vitamins)
2. Scanned image report (PNG with Pillow)
3. Tricky international units report (PDF with mmol/L, umol/L, g/L)
4. Multi-year longitudinal reports JSON (2024, 2025, 2026)
"""

import json
from pathlib import Path
import pymupdf as fitz
from PIL import Image, ImageDraw, ImageFont

REPORTS_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_reports"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_comprehensive_pdf():
    """Create a 3-page synthetic clinical laboratory report PDF with selectable text."""
    pdf_path = REPORTS_DIR / "synthetic_lab_report_2026.pdf"
    doc = fitz.open()

    # --- Page 1: CBC & Differential ---
    page1 = doc.new_page(width=595, height=842)  # A4 size
    p1_text = (
        "APEX METROPOLITAN DIAGNOSTICS LABORATORIES\n"
        "SYNTHETIC LABORATORY REPORT — FOR EDUCATIONAL DEMONSTRATION ONLY\n"
        "--------------------------------------------------------------------------------\n"
        "Patient ID: SYNTH-PATIENT-9042        Age/Sex: 38 / Male        Date: 2026-09-15\n"
        "Specimen: Whole Blood (EDTA)           Fasting Status: Fasting 10 hrs\n"
        "Ordering Physician: Dr. E. Vance, MD   Laboratory Director: Dr. R. Chen, FACP\n"
        "================================================================================\n\n"
        "COMPLETE BLOOD COUNT (CBC) WITH AUTOMATED DIFFERENTIAL\n\n"
        "TEST NAME                       RESULT      UNITS      REFERENCE INTERVAL   FLAG\n"
        "--------------------------------------------------------------------------------\n"
        "Hemoglobin (HGB)                14.8        g/dL       13.8 - 17.2\n"
        "White Blood Cell Count (WBC)    6.8         10^3/uL    4.5 - 11.0\n"
        "Platelet Count (PLT)            240         10^3/uL    150 - 450\n"
        "Red Blood Cell Count (RBC)      5.10        10^6/uL    4.30 - 5.90\n"
        "Mean Corpuscular Volume (MCV)   88.5        fL         80.0 - 100.0\n"
        "Mean Corpuscular Hgb (MCH)      29.0        pg         27.0 - 33.0\n"
        "MCHC                            33.2        g/dL       32.0 - 36.0\n"
        "Red Cell Distribution Width     12.8        %          11.5 - 14.5\n"
        "Neutrophils %                   58.0        %          40.0 - 70.0\n"
        "Lymphocytes %                   32.0        %          20.0 - 40.0\n"
        "Monocytes %                     6.5         %          2.0 - 8.0\n"
        "Eosinophils %                   2.8         %          1.0 - 4.0\n"
        "Basophils %                     0.7         %          0.0 - 1.5\n"
        "--------------------------------------------------------------------------------\n"
        "Page 1 of 3 | Specimen verified | Method: Automated Flow Cytometry/Impedance\n"
    )
    page1.insert_text((40, 50), p1_text, fontsize=9.5, fontname="courier")

    # --- Page 2: Metabolic Panel (Liver & Kidney) ---
    page2 = doc.new_page(width=595, height=842)
    p2_text = (
        "APEX METROPOLITAN DIAGNOSTICS LABORATORIES\n"
        "SYNTHETIC LABORATORY REPORT — FOR EDUCATIONAL DEMONSTRATION ONLY\n"
        "--------------------------------------------------------------------------------\n"
        "Patient ID: SYNTH-PATIENT-9042        Age/Sex: 38 / Male        Date: 2026-09-15\n"
        "Specimen: Serum Gel Separator          Fasting Status: Fasting 10 hrs\n"
        "================================================================================\n\n"
        "COMPREHENSIVE METABOLIC PANEL (HEPATIC & RENAL PROFILES)\n\n"
        "TEST NAME                       RESULT      UNITS      REFERENCE INTERVAL   FLAG\n"
        "--------------------------------------------------------------------------------\n"
        "Alanine Aminotransferase (ALT)  58.0        U/L        7.0 - 56.0           HIGH *\n"
        "Aspartate Aminotransferase (AST) 38.0       U/L        10.0 - 40.0\n"
        "Alkaline Phosphatase (ALP)      72.0        U/L        44.0 - 147.0\n"
        "Total Bilirubin                 0.85        mg/dL      0.20 - 1.20\n"
        "Serum Albumin                   4.5         g/dL       3.4 - 5.4\n"
        "Total Protein                   7.2         g/dL       6.0 - 8.3\n"
        "Serum Creatinine                0.95        mg/dL      0.70 - 1.30\n"
        "Blood Urea Nitrogen (BUN)       14.0        mg/dL      7.0 - 20.0\n"
        "eGFR (CKD-EPI Formula)          104         mL/min     > 90\n"
        "Serum Sodium (Na)               141         mEq/L      135 - 145\n"
        "Serum Potassium (K)             4.3         mEq/L      3.5 - 5.1\n"
        "Serum Chloride (Cl)             102         mEq/L      96 - 106\n"
        "Serum Calcium                   9.4         mg/dL      8.6 - 10.2\n"
        "--------------------------------------------------------------------------------\n"
        "* Note: Mild ALT elevation noted. Clinical correlation recommended.\n"
        "Page 2 of 3 | Method: Photometric Spectrophotometry\n"
    )
    page2.insert_text((40, 50), p2_text, fontsize=9.5, fontname="courier")

    # --- Page 3: Lipids, Glycemic, Thyroid & Vitamins ---
    page3 = doc.new_page(width=595, height=842)
    p3_text = (
        "APEX METROPOLITAN DIAGNOSTICS LABORATORIES\n"
        "SYNTHETIC LABORATORY REPORT — FOR EDUCATIONAL DEMONSTRATION ONLY\n"
        "--------------------------------------------------------------------------------\n"
        "Patient ID: SYNTH-PATIENT-9042        Age/Sex: 38 / Male        Date: 2026-09-15\n"
        "================================================================================\n\n"
        "LIPID PROFILE, DIABETES, ENDOCRINE & VITAMIN PANEL\n\n"
        "TEST NAME                       RESULT      UNITS      REFERENCE INTERVAL   FLAG\n"
        "--------------------------------------------------------------------------------\n"
        "Fasting Blood Glucose           92.0        mg/dL      70.0 - 99.0\n"
        "Hemoglobin A1c (HbA1c)          5.4         %          4.0 - 5.6\n"
        "Total Cholesterol               215.0       mg/dL      100.0 - 199.0        HIGH *\n"
        "HDL Cholesterol                 44.0        mg/dL      40.0 - 60.0\n"
        "LDL Cholesterol (Calculated)    138.0       mg/dL      50.0 - 99.0          HIGH *\n"
        "Triglycerides                   165.0       mg/dL      0.0 - 149.0          HIGH *\n"
        "Thyroid Stimulating Hormone(TSH) 2.15       uIU/mL     0.40 - 4.20\n"
        "Free Thyroxine (FT4)            1.22        ng/dL      0.80 - 1.80\n"
        "25-Hydroxy Vitamin D            22.4        ng/mL      30.0 - 100.0         LOW *\n"
        "Vitamin B12                     340.0       pg/mL      200.0 - 900.0\n"
        "Serum Ferritin                  88.0        ng/mL      20.0 - 250.0\n"
        "High-Sensitivity CRP (hs-CRP)   1.2         mg/L       0.0 - 3.0\n"
        "--------------------------------------------------------------------------------\n"
        "End of Report. Authenticated electronically by Apex Metropolitan LIS.\n"
        "DISCLAIMER: Laboratory findings require clinical correlation by a medical doctor.\n"
        "Page 3 of 3\n"
    )
    page3.insert_text((40, 50), p3_text, fontsize=9.5, fontname="courier")

    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


def generate_scanned_image_report():
    """Create a realistic scanned lab slip image using Pillow."""
    img_path = REPORTS_DIR / "synthetic_scanned_report.png"
    width, height = 750, 950
    # Slightly aged paper color for simulated scanned report
    image = Image.new("RGB", (width, height), color=(248, 249, 250))
    draw = ImageDraw.Draw(image)

    # Simulated scan lines and borders
    draw.rectangle([20, 20, width - 20, height - 20], outline=(180, 190, 200), width=2)
    draw.line([30, 120, width - 30, 120], fill=(140, 150, 160), width=2)
    draw.line([30, 210, width - 30, 210], fill=(140, 150, 160), width=1)

    lines = [
        ("CITY CENTRAL PATHOLOGY (SCANNED COPY)", 40, 40),
        ("CONFIDENTIAL MEDICAL REPORT — SYNTHETIC DATA", 40, 65),
        ("Specimen ID: SYNTH-SCAN-7718   Date: 2026-08-20   Patient: Adult Male", 40, 90),
        ("TEST DESCRIPTION            RESULT       UNIT        REF RANGE", 40, 140),
        ("-------------------------------------------------------------------", 40, 165),
        ("HEMOGLOBIN                  13.9         g/dL        13.5 - 17.5", 40, 190),
        ("WBC COUNT                   7.2          10^3/uL     4.5 - 11.0", 40, 225),
        ("PLATELETS                   215          10^3/uL     150 - 400", 40, 260),
        ("FASTING BLOOD SUGAR         104          mg/dL       70 - 100    [ELEVATED]", 40, 295),
        ("BLOOD UREA NITROGEN         16           mg/dL       7 - 20", 40, 330),
        ("SERUM CREATININE            1.05         mg/dL       0.7 - 1.3", 40, 365),
        ("ALT (SGPT)                  42           U/L         10 - 50", 40, 400),
        ("AST (SGOT)                  31           U/L         10 - 40", 40, 435),
        ("TOTAL CHOLESTEROL           210          mg/dL       125 - 200   [BORDERLINE]", 40, 470),
        ("TRIGLYCERIDES               155          mg/dL       < 150", 40, 505),
        ("TSH                         2.80         uIU/mL      0.40 - 4.50", 40, 540),
        ("VITAMIN D3                  18.5         ng/mL       30 - 100    [DEFICIENT]", 40, 575),
        ("-------------------------------------------------------------------", 40, 620),
        ("SCANNED ARCHIVAL STAMP — OCR AUDIT LOG VERIFIED", 40, 660),
        ("Notice: Verified optical character recognition target fixture.", 40, 700),
    ]

    for text, x, y in lines:
        draw.text((x, y), text, fill=(35, 45, 55))

    from PIL import PngImagePlugin
    info = PngImagePlugin.PngInfo()
    info.add_text("ocr_text", "\n".join(t for t, _, _ in lines))
    image.save(str(img_path), pnginfo=info)
    return str(img_path)


def generate_tricky_units_pdf():
    """Create a PDF report with international units (mmol/L, umol/L, g/L)."""
    pdf_path = REPORTS_DIR / "synthetic_tricky_units_report.pdf"
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    text = (
        "INTERNATIONAL BIO-METRIC LABORATORIES (SI UNITS)\n"
        "SYNTHETIC TEST REPORT FOR UNIT NORMALIZATION & VERIFICATION\n"
        "================================================================================\n"
        "Patient: SYNTH-PATIENT-9042        Date: 2026-07-10        Standard: SI Metric\n"
        "--------------------------------------------------------------------------------\n\n"
        "ANALYTE                         CONCENTRATION    SI UNIT     SI REFERENCE\n"
        "--------------------------------------------------------------------------------\n"
        "Fasting Plasma Glucose          5.8              mmol/L      3.9 - 5.6\n"
        "Total Serum Cholesterol         5.5              mmol/L      3.0 - 5.2\n"
        "HDL Cholesterol                 1.1              mmol/L      1.0 - 1.6\n"
        "LDL Cholesterol                 3.6              mmol/L      1.8 - 3.4\n"
        "Serum Creatinine                84.0             umol/L      62.0 - 115.0\n"
        "Hemoglobin Concentration        148              g/L         135 - 175\n"
        "Serum Urea                      5.2              mmol/L      2.5 - 7.1\n"
        "Serum Potassium                 4.2              mmol/L      3.5 - 5.1\n"
        "Serum Sodium                    140              mmol/L      135 - 145\n"
        "Total Bilirubin                 14.5             umol/L      3.4 - 20.5\n"
        "25-OH Vitamin D                 56.0             nmol/L      75.0 - 250.0\n"
        "--------------------------------------------------------------------------------\n"
        "Validation Target: Unit conversion and normalization verification.\n"
    )
    page.insert_text((40, 60), text, fontsize=10, fontname="courier")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)


def generate_historical_longitudinal_json():
    """Create longitudinal historical records (2024, 2025, 2026) for trend analysis."""
    json_path = DATA_DIR / "historical_reports.json"
    data = {
        "patient_identifier": "SYNTH-PATIENT-9042",
        "description": "Multi-year synthetic longitudinal health records for trend analysis.",
        "series": [
            {
                "report_id": "rep_synth_2024",
                "collection_date": "2024-09-12",
                "laboratory": "Apex Metropolitan Diagnostics",
                "markers": {
                    "CBC_HGB": {"value": 14.5, "unit": "g/dL", "flag": "within_reference"},
                    "CBC_WBC": {"value": 6.4, "unit": "10^3/uL", "flag": "within_reference"},
                    "LIV_ALT": {"value": 36.0, "unit": "U/L", "flag": "within_reference"},
                    "LIV_AST": {"value": 28.0, "unit": "U/L", "flag": "within_reference"},
                    "KID_CREAT": {"value": 0.90, "unit": "mg/dL", "flag": "within_reference"},
                    "GLU_FASTING": {"value": 88.0, "unit": "mg/dL", "flag": "within_reference"},
                    "GLU_HBA1C": {"value": 5.2, "unit": "%", "flag": "within_reference"},
                    "LIP_CHOL": {"value": 192.0, "unit": "mg/dL", "flag": "within_reference"},
                    "LIP_LDL": {"value": 118.0, "unit": "mg/dL", "flag": "above_reference"},
                    "VIT_D": {"value": 19.1, "unit": "ng/mL", "flag": "below_reference"}
                }
            },
            {
                "report_id": "rep_synth_2025",
                "collection_date": "2025-09-18",
                "laboratory": "Apex Metropolitan Diagnostics",
                "markers": {
                    "CBC_HGB": {"value": 14.6, "unit": "g/dL", "flag": "within_reference"},
                    "CBC_WBC": {"value": 6.6, "unit": "10^3/uL", "flag": "within_reference"},
                    "LIV_ALT": {"value": 44.0, "unit": "U/L", "flag": "within_reference"},
                    "LIV_AST": {"value": 32.0, "unit": "U/L", "flag": "within_reference"},
                    "KID_CREAT": {"value": 0.92, "unit": "mg/dL", "flag": "within_reference"},
                    "GLU_FASTING": {"value": 90.0, "unit": "mg/dL", "flag": "within_reference"},
                    "GLU_HBA1C": {"value": 5.3, "unit": "%", "flag": "within_reference"},
                    "LIP_CHOL": {"value": 204.0, "unit": "mg/dL", "flag": "above_reference"},
                    "LIP_LDL": {"value": 126.0, "unit": "mg/dL", "flag": "above_reference"},
                    "VIT_D": {"value": 21.0, "unit": "ng/mL", "flag": "below_reference"}
                }
            },
            {
                "report_id": "rep_synth_2026",
                "collection_date": "2026-09-15",
                "laboratory": "Apex Metropolitan Diagnostics",
                "markers": {
                    "CBC_HGB": {"value": 14.8, "unit": "g/dL", "flag": "within_reference"},
                    "CBC_WBC": {"value": 6.8, "unit": "10^3/uL", "flag": "within_reference"},
                    "LIV_ALT": {"value": 58.0, "unit": "U/L", "flag": "above_reference"},
                    "LIV_AST": {"value": 38.0, "unit": "U/L", "flag": "within_reference"},
                    "KID_CREAT": {"value": 0.95, "unit": "mg/dL", "flag": "within_reference"},
                    "GLU_FASTING": {"value": 92.0, "unit": "mg/dL", "flag": "within_reference"},
                    "GLU_HBA1C": {"value": 5.4, "unit": "%", "flag": "within_reference"},
                    "LIP_CHOL": {"value": 215.0, "unit": "mg/dL", "flag": "above_reference"},
                    "LIP_LDL": {"value": 138.0, "unit": "mg/dL", "flag": "above_reference"},
                    "VIT_D": {"value": 22.4, "unit": "ng/mL", "flag": "below_reference"}
                }
            }
        ]
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return str(json_path)


if __name__ == "__main__":
    p1 = generate_comprehensive_pdf()
    p2 = generate_scanned_image_report()
    p3 = generate_tricky_units_pdf()
    p4 = generate_historical_longitudinal_json()
    print("Synthetic reports generated successfully:")
    print(f"1. {p1}")
    print(f"2. {p2}")
    print(f"3. {p3}")
    print(f"4. {p4}")
