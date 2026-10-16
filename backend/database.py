"""
NutriSphere 3D - Database Configuration & Schema Management
Configures SQLite with thread-safe connections, foreign keys enabled, WAL mode,
PBKDF2-HMAC-SHA256 password security, and relational DDL tables:
users, reports, biomarkers, interpretations, medications, nutrition_preferences, audit_events, test_catalog.
"""

import os
import sqlite3
import hashlib
import secrets
from pathlib import Path
from contextlib import contextmanager

import shutil

BASE_DIR = Path(__file__).resolve().parent.parent

def _get_db_path() -> str:
    """Resolve database path, copying to /tmp in serverless/Vercel environments with read-only root."""
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = Path("/tmp/nutrisphere3d.db")
        source_db = BASE_DIR / "nutrisphere3d.db"
        if not tmp_db.exists() and source_db.exists():
            try:
                shutil.copy2(source_db, tmp_db)
            except Exception as e:
                print(f"[Database] Warning copying seed DB to /tmp: {e}")
        return os.environ.get("NUTRISPHERE_DB_PATH", str(tmp_db))
    return os.environ.get("NUTRISPHERE_DB_PATH", str(BASE_DIR / "nutrisphere3d.db"))

DB_PATH = _get_db_path()


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with 200,000 iterations (OWASP recommendation).
    Never stores plaintext passwords.
    Returns: (salt_hex, hash_hex)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200000
    )
    return salt, key.hex()


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    """Verify that a plaintext password matches the stored salted hash."""
    _, key_hex = hash_password(password, salt=salt)
    return secrets.compare_digest(key_hex, expected_hash)


