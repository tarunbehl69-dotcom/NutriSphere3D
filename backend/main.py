"""
NutriSphere 3D - Main Application Entrypoint
FastAPI application serving both REST API endpoints and interactive frontend UI.
Includes Step 3 Medical Report Upload, PyMuPDF + OCR Extraction Pipeline,
Human Verification, and Server-Validated Session Authentication.
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
import pymupdf

from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    status,
    Depends,
    UploadFile,
    File,
    Form
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.database import get_db, init_db
from backend.models import (
    HealthCheckResponse,
    ErrorOut,
    UserOut,
    TestCatalogItemOut,
    ReportOut,
    AnalyteOut,
    InterpretationOut,
    UploadStatusOut,
    NutritionContextIn,
    AlcoholContextIn,
    ReportSummaryOut,
    ChartPoint,
    ConsentDeclarationIn,
    DeleteReportOut,
    LoginIn,
    TokenOut,
    VerifyBiomarkersIn,
    ReportInterpretRequestIn,
    AlcoholCalculationIn,
    AlcoholCalculationOut,
    AlcoholIntakeRecordIn,
    AlcoholIntakeRecordOut,
    AIReportChatIn,
    AIReportChatOut,
    GameProgressOut,
    GameMissionCompleteIn,
    GameMissionCompleteOut,
    GameQuizSubmitIn,
    GameQuizSubmitOut,
    GameChallengeCompleteIn,
    GameChallengeCompleteOut,
    GameAchievement
)
from backend.services.privacy import (
    delete_report_with_audit,
    log_safe_audit_event,
    verify_report_ownership,
    validate_file_metadata
)
from backend.services.auth import (
    get_current_user,
    get_optional_current_user,
    DEV_DEMO_TOKEN,
    create_session_token,
    authenticate_user_credentials,
    IS_PRODUCTION
)
from backend.services.parser import ReportParserService
from backend.services.normalizer import NormalizerService
from backend.services.interpreter import ClinicalInterpretationService
from backend.services.nutrition import NutritionGuidanceService
from backend.services.alcohol import AlcoholEducationService
from backend.services.ai_assistant import AIAssistantService
from backend.services.game_service import (
    get_or_create_player_progress,
    get_missions_catalog,
    get_achievements_catalog,
    award_mission_completion,
    submit_quiz_answer,
    record_challenge_completion,
    reset_demo_game_progress,
    MISSION_DEFINITIONS,
    ACHIEVEMENT_DEFINITIONS
)
from backend.services.organ_registry import (
    ORGAN_REGISTRY,
    get_all_organs,
    get_organ_by_id,
    find_organ_for_test
)
from backend.seed_data import (
    load_test_catalog,
    load_demo_report,
    load_historical_reports,
    list_sample_reports,
    get_sample_report_path,
    seed_database
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database schema & seed test catalog, demo users, and demo reports
    seed_database()
    yield


app = FastAPI(
    title="NutriSphere 3D - Medical Report Intelligence & Interactive Anatomy",
    description="Interactive 3D medical report explanation engine and health literacy platform.",
    version="0.3.0-step3",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories for CSS, JS, and 3D models
if (FRONTEND_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
if (FRONTEND_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
if (FRONTEND_DIR / "models").exists():
    app.mount("/models", StaticFiles(directory=str(FRONTEND_DIR / "models")), name="models")
if (FRONTEND_DIR / "draco").exists():
    app.mount("/draco", StaticFiles(directory=str(FRONTEND_DIR / "draco")), name="draco")


# --- UI Page Routes ---

@app.get("/", tags=["UI"])
async def serve_index():
    """Serve Landing Page with 3D hero."""
    index_file = FRONTEND_DIR / "index.html"
    return FileResponse(str(index_file))


@app.get("/upload", tags=["UI"])
async def serve_upload():
    """Serve Report Upload & Human Verification Page."""
    upload_file = FRONTEND_DIR / "upload.html"
    return FileResponse(str(upload_file))


@app.get("/results", tags=["UI"])
async def serve_results():
    """Serve Biomarker Breakdown and 3D Organ Explorer Page."""
    results_file = FRONTEND_DIR / "results.html"
    return FileResponse(str(results_file))


@app.get("/anatomy", tags=["UI"])
async def serve_anatomy():
    """Serve Dedicated 3D Anatomical Explorer Page."""
    anatomy_file = FRONTEND_DIR / "anatomy.html"
    return FileResponse(str(anatomy_file))


@app.get("/dashboard", tags=["UI"])
async def serve_dashboard():
    """Serve Longitudinal Trends, Nutrition & Health Education Page."""
    dashboard_file = FRONTEND_DIR / "dashboard.html"
    return FileResponse(str(dashboard_file))


@app.get("/alcohol", tags=["UI"])
async def serve_alcohol():
    """Serve Dedicated Alcohol & Your Health Analysis Module."""
    alcohol_file = FRONTEND_DIR / "alcohol.html"
    return FileResponse(str(alcohol_file))


@app.get("/nutrition", tags=["UI"])
async def serve_nutrition():
    """Serve Dedicated Food-First Indian Nutrition Guidance Page."""
    nutrition_file = FRONTEND_DIR / "nutrition.html"
    return FileResponse(str(nutrition_file))


@app.get("/quest", tags=["UI"])
async def serve_quest():
    """Serve NutriSphere Quest — Journey Inside the Human Body 3D Game."""
    quest_file = FRONTEND_DIR / "quest.html"
    return FileResponse(str(quest_file))


@app.get("/games", tags=["UI"])
async def serve_games():
    """Serve NutriSphere Quest — Learn Your Body (Optional 3D Educational Game)."""
    games_file = FRONTEND_DIR / "games.html"
    return FileResponse(str(games_file))


# --- System & Health Endpoints ---

@app.get("/api/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """Health check endpoint confirming API and SQLite readiness."""
    return HealthCheckResponse(
        status="healthy",
        version="0.3.0-step3",
        database="connected",
        clinical_notice="NutriSphere 3D provides educational explanations only, not diagnostic decisions."
    )


# --- Authentication Endpoints ---

@app.post("/api/auth/login", response_model=TokenOut, tags=["Auth"])
async def login(credentials: LoginIn):
    """Authenticate with username & password; returns server-validated session token."""
    user = authenticate_user_credentials(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = create_session_token(user["id"])
    return TokenOut(
        access_token=token,
        token_type="bearer",
        user_id=user["id"],
        username=user["username"]
    )


@app.post("/api/auth/demo-token", response_model=TokenOut, tags=["Auth"])
async def get_dev_demo_token():
    """Retrieve isolated development-only demo token (strictly forbidden in production)."""
    if IS_PRODUCTION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development demo credentials are disabled in production environment."
        )
    return TokenOut(
        access_token=DEV_DEMO_TOKEN,
        token_type="bearer",
        user_id="usr_demo_001",
        username="demouser"
    )


# --- Clinical Catalog Endpoints ---

@app.get("/api/catalog", tags=["Catalog"])
async def query_test_catalog(panel: str = None, search: str = None):
    """Query the clinical test catalog with optional panel or search filter."""
    with get_db() as conn:
        query = "SELECT * FROM test_catalog WHERE 1=1"
        params = []
        if panel:
            query += " AND LOWER(panel) = LOWER(?)"
            params.append(panel)
        if search:
            query += " AND (LOWER(canonical_name) LIKE ? OR LOWER(aliases) LIKE ? OR LOWER(analyte_code) LIKE ?)"
            s_param = f"%{search.lower()}%"
            params.extend([s_param, s_param, s_param])
        query += " ORDER BY panel, canonical_name ASC;"
        rows = conn.execute(query, params).fetchall()
        items = [dict(row) for row in rows]
        return {"total": len(items), "items": items}


@app.get("/api/catalog/seed", tags=["Catalog"])
async def get_seed_catalog():
    """Return preliminary test catalog items from seed CSV."""
    catalog = load_test_catalog()
    return {"total": len(catalog), "items": catalog}


@app.get("/api/catalog/{analyte_code}", response_model=TestCatalogItemOut, tags=["Catalog"])
async def get_catalog_analyte(analyte_code: str):
    """Retrieve full clinical metadata and reference intervals for a specific analyte."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM test_catalog WHERE LOWER(analyte_code) = LOWER(?);",
            (analyte_code,)
        ).fetchone()
        if not row:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorOut(
                    code="ANALYTE_NOT_FOUND",
                    message=f"Analyte '{analyte_code}' not found in the test catalog."
                ).model_dump(mode="json")
            )
        return dict(row)


