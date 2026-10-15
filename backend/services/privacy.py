"""
NutriSphere 3D - Privacy, Authorization & Validation Utilities
Enforces:
- File size validation (max 15MB)
- MIME type validation (PDF, JPG, PNG only)
- Safe filename sanitization (prevents path traversal)
- Report ownership authorization (blocks cross-user data access)
- Conspicuous deletion controls with audit logging
- Zero-logging of raw report content or biomarker values (PHI privacy guarantee)
"""

import os
import re
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status

from backend.database import get_db

MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}


def validate_file_metadata(file_size_bytes: int, mime_type: str, file_name: str) -> str:
    """
    Validate file upload constraints.
    Raises HTTPException(413) if too large.
    Raises HTTPException(415) if invalid MIME type.
    Raises HTTPException(400) if invalid path/filename.
    Returns sanitized filename.
    """
    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of 15MB (got {file_size_bytes / (1024 * 1024):.2f}MB)."
        )

    if mime_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{mime_type}'. Supported types: PDF, JPEG, PNG."
        )

    # Sanitize filename & prevent path traversal
    clean_name = os.path.basename(file_name)
    clean_name = re.sub(r"[^\w\.\-_]", "_", clean_name)
    ext = Path(clean_name).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File extension '{ext}' is not permitted."
        )

    return clean_name


def verify_report_ownership(report_user_id: str, authenticated_user_id: str):
    """
    Ensure user owns the requested report before granting access.
    Raises HTTPException(403) or 404 on mismatch.
    """
    if report_user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to view or modify this medical report."
        )


def log_safe_audit_event(
    event_type: str,
    user_id: Optional[str],
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    client_ip: Optional[str] = None,
    conn=None
) -> str:
    """
    Log an operational audit event into SQLite.
    Privacy guarantee: Never logs report textual content, patient name, or extracted biomarker values.
    """
    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    insert_sql = """
        INSERT INTO audit_events (id, user_id, event_type, resource_id, details)
        VALUES (?, ?, ?, ?, ?);
    """
    params = (event_id, user_id, event_type, resource_id, details or "Operational event recorded without PHI.")

    if conn is not None:
        conn.execute(insert_sql, params)
    else:
        with get_db() as local_conn:
            local_conn.execute(insert_sql, params)
    return event_id


def delete_report_with_audit(report_id: str, current_user_id: str) -> Dict[str, Any]:
    """
    Conspicuously and permanently delete a user-owned medical report and associated records.
    Foreign key cascading purges biomarkers and interpretations automatically.
    Safely unlinks physical uploaded files and temporary artifacts from disk.
    """
    with get_db() as conn:
        report = conn.execute("SELECT user_id, file_name, file_path FROM reports WHERE id = ?;", (report_id,)).fetchone()
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical report '{report_id}' was not found."
            )

        # Verify owner authorization
        verify_report_ownership(report["user_id"], current_user_id)

        # 1. Unlink physical file on disk if present
        saved_file_path = report["file_path"]
        if saved_file_path:
            p = Path(saved_file_path)
            try:
                if p.exists() and p.is_file():
                    p.unlink(missing_ok=True)
            except Exception:
                pass

        # Also purge any artifacts matching report_id in uploads directory
        uploads_user_dir = Path(__file__).resolve().parent.parent.parent / "uploads" / current_user_id
        if uploads_user_dir.exists():
            for f in uploads_user_dir.glob(f"{report_id}*"):
                try:
                    if f.is_file():
                        f.unlink(missing_ok=True)
                except Exception:
                    pass

        # 2. Execute database deletion (cascades to biomarkers & interpretations)
        conn.execute("DELETE FROM reports WHERE id = ?;", (report_id,))

        # 3. Record audit log using the same connection transaction
        audit_id = log_safe_audit_event(
            event_type="REPORT_PERMANENT_DELETION",
            user_id=current_user_id,
            resource_id=report_id,
            details=f"Permanently purged report '{report['file_name']}', disk files, and child biomarker records.",
            conn=conn
        )

    return {
        "report_id": report_id,
        "status": "deleted",
        "message": "Report, physical files, and associated extracted biomarkers purged completely from storage.",
        "audit_event_id": audit_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