def get_db_connection() -> sqlite3.Connection:
    """Create a configured SQLite database connection."""
    target_path = _get_db_path()
    conn = sqlite3.connect(target_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    # Enforce foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    # WAL mode requires shared memory; use standard rollback journal in serverless environments
    if not os.environ.get("VERCEL") and not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        conn.execute("PRAGMA journal_mode = WAL;")
    return conn


@contextmanager
def get_db():
    """Context manager for transaction management and auto-closing connections."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create all relational tables and seed baseline local demo user."""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Users table (Zero plaintext passwords)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT,
                is_active INTEGER DEFAULT 1,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Test Catalog table (Extensible clinical dictionary)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_catalog (
                analyte_code TEXT PRIMARY KEY,
                canonical_name TEXT NOT NULL,
                panel TEXT NOT NULL,
                aliases TEXT,
                standard_unit TEXT NOT NULL,
                acceptable_units TEXT,
                unit_conversions TEXT,
                reference_low REAL,
                reference_high REAL,
                reference_text TEXT,
                contextual_ranges TEXT,
                organ_system TEXT NOT NULL,
                educational_explanation TEXT,
                clinical_questions TEXT,
                medical_references TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                file_name TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                file_size_bytes INTEGER,
                file_path TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                collection_date TEXT,
                laboratory_name TEXT,
                analysis_status TEXT DEFAULT 'pending',
                source_hash TEXT,
                extraction_notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        try:
            cursor.execute("ALTER TABLE reports ADD COLUMN file_path TEXT;")
        except Exception:
            pass

        # 4. Biomarkers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS biomarkers (
                id TEXT PRIMARY KEY,
                report_id TEXT NOT NULL,
                analyte_code TEXT NOT NULL,
                label TEXT NOT NULL,
                value_numeric REAL,
                value_text TEXT,
                unit TEXT,
                reference_low REAL,
                reference_high REAL,
                reference_text TEXT,
                flag TEXT DEFAULT 'unknown',
                collection_date TEXT,
                source_page INTEGER DEFAULT 1,
                extraction_confidence REAL DEFAULT 1.0,
                FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
            );
        """)

        # 5. Interpretations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interpretations (
                id TEXT PRIMARY KEY,
                biomarker_id TEXT NOT NULL,
                explanation TEXT NOT NULL,
                reasoning_limits TEXT NOT NULL,
                followup TEXT,
                clinical_questions TEXT,
                medical_reference TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (biomarker_id) REFERENCES biomarkers(id) ON DELETE CASCADE
            );
        """)

        # 6. Medications table (Opt-in structured clinical context)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                report_id TEXT,
                drug_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                started_date TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE SET NULL
            );
        """)

        # 7. Nutrition Preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_preferences (
                id TEXT PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                dietary_pattern TEXT DEFAULT 'vegetarian',
                allergies TEXT DEFAULT '[]',
                cultural_restrictions TEXT,
                calorie_tracking_opt_in INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 8. Audit Events table (Traceability and access control auditing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                event_type TEXT NOT NULL,
                resource_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_hash TEXT,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # 9. Alcohol Intake Records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alcohol_intake_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                beverage_type TEXT NOT NULL,
                volume_ml REAL NOT NULL,
                abv_percent REAL NOT NULL,
                pure_alcohol_grams REAL NOT NULL,
                standard_drinks REAL NOT NULL,
                drinking_days_per_week INTEGER DEFAULT 1,
                weekly_grams REAL NOT NULL,
                recorded_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 10. Game Player Progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_player_progress (
                user_id TEXT PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                level_title TEXT DEFAULT 'Health Beginner',
                current_mission TEXT DEFAULT 'liver_lab',
                completed_missions_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # 11. Game Missions Completed table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_missions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                mission_id TEXT NOT NULL,
                score INTEGER DEFAULT 100,
                xp_earned INTEGER DEFAULT 100,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, mission_id)
            );
        """)

        # 12. Game Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_achievements (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                icon TEXT NOT NULL,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, achievement_id)
            );
        """)

        # 13. Game Quiz Answers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_quiz_answers (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                quiz_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                xp_awarded INTEGER DEFAULT 0,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Create indexing for lookup performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_user ON reports(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_biomarkers_report ON biomarkers(report_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_biomarkers_analyte ON biomarkers(analyte_code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_catalog_panel ON test_catalog(panel);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_events(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alcohol_user ON alcohol_intake_records(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_progress_user ON game_player_progress(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_missions_user ON game_missions(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_achievements_user ON game_achievements(user_id);")

        # Provision local demo account safely (repeatable)
        demo_user_id = "usr_demo_001"
        salt, p_hash = hash_password("DemoPatient2026!")
        cursor.execute("""
            INSERT OR REPLACE INTO users (id, username, email, password_hash, salt, full_name, is_active, role)
            VALUES (?, ?, ?, ?, ?, ?, 1, 'demo_user');
        """, (demo_user_id, "demouser", "demo@nutrisphere3d.local", p_hash, salt, "Synthetic Demo Patient"))

        # Provision secondary user for cross-user security and multi-tenant testing
        sec_user_id = "usr_demo_002"
        sec_salt, sec_hash = hash_password("SecondUser2026!")
        cursor.execute("""
            INSERT OR REPLACE INTO users (id, username, email, password_hash, salt, full_name, is_active, role)
            VALUES (?, ?, ?, ?, ?, ?, 1, 'user');
        """, (sec_user_id, "seconduser", "second@nutrisphere3d.local", sec_hash, sec_salt, "Secondary Test Patient"))

        # Provision default nutrition preferences for demo user
        cursor.execute("""
            INSERT OR IGNORE INTO nutrition_preferences (id, user_id, dietary_pattern, allergies, cultural_restrictions)
            VALUES ('pref_demo_001', ?, 'vegetarian', '["peanuts"]', 'Indian Traditional / Jain friendly options');
        """, (demo_user_id,))

        # Seed baseline synthetic alcohol record for demo user
        cursor.execute("""
            INSERT OR IGNORE INTO alcohol_intake_records (
                id, user_id, beverage_type, volume_ml, abv_percent, pure_alcohol_grams,
                standard_drinks, drinking_days_per_week, weekly_grams, recorded_date
            ) VALUES (
                'alc_demo_001', ?, 'Beer', 660.0, 5.0, 26.04, 2.6, 2, 52.08, '2026-09-15'
            );
        """, (demo_user_id,))

        # Record audit event for account creation
        cursor.execute("""
            INSERT OR IGNORE INTO audit_events (id, user_id, event_type, resource_id, details)
            VALUES ('evt_init_001', ?, 'SYSTEM_INIT', 'usr_demo_001', 'Seeded local demo account with PBKDF2 hash.');
        """, (demo_user_id,))

        # Initialize Game Progress for demo user
        cursor.execute("""
            INSERT OR IGNORE INTO game_player_progress (user_id, xp, level, level_title, current_mission, completed_missions_count)
            VALUES (?, 120, 2, 'Body Explorer', 'liver_lab', 1);
        """, (demo_user_id,))

        cursor.execute("""
            INSERT OR IGNORE INTO game_missions (id, user_id, mission_id, score, xp_earned)
            VALUES ('gmis_demo_001', ?, 'organ_explorer', 100, 100);
        """, (demo_user_id,))

        cursor.execute("""
            INSERT OR IGNORE INTO game_achievements (id, user_id, achievement_id, title, description, icon)
            VALUES ('gach_demo_001', ?, 'first_mission', 'First Mission Completed', 'Completed your first interactive health exploration mission!', '🏆');
        """, (demo_user_id,))