# --- Verified Anatomical Registry Endpoints ---

@app.get("/api/organs", tags=["Anatomy"])
async def list_verified_organs():
    """Return all verified anatomical organ definitions and their 3D models."""
    return {"total": len(ORGAN_REGISTRY), "organs": get_all_organs()}


@app.get("/api/organs/{organ_id}", tags=["Anatomy"])
async def get_verified_organ(organ_id: str):
    """Retrieve full anatomical, medical, and test metadata for an organ."""
    organ = get_organ_by_id(organ_id)
    if not organ:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorOut(
                code="ORGAN_NOT_FOUND",
                message=f"Organ '{organ_id}' not found in the verified anatomical registry."
            ).model_dump(mode="json")
        )
    return organ


@app.get("/api/user/demo", response_model=UserOut, tags=["Users"])
async def get_demo_user():
    """Retrieve local demonstration user account (zero password leakage)."""
    with get_db() as conn:
        row = conn.execute("SELECT id, username, email, full_name, role, is_active, created_at FROM users WHERE id = 'usr_demo_001';").fetchone()
        if not row:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorOut(code="USER_NOT_FOUND", message="Demo user account not found.").model_dump(mode="json")
            )
        return dict(row)


@app.get("/api/medications", tags=["Medications"])
async def get_demo_medications():
    """Retrieve opt-in structured medications context for the demo user."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM medications WHERE user_id = 'usr_demo_001';").fetchall()
        return {"medications": [dict(r) for r in rows]}


@app.get("/api/audit-logs", tags=["Audit"])
async def get_audit_events():
    """Retrieve audit log trail for compliance and data transparency."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM audit_events ORDER BY timestamp DESC LIMIT 50;").fetchall()
        return {"events": [dict(r) for r in rows]}


@app.get("/api/demo-report", tags=["Demo"])
async def get_demo_report():
    """Return synthetic medical report fixture for demonstration."""
    demo = load_demo_report()
    if isinstance(demo, dict) and "id" not in demo and "report_metadata" in demo:
        demo["id"] = demo["report_metadata"].get("report_id", "rep_demo_2026_001")
    return demo


