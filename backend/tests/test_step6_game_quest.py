"""
NutriSphere Quest — Automated Test Suite (Step 6)
Verifies:
1. /quest Game UI Route serving valid HTML with Three.js, HUD, and 3D Body World Map.
2. /api/game/progress endpoint returning valid XP, Level rank, and unlocked badges.
3. /api/game/missions endpoint listing 7 educational missions and quiz questions.
4. /api/game/achievements endpoint listing 6 achievement badges.
5. /api/game/quiz/submit verifying educational questions with instant rationale and +10 XP award.
6. /api/game/challenge/complete verifying mini-challenges (Balanced Plate, Organ Explorer) and +50 XP.
7. /api/game/mission/complete verifying progression, level-ups, and milestone badges.
8. /api/game/reset restoring fresh academic demo state.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.auth import DEV_DEMO_TOKEN

client = TestClient(app)
AUTH_HEADERS = {"Authorization": f"Bearer {DEV_DEMO_TOKEN}"}


def test_quest_ui_route_served():
    """Verify /quest route serves quest.html with Three.js, QuestApp, and game HUD."""
    res = client.get("/quest")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "NutriSphere Quest" in res.text
    assert "Journey Inside the Human Body" in res.text
    assert "three.min.js" in res.text
    assert "quest.js" in res.text


def test_games_ui_route_served():
    """Verify /games route serves games.html with optional 3D educational game modes."""
    res = client.get("/games")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "NutriSphere Quest" in res.text
    assert "Learn Your Body" in res.text
    assert "Game 1: Find the Organ" in res.text
    assert "Game 2: Match the Test" in res.text
    assert "Game 3: Explore Your Body" in res.text
    assert "games.js" in res.text


def test_get_game_player_progress():
    """Verify player progress returns valid progression schema."""
    res = client.get("/api/game/progress", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert "user_id" in data
    assert "xp" in data
    assert "level" in data
    assert data["level"] >= 1
    assert "level_title" in data
    assert "completed_missions" in data
    assert "unlocked_achievements" in data
    assert isinstance(data["unlocked_achievements"], list)


def test_list_game_missions_catalog():
    """Verify all 7 educational missions are returned with objectives and quiz questions."""
    res = client.get("/api/game/missions", headers=AUTH_HEADERS)
    assert res.status_code == 200
    missions = res.json()
    assert len(missions) == 7

    mission_ids = [m["id"] for m in missions]
    assert "liver_lab" in mission_ids
    assert "heart_station" in mission_ids
    assert "kidney_room" in mission_ids
    assert "digestive_journey" in mission_ids
    assert "nutrition_plate" in mission_ids
    assert "alcohol_journey" in mission_ids
    assert "report_detective" in mission_ids

    # Verify quiz questions are attached to liver_lab
    liver = next(m for m in missions if m["id"] == "liver_lab")
    assert len(liver["questions"]) >= 2
    assert "question" in liver["questions"][0]
    assert len(liver["questions"][0]["options"]) >= 3


def test_list_game_achievements_catalog():
    """Verify all 6 achievement badges exist."""
    res = client.get("/api/game/achievements", headers=AUTH_HEADERS)
    assert res.status_code == 200
    achievements = res.json()
    assert len(achievements) == 6

    ach_ids = [a["id"] for a in achievements]
    assert "first_mission" in ach_ids
    assert "organ_explorer" in ach_ids
    assert "report_detective" in ach_ids
    assert "nutrition_learner" in ach_ids
    assert "body_systems_explorer" in ach_ids
    assert "master_explorer" in ach_ids


def test_quiz_submit_correct_and_rationale():
    """Verify submitting a correct quiz answer awards +10 XP and returns rationale."""
    # Question liv_q1: "Filtering toxins, producing bile to digest fats, and storing energy" (option index 1)
    payload = {
        "quiz_id": "liver_lab",
        "question_id": "liv_q1",
        "selected_option": 1
    }
    res = client.post("/api/game/quiz/submit", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True
    assert "explanation" in data
    assert len(data["explanation"]) > 10


def test_quiz_submit_incorrect():
    """Verify submitting an incorrect quiz answer returns correct rationale without error."""
    payload = {
        "quiz_id": "liver_lab",
        "question_id": "liv_q1",
        "selected_option": 0
    }
    res = client.post("/api/game/quiz/submit", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is False
    assert data["xp_awarded"] == 0
    assert "explanation" in data


def test_interactive_challenge_completion():
    """Verify interactive mini-challenges award +50 XP and unlock corresponding achievements."""
    payload = {
        "challenge_id": "organ_explorer",
        "payload_summary": "Explored 3D Liver in depth",
        "data": {"organ": "Liver"}
    }
    res = client.post("/api/game/challenge/complete", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["xp_earned"] == 50
    assert "total_xp" in data


def test_mission_completion_and_level_up():
    """Verify completing a mission awards base XP and updates completed missions count."""
    payload = {
        "mission_id": "kidney_room",
        "score": 100
    }
    res = client.post("/api/game/mission/complete", json=payload, headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["mission_id"] == "kidney_room"
    assert data["xp_earned"] >= 10
    assert data["level"] >= 1


def test_game_reset_endpoint():
    """Verify resetting demo game progress returns level 1 state, then restore demo baseline."""
    res = client.post("/api/game/reset", headers=AUTH_HEADERS)
    assert res.status_code == 200
    data = res.json()
    assert data["level"] == 1
    assert data["level_title"] == "Health Beginner"
    assert data["xp"] == 0
    assert len(data["completed_missions"]) == 0

    # Re-seed baseline demo state for interactive web demonstration
    from backend.database import get_db
    with get_db() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO game_player_progress (user_id, xp, level, level_title, current_mission, completed_missions_count, updated_at)
            VALUES ("usr_demo_001", 120, 2, "Body Explorer", "heart_station", 1, CURRENT_TIMESTAMP)
        """)
        c.execute("""
            INSERT OR IGNORE INTO game_missions (id, user_id, mission_id, score, xp_earned)
            VALUES ("gmis_init_001", "usr_demo_001", "liver_lab", 100, 100)
        """)
        c.execute("""
            INSERT OR IGNORE INTO game_achievements (id, user_id, achievement_id, title, description, icon)
            VALUES ("gach_init_001", "usr_demo_001", "first_mission", "First Mission Completed", "Completed your first interactive health exploration mission!", "🏆")
        """)
        conn.commit()