@app.get("/api/reports/historical", tags=["Reports"])
async def get_historical_reports():
    """Return longitudinal multi-year health records for trend comparisons."""
    records = load_historical_reports()
    return records


@app.get("/api/sample-reports", tags=["Reports"])
async def get_sample_reports_list():
    """Return list of available synthetic demonstration files (PDF/PNG)."""
    samples = list_sample_reports()
    return {"total": len(samples), "samples": samples}


@app.get("/api/sample-reports/{filename}", tags=["Reports"])
async def download_sample_report(filename: str):
    """Serve or download a specific synthetic report file safely."""
    file_path = get_sample_report_path(filename)
    if not file_path:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorOut(
                code="SAMPLE_NOT_FOUND",
                message=f"Sample report '{filename}' was not found."
            ).model_dump(mode="json")
        )
    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "image/png"
    return FileResponse(str(file_path), media_type=media_type, filename=filename)


# --- Step 2 & 3 Privacy & Consent Endpoints ---

@app.post("/api/consent", tags=["Privacy"])
async def record_user_consent(
    consent: ConsentDeclarationIn,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Record explicit affirmative patient consent and clinical disclaimer acknowledgment."""
    evt_id = log_safe_audit_event(
        event_type="CONSENT_AFFIRMED",
        user_id=current_user["id"],
        details=f"Explicit consent version {consent.consent_version} granted. Non-diagnostic scope acknowledged."
    )
    return {
        "status": "consent_recorded",
        "user_id": current_user["id"],
        "version": consent.consent_version,
        "audit_event_id": evt_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# --- Step 3 Report Upload & Ingestion Pipeline ---

@app.post("/api/reports", response_model=ReportOut, status_code=status.HTTP_201_CREATED, tags=["Reports"])
async def upload_medical_report(
    file: UploadFile = File(...),
    consent: str = Form(..., description="JSON string of ConsentDeclarationIn"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Secure multi-page PDF, JPG, and PNG upload and extraction workflow.
    Validates explicit affirmative consent and file constraints (max 15MB, MIME, magic bytes).
    Extracts text/OCR, normalizes biomarkers using 74-analyte catalog, tracks page citations,
    and flags uncertain or unsupported results for human review.
    Never invents missing medical values, diagnoses or laboratory reference ranges.
    """
    # 1. Parse and validate explicit affirmative consent
    try:
        consent_dict = json.loads(consent) if isinstance(consent, str) else consent
        consent_decl = ConsentDeclarationIn(**consent_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Consent validation failed: {str(e)}"
        )

    if not consent_decl.has_consented or not consent_decl.disclaimer_acknowledged:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Explicit affirmative consent and clinical disclaimer acknowledgment are required before processing."
        )

    # 2. Read file content and validate size & mime
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty (0 bytes)."
        )

    clean_filename = validate_file_metadata(file_size, file.content_type or "", file.filename or "report.pdf")

    # 3. Magic bytes validation
    is_pdf = content.startswith(b"%PDF-")
    is_png = content.startswith(b"\x89PNG\r\n\x1a\n")
    is_jpeg = content.startswith(b"\xff\xd8\xff")

    if not (is_pdf or is_png or is_jpeg):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File content does not match allowed media types (corrupted header or unpermitted format)."
        )

    # 4. Multi-page limit check for PDF (max 20 pages)
    if is_pdf:
        try:
            pdf_doc = pymupdf.open(stream=content, filetype="pdf")
            page_count = len(pdf_doc)
            if page_count > 20:
                pdf_doc.close()
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"PDF exceeds maximum page limit of 20 pages (got {page_count} pages)."
                )
            pdf_doc.close()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unable to parse PDF structure: {str(e)}"
            )

    # 5. Secure file persistence on disk
    report_id = f"rep_{uuid.uuid4().hex[:12]}"
    user_upload_dir = BASE_DIR / "uploads" / current_user["id"]
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    saved_file_path = user_upload_dir / f"{report_id}_{clean_filename}"
    saved_file_path.write_bytes(content)

    # 6. Parse document using PyMuPDF / OCR adapter
    parser = ReportParserService()
    doc_info = parser.parse_document(str(saved_file_path), file.content_type or "")

    metadata = doc_info["metadata"]
    extracted_raw = doc_info["biomarkers"]
    collection_date = metadata.get("collection_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    laboratory_name = metadata.get("laboratory_name") or "Clinical Diagnostic Laboratory"

    # 7. Normalize biomarkers using 74-analyte test catalog
    normalizer = NormalizerService()
    processed_biomarkers = []
    has_low_confidence = doc_info["requires_verification"]

    with get_db() as conn:
        for idx, raw_bm in enumerate(extracted_raw):
            norm = normalizer.normalize_biomarker(raw_bm)
            bm_id = f"bm_{report_id}_{idx+1:03d}"

            # Check if flagged for verification
            if norm["needs_human_verification"] or norm["analyte_code"] == "UNKNOWN_ANALYTE" or norm["flag"] in {"unclassified", "incompatible_units", "unknown"}:
                has_low_confidence = True

            # Generate evidence-linked educational interpretation via ClinicalInterpretationService
            interpreter_svc = ClinicalInterpretationService()
            bm_interp_payload = {
                "id": bm_id,
                "analyte_code": norm["analyte_code"],
                "label": norm["label"],
                "value_numeric": norm["normalized_value"],
                "value_text": norm["raw_value_text"],
                "unit": norm["standard_unit"] or norm["raw_unit"],
                "reference_low": norm["reference_low"],
                "reference_high": norm["reference_high"],
                "reference_text": norm["reference_text"],
                "flag": norm["flag"],
                "source_page": norm["source_page"],
                "extraction_confidence": norm["extraction_confidence"]
            }
            interp = interpreter_svc.interpret_biomarker(bm_interp_payload)

            analyte_out = AnalyteOut(
                id=bm_id,
                report_id=report_id,
                analyte_code=norm["analyte_code"],
                label=norm["label"],
                value_numeric=norm["normalized_value"],
                value_text=norm["raw_value_text"],
                unit=norm["standard_unit"] or norm["raw_unit"],
                reference_low=norm["reference_low"],
                reference_high=norm["reference_high"],
                reference_text=norm["reference_text"],
                flag=norm["flag"],
                organ_system=norm["organ_system"],
                source_page=norm["source_page"],
                extraction_confidence=norm["extraction_confidence"],
                interpretation=interp
            )
            processed_biomarkers.append((analyte_out, interp))

        # 8. Determine report status: needs_human_verification vs extracted
        analysis_status = "needs_human_verification" if has_low_confidence or len(processed_biomarkers) == 0 else "extracted"
        notes = f"Extracted {len(processed_biomarkers)} biomarkers across {len(doc_info['pages'])} pages."

        # 9. Insert report into SQLite
        conn.execute("""
            INSERT INTO reports (
                id, user_id, file_name, mime_type, file_size_bytes, file_path,
                collection_date, laboratory_name, analysis_status, extraction_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            report_id,
            current_user["id"],
            clean_filename,
            file.content_type or "application/octet-stream",
            file_size,
            str(saved_file_path),
            collection_date,
            laboratory_name,
            analysis_status,
            notes
        ))

        # 10. Insert biomarkers and interpretations
        for bm_out, interp_out in processed_biomarkers:
            conn.execute("""
                INSERT INTO biomarkers (
                    id, report_id, analyte_code, label, value_numeric, value_text,
                    unit, reference_low, reference_high, reference_text, flag,
                    collection_date, source_page, extraction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                bm_out.id,
                report_id,
                bm_out.analyte_code,
                bm_out.label,
                bm_out.value_numeric,
                bm_out.value_text,
                bm_out.unit,
                bm_out.reference_low,
                bm_out.reference_high,
                bm_out.reference_text,
                bm_out.flag,
                collection_date,
                bm_out.source_page,
                bm_out.extraction_confidence
            ))

            interp_id = f"int_{bm_out.id}"
            conn.execute("""
                INSERT INTO interpretations (
                    id, biomarker_id, explanation, reasoning_limits, followup, clinical_questions, medical_reference
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                interp_id,
                bm_out.id,
                interp_out.explanation,
                interp_out.reasoning_limits,
                interp_out.followup,
                "; ".join(interp_out.clinical_questions),
                interp_out.medical_reference
            ))

        # 11. Log audit event (zero PHI)
        log_safe_audit_event(
            event_type="REPORT_UPLOADED_AND_EXTRACTED",
            user_id=current_user["id"],
            resource_id=report_id,
            details=f"File '{clean_filename}' uploaded ({file_size} bytes). Extracted {len(processed_biomarkers)} biomarkers. Status: {analysis_status}.",
            conn=conn
        )

    # Return full structured report
    return await get_report_by_id(report_id, current_user=current_user)


@app.get("/api/reports", tags=["Reports"])
async def list_user_reports(current_user: Dict[str, Any] = Depends(get_current_user)):
    """List all medical reports owned by the authenticated user."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, user_id, file_name, mime_type, file_size_bytes, uploaded_at, collection_date, laboratory_name, analysis_status, extraction_notes FROM reports WHERE user_id = ? ORDER BY uploaded_at DESC;",
            (current_user["id"],)
        ).fetchall()
        reports = [dict(r) for r in rows]
        return {"total": len(reports), "reports": reports}


@app.get("/api/reports/{report_id}", response_model=ReportOut, tags=["Reports"])
async def get_report_by_id(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve full structured report output with server-validated owner authorization."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?;", (report_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' was not found.")
        verify_report_ownership(row["user_id"], current_user["id"])

        bm_rows = conn.execute("SELECT * FROM biomarkers WHERE report_id = ?;", (report_id,)).fetchall()
        interpreter_svc = ClinicalInterpretationService()
        med_rows = conn.execute("SELECT drug_name, dosage, frequency FROM medications WHERE user_id = ?;", (current_user["id"],)).fetchall()
        user_meds = [dict(m) for m in med_rows] if med_rows else []
        patient_context = {"medications": user_meds} if user_meds else None

        biomarkers = []
        for bm in bm_rows:
            bm_dict = dict(bm)
            interp = interpreter_svc.interpret_biomarker(bm_dict, patient_context=patient_context)
            org_sys = interpreter_svc.catalog.get(bm["analyte_code"], {}).get("organ_system", "General")
            biomarkers.append(AnalyteOut(
                id=bm["id"],
                report_id=bm["report_id"],
                analyte_code=bm["analyte_code"],
                label=bm["label"],
                value_numeric=bm["value_numeric"],
                value_text=bm["value_text"],
                unit=bm["unit"],
                reference_low=bm["reference_low"],
                reference_high=bm["reference_high"],
                reference_text=bm["reference_text"],
                flag=bm["flag"],
                organ_system=org_sys,
                collection_date=bm["collection_date"],
                source_page=bm["source_page"],
                extraction_confidence=bm["extraction_confidence"],
                interpretation=interp
            ))

        return ReportOut(
            id=row["id"],
            user_id=row["user_id"],
            file_name=row["file_name"],
            mime_type=row["mime_type"],
            file_size_bytes=row["file_size_bytes"] or 0,
            uploaded_at=str(row["uploaded_at"]),
            collection_date=row["collection_date"],
            laboratory_name=row["laboratory_name"],
            analysis_status=row["analysis_status"],
            biomarkers_count=len(biomarkers),
            biomarkers=biomarkers,
            extraction_notes=row["extraction_notes"],
            consent_verified=True
        )


@app.get("/api/reports/{report_id}/status", response_model=UploadStatusOut, tags=["Reports"])
async def get_report_status(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Check extraction status and determine if human verification is required."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?;", (report_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' was not found.")
        verify_report_ownership(row["user_id"], current_user["id"])

        bm_rows = conn.execute("SELECT label, extraction_confidence, flag, source_page FROM biomarkers WHERE report_id = ?;", (report_id,)).fetchall()
        low_conf = [
            b["label"] for b in bm_rows
            if b["extraction_confidence"] < 0.85 or b["flag"] in {"unclassified", "incompatible_units", "unknown"}
        ]
        pages_count = max([b["source_page"] for b in bm_rows] + [1])

        st = row["analysis_status"]
        progress = 100 if st in {"verified", "extracted"} else (75 if st == "needs_human_verification" else 25)
        msg = (
            "Biomarkers verified and ready for 3D exploration." if st == "verified"
            else ("Extraction complete with high confidence." if st == "extracted"
            else "Human verification required for ambiguous or unclassified tests.")
        )

        return UploadStatusOut(
            report_id=report_id,
            status=st,
            progress_percent=progress,
            message=msg,
            source_pages_count=pages_count,
            low_confidence_fields=low_conf,
            requires_verification=(st == "needs_human_verification"),
            created_at=str(row["uploaded_at"])
        )


@app.put("/api/reports/{report_id}/verify", response_model=ReportOut, tags=["Reports"])
async def verify_report_biomarkers(
    report_id: str,
    payload: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Manual review & verification endpoint:
    Allows user or clinician to confirm/edit extracted biomarkers, units, and ranges.
    Transitions report status to 'verified'.
    """
    with get_db() as conn:
        rep = conn.execute("SELECT * FROM reports WHERE id = ?;", (report_id,)).fetchone()
        if not rep:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' was not found.")
        verify_report_ownership(rep["user_id"], current_user["id"])

        # Update metadata if provided
        if "collection_date" in payload and payload["collection_date"]:
            conn.execute("UPDATE reports SET collection_date = ? WHERE id = ?;", (payload["collection_date"], report_id))
        if "laboratory_name" in payload and payload["laboratory_name"]:
            conn.execute("UPDATE reports SET laboratory_name = ? WHERE id = ?;", (payload["laboratory_name"], report_id))

        raw_bms = payload.get("biomarkers", [])
        if raw_bms:
            # Delete existing biomarkers to replace with verified set
            conn.execute("DELETE FROM biomarkers WHERE report_id = ?;", (report_id,))

            for idx, bm in enumerate(raw_bms):
                bm_id = bm.get("id") or f"bm_{report_id}_{idx+1:03d}"
                val_num = bm.get("value_numeric")
                if val_num is not None:
                    try:
                        val_num = float(val_num)
                    except (ValueError, TypeError):
                        val_num = None

                ref_low = bm.get("reference_low")
                if ref_low is not None:
                    try:
                        ref_low = float(ref_low)
                    except (ValueError, TypeError):
                        ref_low = None

                ref_high = bm.get("reference_high")
                if ref_high is not None:
                    try:
                        ref_high = float(ref_high)
                    except (ValueError, TypeError):
                        ref_high = None

                flag = bm.get("flag", "unknown")
                # Re-evaluate flag if within reference
                if val_num is not None and ref_low is not None and ref_high is not None:
                    if val_num < ref_low:
                        flag = "below_reference"
                    elif val_num > ref_high:
                        flag = "above_reference"
                    else:
                        flag = "within_reference"

                conn.execute("""
                    INSERT INTO biomarkers (
                        id, report_id, analyte_code, label, value_numeric, value_text,
                        unit, reference_low, reference_high, reference_text, flag,
                        collection_date, source_page, extraction_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    bm_id,
                    report_id,
                    bm.get("analyte_code", "UNKNOWN_ANALYTE"),
                    bm.get("label", "Biomarker"),
                    val_num,
                    bm.get("value_text"),
                    bm.get("unit"),
                    ref_low,
                    ref_high,
                    bm.get("reference_text") or (f"{ref_low} - {ref_high} {bm.get('unit', '')}" if ref_low and ref_high else None),
                    flag,
                    payload.get("collection_date") or rep["collection_date"],
                    bm.get("source_page", 1),
                    1.0  # Verified by human -> confidence becomes 1.0
                ))

                # Insert default interpretation if not exists
                interp_id = f"int_{bm_id}"
                conn.execute("""
                    INSERT OR REPLACE INTO interpretations (
                        id, biomarker_id, explanation, reasoning_limits, followup, clinical_questions, medical_reference
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    interp_id,
                    bm_id,
                    f"Reported value {val_num} {bm.get('unit') or ''} verified by user review.",
                    "Normal and out-of-range lab results require comprehensive physical and clinical evaluation.",
                    "Review with primary care physician.",
                    "How should I track this value over time?; Are repeat measurements indicated?",
                    "AACC / Mayo Clinic Laboratories"
                ))

        # Transition status to verified
        conn.execute("UPDATE reports SET analysis_status = 'verified' WHERE id = ?;", (report_id,))

        # Log audit event
        log_safe_audit_event(
            event_type="REPORT_HUMAN_VERIFIED",
            user_id=current_user["id"],
            resource_id=report_id,
            details=f"Human verified {len(raw_bms)} biomarkers for report '{rep['file_name']}'. Status transitioned to 'verified'.",
            conn=conn
        )

    # Return full report
    return await get_report_by_id(report_id, current_user=current_user)


@app.delete("/api/reports/{report_id}", response_model=DeleteReportOut, tags=["Reports"])
async def delete_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Conspicuous deletion control: permanently purge report, disk files, and child biomarkers."""
    res = delete_report_with_audit(report_id=report_id, current_user_id=current_user["id"])
    return DeleteReportOut(**res)


@app.get("/api/reports/{report_id}/summary", response_model=ReportSummaryOut, tags=["Reports"])
async def get_report_summary(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate comprehensive report summary with multi-marker clusters, symptom-aware cautions, and uncertainty indicators."""
    with get_db() as conn:
        rep = conn.execute("SELECT * FROM reports WHERE id = ?;", (report_id,)).fetchone()
        if not rep:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' was not found.")
        verify_report_ownership(rep["user_id"], current_user["id"])

        # Fetch opt-in medications if registered for this user
        med_rows = conn.execute("SELECT drug_name, dosage, frequency FROM medications WHERE user_id = ?;", (current_user["id"],)).fetchall()
        user_meds = [dict(m) for m in med_rows] if med_rows else []
        patient_context = {"medications": user_meds} if user_meds else None

        bm_rows = conn.execute("SELECT * FROM biomarkers WHERE report_id = ?;", (report_id,)).fetchall()
        biomarkers = [dict(b) for b in bm_rows]

        interpreter_svc = ClinicalInterpretationService()
        report_data = {
            "id": rep["id"],
            "user_id": rep["user_id"],
            "collection_date": rep["collection_date"],
            "biomarkers": biomarkers
        }
        summary_dict = interpreter_svc.interpret_report(report_data, patient_context=patient_context)
        return ReportSummaryOut(**summary_dict)


@app.post("/api/reports/{report_id}/interpret", response_model=ReportSummaryOut, tags=["Reports"])
async def interpret_report_with_context(
    report_id: str,
    context: Optional[ReportInterpretRequestIn] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Evidence-linked comprehensive report interpretation engine with voluntary patient context.
    Evaluates multi-marker clusters (Hepatic, Renal, Cardiometabolic, Hematology, Thyroid),
    analyte-specific critical/panic rules, drug-test interactions, and organ literacy notice.
    Zero PHI is stored or leaked.
    """
    with get_db() as conn:
        rep = conn.execute("SELECT * FROM reports WHERE id = ?;", (report_id,)).fetchone()
        if not rep:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' was not found.")
        verify_report_ownership(rep["user_id"], current_user["id"])

        bm_rows = conn.execute("SELECT * FROM biomarkers WHERE report_id = ?;", (report_id,)).fetchall()
        biomarkers = [dict(b) for b in bm_rows]

        p_ctx = None
        if context:
            p_ctx = {
                "medications": [m.model_dump() for m in context.medications] if context.medications else [],
                "age": context.age,
                "pregnancy_status": context.pregnancy_status,
                "medical_conditions": context.medical_conditions or []
            }
        else:
            med_rows = conn.execute("SELECT drug_name, dosage, frequency FROM medications WHERE user_id = ?;", (current_user["id"],)).fetchall()
            if med_rows:
                p_ctx = {"medications": [dict(m) for m in med_rows]}

        interpreter_svc = ClinicalInterpretationService()
        report_data = {
            "id": rep["id"],
            "user_id": rep["user_id"],
            "collection_date": rep["collection_date"],
            "biomarkers": biomarkers
        }
        summary_dict = interpreter_svc.interpret_report(report_data, patient_context=p_ctx)

        # Log safe audit event (zero PHI)
        log_safe_audit_event(
            event_type="REPORT_INTERPRETATION_GENERATED",
            user_id=current_user["id"],
            resource_id=report_id,
            details=f"Generated clinical interpretation across {len(biomarkers)} markers and {len(summary_dict.get('multimarker_clusters', []))} multi-marker clusters.",
            conn=conn
        )

        return ReportSummaryOut(**summary_dict)


@app.post("/api/nutrition/context", tags=["Nutrition"])
async def generate_nutrition_context(context: NutritionContextIn):
    """Deliver food-first Indian dietary educational guidance filtered by allergy contraindications and optional report biomarkers."""
    svc = NutritionGuidanceService()
    report_bms = None
    if context.report_id:
        with get_db() as conn:
            bm_rows = conn.execute("SELECT * FROM biomarkers WHERE report_id = ?;", (context.report_id,)).fetchall()
            if bm_rows:
                report_bms = [dict(b) for b in bm_rows]

    return svc.get_suggestions(
        dietary_preference=context.dietary_pattern,
        allergies=context.allergies,
        report_biomarkers=report_bms
    )


@app.post("/api/alcohol/context", tags=["Alcohol"])
async def generate_alcohol_context(context: AlcoholContextIn):
    """Deliver evidence-based alcohol health education. Strictly disclaims 'safe drinking quota'."""
    svc = AlcoholEducationService()
    return svc.get_risk_education(
        has_liver_flags=context.has_liver_conditions,
        takes_medications=context.takes_medications,
        pregnancy_status=context.pregnancy_status
    )


@app.post("/api/alcohol/calculate", response_model=AlcoholCalculationOut, tags=["Alcohol"])
async def calculate_alcohol_consumption(calc_in: AlcoholCalculationIn):
    """
    Calculate pure ethanol mass (grams) using exact formula:
    volume_ml * (abv_percent / 100) * 0.789, standard drinks (WHO 10g and US 14g),
    and weekly exposure tier. Strictly disclaims individual safe drinking allowance.
    """
    svc = AlcoholEducationService()
    res = svc.calculate_intake(
        beverage_type=calc_in.beverage_type,
        volume_ml=calc_in.volume_ml,
        abv_percent=calc_in.abv_percent,
        drinking_days_per_week=calc_in.drinking_days_per_week
    )
    return AlcoholCalculationOut(**res)


@app.post("/api/alcohol/records", response_model=AlcoholIntakeRecordOut, status_code=status.HTTP_201_CREATED, tags=["Alcohol"])
async def create_alcohol_record(
    record_in: AlcoholIntakeRecordIn,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Save user-reported alcohol intake record with calculated pure grams and standard drinks."""
    svc = AlcoholEducationService()
    calc = svc.calculate_intake(
        beverage_type=record_in.beverage_type,
        volume_ml=record_in.volume_ml,
        abv_percent=record_in.abv_percent,
        drinking_days_per_week=record_in.drinking_days_per_week
    )
    rec_id = f"alc_{uuid.uuid4().hex[:12]}"
    rec_date = record_in.recorded_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with get_db() as conn:
        conn.execute("""
            INSERT INTO alcohol_intake_records (
                id, user_id, beverage_type, volume_ml, abv_percent, pure_alcohol_grams,
                standard_drinks, drinking_days_per_week, weekly_grams, recorded_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            rec_id,
            current_user["id"],
            record_in.beverage_type,
            record_in.volume_ml,
            record_in.abv_percent,
            calc["pure_alcohol_grams"],
            calc["standard_drinks_who"],
            record_in.drinking_days_per_week,
            calc["weekly_grams"],
            rec_date
        ))

        log_safe_audit_event(
            event_type="ALCOHOL_RECORD_LOGGED",
            user_id=current_user["id"],
            resource_id=rec_id,
            details=f"Logged intake record ({record_in.beverage_type}, {record_in.volume_ml} mL at {record_in.abv_percent}% ABV).",
            conn=conn
        )

    return AlcoholIntakeRecordOut(
        id=rec_id,
        user_id=current_user["id"],
        beverage_type=record_in.beverage_type,
        volume_ml=record_in.volume_ml,
        abv_percent=record_in.abv_percent,
        pure_alcohol_grams=calc["pure_alcohol_grams"],
        standard_drinks=calc["standard_drinks_who"],
        drinking_days_per_week=record_in.drinking_days_per_week,
        weekly_grams=calc["weekly_grams"],
        recorded_date=rec_date,
        created_at=datetime.now(timezone.utc).isoformat()
    )


@app.get("/api/alcohol/records", tags=["Alcohol"])
async def list_alcohol_records(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieve logged alcohol consumption history for authenticated user."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM alcohol_intake_records WHERE user_id = ? ORDER BY recorded_date DESC, created_at DESC;",
            (current_user["id"],)
        ).fetchall()
        items = [dict(r) for r in rows]
        total_weekly_grams = round(sum(r["weekly_grams"] for r in items), 2) if items else 0.0
        return {
            "total_records": len(items),
            "weekly_total_grams": total_weekly_grams,
            "records": items
        }


@app.delete("/api/alcohol/records/{record_id}", tags=["Alcohol"])
async def delete_alcohol_record(
    record_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a specific alcohol intake record with owner validation."""
    with get_db() as conn:
        rec = conn.execute("SELECT * FROM alcohol_intake_records WHERE id = ?;", (record_id,)).fetchone()
        if not rec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alcohol record '{record_id}' not found.")
        verify_report_ownership(rec["user_id"], current_user["id"])
        conn.execute("DELETE FROM alcohol_intake_records WHERE id = ?;", (record_id,))
        log_safe_audit_event(
            event_type="ALCOHOL_RECORD_DELETED",
            user_id=current_user["id"],
            resource_id=record_id,
            details=f"Deleted alcohol record {record_id}.",
            conn=conn
        )
        return {"status": "deleted", "id": record_id}


@app.get("/api/alcohol/report-context/{report_id}", tags=["Alcohol"])
async def get_alcohol_report_context(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Connect verified laboratory findings to hepatic and systemic alcohol health analysis.
    Evaluates ALT, AST (and de Ritis ratio), GGT, Bilirubin, Albumin, ALP, Triglycerides, and MCV.
    """
    with get_db() as conn:
        rep = conn.execute("SELECT * FROM reports WHERE id = ?;", (report_id,)).fetchone()
        if not rep:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' was not found.")
        verify_report_ownership(rep["user_id"], current_user["id"])

        bm_rows = conn.execute("SELECT * FROM biomarkers WHERE report_id = ?;", (report_id,)).fetchall()
        biomarkers = [dict(b) for b in bm_rows]

        med_rows = conn.execute("SELECT drug_name, dosage, frequency FROM medications WHERE user_id = ?;", (current_user["id"],)).fetchall()
        user_meds = [dict(m) for m in med_rows] if med_rows else []
        patient_context = {"medications": user_meds} if user_meds else {}

        svc = AlcoholEducationService()
        analysis = svc.get_report_alcohol_analysis(biomarkers, patient_context)
        return analysis


@app.get("/api/alcohol/recovery-nutrition", tags=["Alcohol"])
async def get_alcohol_recovery_nutrition():
    """Retrieve food-first Indian nutrition and recovery guidance, dispelling detox myths."""
    svc = AlcoholEducationService()
    return svc.get_recovery_nutrition_guidance()


@app.post("/api/chat/explain", response_model=AIReportChatOut, tags=["AI Assistant"])
async def explain_report_with_ai(
    query_in: AIReportChatIn,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Report-grounded conversational medical report explanation assistant.
    Strictly cites verified lab values and reference intervals without fabricating diagnoses.
    """
    with get_db() as conn:
        rep = conn.execute("SELECT * FROM reports WHERE id = ?;", (query_in.report_id,)).fetchone()
        if not rep:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{query_in.report_id}' was not found.")
        verify_report_ownership(rep["user_id"], current_user["id"])

    ai_svc = AIAssistantService()
    return ai_svc.answer_report_question(
        report_id=query_in.report_id,
        question=query_in.question,
        user_id=current_user["id"],
        conversation_history=query_in.conversation_history
    )


# ==========================================
# NUTRISPHERE QUEST — GAME API ENDPOINTS
# ==========================================

@app.get("/api/game/progress", response_model=GameProgressOut, tags=["Game Quest"])
async def get_game_player_progress(current_user: Dict[str, Any] = Depends(get_optional_current_user)):
    """Retrieve player XP, Level, unlocked badges, and completed missions."""
    return get_or_create_player_progress(current_user["id"])


@app.get("/api/game/missions", tags=["Game Quest"])
async def list_game_missions(current_user: Dict[str, Any] = Depends(get_optional_current_user)):
    """List all 7 playable educational health missions with player completion status and quiz questions."""
    return get_missions_catalog(current_user["id"])


@app.get("/api/game/achievements", response_model=List[GameAchievement], tags=["Game Quest"])
async def list_game_achievements(current_user: Dict[str, Any] = Depends(get_optional_current_user)):
    """List all achievements/badges with player unlocked status."""
    return get_achievements_catalog(current_user["id"])


@app.post("/api/game/mission/complete", response_model=GameMissionCompleteOut, tags=["Game Quest"])
async def complete_game_mission(
    req: GameMissionCompleteIn,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Record mission completion, award mission XP, and trigger achievement / level evaluations."""
    return award_mission_completion(user_id=current_user["id"], mission_id=req.mission_id, score=req.score)


@app.post("/api/game/quiz/submit", response_model=GameQuizSubmitOut, tags=["Game Quest"])
async def submit_game_quiz(
    req: GameQuizSubmitIn,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Submit an answer to an educational quiz question. Awards +10 XP for correct answers."""
    return submit_quiz_answer(
        user_id=current_user["id"],
        quiz_id=req.quiz_id,
        question_id=req.question_id,
        selected_option=req.selected_option
    )


@app.post("/api/game/challenge/complete", response_model=GameChallengeCompleteOut, tags=["Game Quest"])
async def complete_game_challenge(
    req: GameChallengeCompleteIn,
    current_user: Dict[str, Any] = Depends(get_optional_current_user)
):
    """Complete an interactive mini-challenge (Balanced Plate, Blood Flow, Organ Explorer). Awards +50 XP."""
    return record_challenge_completion(
        user_id=current_user["id"],
        challenge_id=req.challenge_id,
        payload=req.data
    )


@app.post("/api/game/reset", response_model=GameProgressOut, tags=["Game Quest"])
async def reset_game_state(current_user: Dict[str, Any] = Depends(get_optional_current_user)):
    """Reset player progress and achievements for a fresh academic demo walkthrough."""
    return reset_demo_game_progress(current_user["id"])


# --- Exception Handlers ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Structured ErrorOut response for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorOut(
            code=f"HTTP_{exc.status_code}",
            message=exc.detail
        ).model_dump(mode="json")
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Structured ErrorOut response for validation failures (e.g. invalid MIME/units/range)."""
    clean_errors = [
        {
            "field": " -> ".join(str(loc) for loc in err.get("loc", [])),
            "message": str(err.get("msg", "")),
            "type": str(err.get("type", ""))
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorOut(
            code="VALIDATION_ERROR",
            message="Request input validation failed. Please check field types, units, and ranges.",
            details=clean_errors
        ).model_dump(mode="json")
    )


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Structured 404 response for missing routes."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorOut(
            code="NOT_FOUND",
            message=f"The requested path '{request.url.path}' was not found on this server."
        ).model_dump(mode="json")
    )
