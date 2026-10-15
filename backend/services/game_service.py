"""
NutriSphere Quest — Educational Game Progression & Mission Engine
Manages:
- Player XP, levels, and level progression
- Mission start, validation, and completion
- Educational quiz verification and feedback
- Interactive challenge verification (Balanced Plate, Blood Flow, Report Detective)
- Achievement tracking and persistent SQLite storage
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.database import get_db

# Level progression thresholds
LEVEL_THRESHOLDS = [
    (1, "Health Beginner", 0, 100),
    (2, "Body Explorer", 100, 250),
    (3, "Organ Investigator", 250, 450),
    (4, "Health Knowledge Builder", 450, 700),
    (5, "Body Systems Expert", 700, 10000)
]

ACHIEVEMENT_DEFINITIONS = [
    {
        "id": "first_mission",
        "title": "First Mission Completed",
        "description": "Completed your first interactive health exploration mission!",
        "icon": "🏆"
    },
    {
        "id": "organ_explorer",
        "title": "Organ Explorer",
        "description": "Explored all major human body organs in 3D!",
        "icon": "🔬"
    },
    {
        "id": "report_detective",
        "title": "Report Detective",
        "description": "Successfully decoded a laboratory report and matched findings to organs!",
        "icon": "🕵️"
    },
    {
        "id": "nutrition_learner",
        "title": "Nutrition Learner",
        "description": "Crafted a culturally balanced Indian meal plate!",
        "icon": "🥗"
    },
    {
        "id": "body_systems_explorer",
        "title": "Body Systems Explorer",
        "description": "Explored interconnected circulatory and digestive pathways in 3D!",
        "icon": "⚡"
    },
    {
        "id": "master_explorer",
        "title": "Master Health Explorer",
        "description": "Reached Level 5 and mastered all body systems missions!",
        "icon": "👑"
    }
]

MISSION_DEFINITIONS = [
    {
        "id": "liver_lab",
        "title": "Mission 1: The Liver Lab",
        "organ": "Liver",
        "badge": "Hepatic Station",
        "description": "Explore the liver, learn its 4 core metabolic functions, and decode liver enzyme tests.",
        "xp_reward": 100,
        "stages_count": 5
    },
    {
        "id": "heart_station",
        "title": "Mission 2: The Heart Station",
        "organ": "Heart",
        "badge": "Cardiovascular Control",
        "description": "Follow the path of blood through heart chambers, and learn about LDL and HDL cholesterol.",
        "xp_reward": 100,
        "stages_count": 5
    },
    {
        "id": "kidney_room",
        "title": "Mission 3: Kidney Control Room",
        "organ": "Kidneys",
        "badge": "Renal Operations",
        "description": "Discover how millions of nephrons filter waste and understand creatinine and eGFR.",
        "xp_reward": 100,
        "stages_count": 5
    },
    {
        "id": "digestive_journey",
        "title": "Mission 4: The Digestive Journey",
        "organ": "Stomach & Intestines",
        "badge": "Enteric Highway",
        "description": "Travel from mouth to small intestine and learn how vital nutrients get absorbed.",
        "xp_reward": 100,
        "stages_count": 5
    },
    {
        "id": "nutrition_plate",
        "title": "Mission 5: The Nutrition Challenge",
        "organ": "Whole Body",
        "badge": "Balanced Plate",
        "description": "Build a balanced Indian meal plate across vegetables, whole grains, protein, and healthy fats.",
        "xp_reward": 100,
        "stages_count": 4
    },
    {
        "id": "alcohol_journey",
        "title": "Mission 6: Alcohol & The Body",
        "organ": "Liver & Brain",
        "badge": "Clearance Science",
        "description": "Explore the 3D alcohol pathway and understand enzymatic clearance rates without myths.",
        "xp_reward": 100,
        "stages_count": 5
    },
    {
        "id": "report_detective",
        "title": "Signature Mission: Report Detective",
        "organ": "Diagnostic Lab",
        "badge": "Case Investigation",
        "description": "Analyze a patient laboratory report, find tests and healthy ranges, and match them to organs.",
        "xp_reward": 150,
        "stages_count": 6
    }
]

QUIZ_QUESTION_BANK = {
    # Liver Lab Quiz Questions
    "liv_q1": {
        "quiz_id": "liver_lab",
        "question": "What is the primary role of the liver in processing food and drinks?",
        "options": [
            "Pumping oxygen to leg muscles",
            "Filtering toxins, producing bile to digest fats, and storing energy",
            "Storing environmental air for breathing",
            "Producing stomach acid only"
        ],
        "correct_option": 1,
        "explanation": "The liver is your body's master chemical filter and energy center: it filters toxins, turns food into glycogen, and produces bile to break down fats."
    },
    "liv_q2": {
        "quiz_id": "liver_lab",
        "question": "What does a mildly high ALT (SGPT) enzyme test usually tell a doctor?",
        "options": [
            "A broken bone in the spine",
            "Liver cells are under temporary stress or irritation from diet, alcohol, or medications",
            "The heart has stopped beating",
            "Dehydration only"
        ],
        "correct_option": 1,
        "explanation": "ALT is found inside liver cells. When liver cells experience metabolic stress, ALT leaks into the bloodstream, alerting doctors to investigate lifestyle factors."
    },
    "liv_q3": {
        "quiz_id": "liver_lab",
        "question": "True or False: A slightly elevated liver enzyme result is always a permanent disease.",
        "options": [
            "True, liver cells cannot repair themselves",
            "False, liver cells have remarkable healing ability and enzymes often normalize with healthy habits"
        ],
        "correct_option": 1,
        "explanation": "False! The liver is resilient. Mild elevations are often temporary and improve with nourishing foods, reduced alcohol, and physical activity."
    },

    # Heart Station Quiz Questions
    "hrt_q1": {
        "quiz_id": "heart_station",
        "question": "Which chamber of the heart pumps oxygen-rich blood out to your entire body through the aorta?",
        "options": [
            "Right Atrium",
            "Right Ventricle",
            "Left Ventricle",
            "Pulmonary Vein"
        ],
        "correct_option": 2,
        "explanation": "The Left Ventricle has thick, muscular walls that pump fresh, oxygen-filled blood through the aorta to all 37 trillion cells in your body."
    },
    "hrt_q2": {
        "quiz_id": "heart_station",
        "question": "Why is LDL often referred to as 'bad' cholesterol?",
        "options": [
            "It turns blood blue",
            "Too many circulating LDL particles can slowly build up along artery walls",
            "It prevents digestion of all foods",
            "It causes immediate heart failure"
        ],
        "correct_option": 1,
        "explanation": "When there are more LDL particles than the body needs, they can deposit cholesterol in vessel walls. Soluble fiber (oats, beans) helps clear excess LDL."
    },

    # Kidney Room Quiz Questions
    "kid_q1": {
        "quiz_id": "kidney_room",
        "question": "What do the kidneys filter out of your blood?",
        "options": [
            "Excess water, salts, and nitrogen wastes (urea, creatinine) to make urine",
            "Solid food particles",
            "Only red blood cells",
            "Air bubbles"
        ],
        "correct_option": 0,
        "explanation": "Millions of microscopic nephrons filter blood 24/7, keeping essential proteins while balancing water, electrolytes, and clearing metabolic waste."
    },
    "kid_q2": {
        "quiz_id": "kidney_room",
        "question": "What does an eGFR value of 88 mL/min indicate?",
        "options": [
            "Immediate kidney failure requiring dialysis",
            "Normal, stable kidney filtration rate that effectively cleans the blood",
            "A heart problem",
            "Severe lung infection"
        ],
        "correct_option": 1,
        "explanation": "eGFR (estimated Glomerular Filtration Rate) measures filtration speed. A value around 88–90 mL/min represents healthy, functional kidney filtration."
    },

    # Digestive Journey Quiz Questions
    "dig_q1": {
        "quiz_id": "digestive_journey",
        "question": "Where does the majority of nutrient absorption take place in your body?",
        "options": [
            "In the mouth",
            "In the stomach",
            "In the small intestine with its microscopic villi",
            "In the kidneys"
        ],
        "correct_option": 2,
        "explanation": "The small intestine is lined with millions of tiny finger-like villi that absorb vitamins, minerals, amino acids, and glucose into the bloodstream."
    },
    "dig_q2": {
        "quiz_id": "digestive_journey",
        "question": "What is required from the stomach to absorb Vitamin B12 effectively?",
        "options": [
            "Intrinsic Factor produced by gastric parietal cells",
            "Bile from the gallbladder",
            "Insulin from the pancreas",
            "Tooth enamel"
        ],
        "correct_option": 0,
        "explanation": "Stomach cells secrete 'Intrinsic Factor', a special protein that binds to Vitamin B12 so it can be absorbed downstream in the small intestine."
    },

    # Alcohol Journey Quiz Questions
    "alc_q1": {
        "quiz_id": "alcohol_journey",
        "question": "Can black coffee or cold showers speed up how fast your liver clears alcohol?",
        "options": [
            "Yes, coffee burns alcohol in minutes",
            "No, liver enzymes metabolize alcohol at a fixed rate of about 7–10 grams per hour",
            "Yes, cold showers double metabolic enzyme speed",
            "Yes, sleeping clears it instantly"
        ],
        "correct_option": 1,
        "explanation": "Liver enzymes (ADH and CYP2E1) work at a fixed physiological rate. Neither coffee nor showers speed up alcohol elimination."
    },
    "alc_q2": {
        "quiz_id": "alcohol_journey",
        "question": "How much alcohol is absorbed directly through the stomach lining into the blood?",
        "options": [
            "0%",
            "About 20%, while the remaining 80% absorbs in the small intestine",
            "100% in the mouth",
            "None, it only enters lungs"
        ],
        "correct_option": 1,
        "explanation": "About 20% enters directly through the stomach wall into blood capillaries. Eating healthy meals before drinking slows this absorption down significantly."
    },

    # Report Detective Quiz Questions
    "rep_q1": {
        "quiz_id": "report_detective",
        "question": "What is a laboratory 'Reference Range' (or Reference Interval)?",
        "options": [
            "The monetary cost of a blood test",
            "The expected statistical range where 95% of healthy individuals fall",
            "A permanent legal diagnosis",
            "The manufacturer's serial code"
        ],
        "correct_option": 1,
        "explanation": "A reference interval represents the normal statistical range of values observed across healthy reference populations in standardized diagnostic labs."
    },
    "rep_q2": {
        "quiz_id": "report_detective",
        "question": "When a blood test like ALT is slightly above the reference range, what is the best next step?",
        "options": [
            "Panic and buy unverified online cures",
            "Review the report with your doctor alongside your symptoms and daily lifestyle",
            "Assume the entire laboratory made a mistake and do nothing",
            "Stop eating all food"
        ],
        "correct_option": 1,
        "explanation": "Blood tests are educational pieces of a broader health picture. Your doctor interprets them alongside your personal medical history, symptoms, and habits."
    }
}


def calculate_level_info(total_xp: int) -> tuple[int, str, int, int]:
    """
    Returns: (level, level_title, next_level_xp, xp_to_next_level)
    """
    current_level = 1
    current_title = "Health Beginner"
    next_level_xp = 100

    for lvl, title, min_xp, next_xp in LEVEL_THRESHOLDS:
        if total_xp >= min_xp:
            current_level = lvl
            current_title = title
            next_level_xp = next_xp

    xp_to_next = max(0, next_level_xp - total_xp)
    return current_level, current_title, next_level_xp, xp_to_next


def get_or_create_player_progress(user_id: str = "usr_demo_001") -> Dict[str, Any]:
    """Retrieve player's current progression, completed missions, and achievements."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Check existing progress
        cursor.execute("SELECT * FROM game_player_progress WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if not row:
            # Create default progress
            cursor.execute("""
                INSERT INTO game_player_progress (user_id, xp, level, level_title, current_mission, completed_missions_count)
                VALUES (?, 0, 1, 'Health Beginner', 'liver_lab', 0)
            """, (user_id,))
            conn.commit()
            cursor.execute("SELECT * FROM game_player_progress WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()

        total_xp = row["xp"]
        level, level_title, next_level_xp, xp_to_next = calculate_level_info(total_xp)

        # Update level if out of sync
        if level != row["level"] or level_title != row["level_title"]:
            cursor.execute("""
                UPDATE game_player_progress
                SET level = ?, level_title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (level, level_title, user_id))
            conn.commit()

        # Fetch completed missions
        cursor.execute("SELECT mission_id FROM game_missions WHERE user_id = ?", (user_id,))
        completed_missions = [r["mission_id"] for r in cursor.fetchall()]

        # Fetch unlocked achievements
        cursor.execute("SELECT achievement_id, unlocked_at FROM game_achievements WHERE user_id = ?", (user_id,))
        unlocked_map = {r["achievement_id"]: r["unlocked_at"] for r in cursor.fetchall()}

        achievements_list = []
        for ach in ACHIEVEMENT_DEFINITIONS:
            ach_id = ach["id"]
            is_unlocked = ach_id in unlocked_map
            achievements_list.append({
                "id": ach_id,
                "title": ach["title"],
                "description": ach["description"],
                "icon": ach["icon"],
                "unlocked": is_unlocked,
                "unlocked_at": unlocked_map.get(ach_id)
            })

        return {
            "user_id": user_id,
            "xp": total_xp,
            "level": level,
            "level_title": level_title,
            "current_mission": row["current_mission"] or "liver_lab",
            "completed_missions_count": len(completed_missions),
            "next_level_xp": next_level_xp,
            "xp_to_next_level": xp_to_next,
            "completed_missions": completed_missions,
            "unlocked_achievements": achievements_list
        }


def get_missions_catalog(user_id: str = "usr_demo_001") -> List[Dict[str, Any]]:
    """Retrieve full catalog of missions with user completion status and associated quiz questions."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT mission_id, score, completed_at FROM game_missions WHERE user_id = ?", (user_id,))
        completed = {r["mission_id"]: {"score": r["score"], "completed_at": r["completed_at"]} for r in cursor.fetchall()}

    result = []
    for m in MISSION_DEFINITIONS:
        m_id = m["id"]
        is_done = m_id in completed
        questions = [
            {"id": qid, "question": q["question"], "options": q["options"]}
            for qid, q in QUIZ_QUESTION_BANK.items()
            if q.get("quiz_id") == m_id
        ]
        result.append({
            **m,
            "completed": is_done,
            "score": completed[m_id]["score"] if is_done else 0,
            "completed_at": completed[m_id]["completed_at"] if is_done else None,
            "questions": questions
        })
    return result


def get_achievements_catalog(user_id: str = "usr_demo_001") -> List[Dict[str, Any]]:
    """Retrieve full catalog of badges with user unlocked status."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT achievement_id, unlocked_at FROM game_achievements WHERE user_id = ?", (user_id,))
        unlocked = {r["achievement_id"]: r["unlocked_at"] for r in cursor.fetchall()}

    result = []
    for ach in ACHIEVEMENT_DEFINITIONS:
        ach_id = ach["id"]
        is_unlocked = ach_id in unlocked
        result.append({
            **ach,
            "unlocked": is_unlocked,
            "unlocked_at": unlocked.get(ach_id)
        })
    return result


def award_mission_completion(user_id: str, mission_id: str, score: int = 100) -> Dict[str, Any]:
    """Record mission completion, award XP, evaluate level up and achievements."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Check if already completed
        cursor.execute("SELECT * FROM game_missions WHERE user_id = ? AND mission_id = ?", (user_id, mission_id))
        existing = cursor.fetchone()

        # Determine XP reward based on mission catalog
        mission_def = next((m for m in MISSION_DEFINITIONS if m["id"] == mission_id), None)
        base_xp = mission_def["xp_reward"] if mission_def else 100

        xp_to_award = 0
        if not existing:
            xp_to_award = base_xp
            cursor.execute("""
                INSERT INTO game_missions (id, user_id, mission_id, score, xp_earned)
                VALUES (?, ?, ?, ?, ?)
            """, (f"gmis_{uuid.uuid4().hex[:12]}", user_id, mission_id, score, xp_to_award))
        else:
            # Replay practice bonus (+10 XP)
            xp_to_award = 10
            cursor.execute("""
                UPDATE game_missions
                SET score = MAX(score, ?), completed_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND mission_id = ?
            """, (score, user_id, mission_id))

        # Get current progress
        cursor.execute("SELECT xp, level FROM game_player_progress WHERE user_id = ?", (user_id,))
        curr = cursor.fetchone()
        current_xp = curr["xp"] if curr else 0
        old_level = curr["level"] if curr else 1

        new_total_xp = current_xp + xp_to_award
        new_level, new_title, _, _ = calculate_level_info(new_total_xp)
        level_up = (new_level > old_level)

        # Update progress
        cursor.execute("""
            INSERT INTO game_player_progress (user_id, xp, level, level_title, completed_missions_count, updated_at)
            VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                xp = ?,
                level = ?,
                level_title = ?,
                completed_missions_count = (SELECT COUNT(*) FROM game_missions WHERE user_id = ?),
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, new_total_xp, new_level, new_title, new_total_xp, new_level, new_title, user_id))

        # Check achievements
        new_achievements = []

        # 1. First mission
        cursor.execute("SELECT 1 FROM game_achievements WHERE user_id = ? AND achievement_id = 'first_mission'", (user_id,))
        if not cursor.fetchone():
            ach_def = next(a for a in ACHIEVEMENT_DEFINITIONS if a["id"] == "first_mission")
            cursor.execute("""
                INSERT INTO game_achievements (id, user_id, achievement_id, title, description, icon)
                VALUES (?, ?, 'first_mission', ?, ?, ?)
            """, (f"gach_{uuid.uuid4().hex[:12]}", user_id, ach_def["title"], ach_def["description"], ach_def["icon"]))
            new_achievements.append({**ach_def, "unlocked": True, "unlocked_at": datetime.now(timezone.utc).isoformat()})

        # 2. Report Detective achievement
        if mission_id == "report_detective":
            cursor.execute("SELECT 1 FROM game_achievements WHERE user_id = ? AND achievement_id = 'report_detective'", (user_id,))
            if not cursor.fetchone():
                ach_def = next(a for a in ACHIEVEMENT_DEFINITIONS if a["id"] == "report_detective")
                cursor.execute("""
                    INSERT INTO game_achievements (id, user_id, achievement_id, title, description, icon)
                    VALUES (?, ?, 'report_detective', ?, ?, ?)
                """, (f"gach_{uuid.uuid4().hex[:12]}", user_id, ach_def["title"], ach_def["description"], ach_def["icon"]))
                new_achievements.append({**ach_def, "unlocked": True, "unlocked_at": datetime.now(timezone.utc).isoformat()})

        # 3. Nutrition Learner
        if mission_id == "nutrition_plate":
            cursor.execute("SELECT 1 FROM game_achievements WHERE user_id = ? AND achievement_id = 'nutrition_learner'", (user_id,))
            if not cursor.fetchone():
                ach_def = next(a for a in ACHIEVEMENT_DEFINITIONS if a["id"] == "nutrition_learner")
                cursor.execute("""
                    INSERT INTO game_achievements (id, user_id, achievement_id, title, description, icon)
                    VALUES (?, ?, 'nutrition_learner', ?, ?, ?)
                """, (f"gach_{uuid.uuid4().hex[:12]}", user_id, ach_def["title"], ach_def["description"], ach_def["icon"]))
                new_achievements.append({**ach_def, "unlocked": True, "unlocked_at": datetime.now(timezone.utc).isoformat()})

        # 4. Body Systems Explorer (>= 4 completed missions)
        cursor.execute("SELECT COUNT(*) as cnt FROM game_missions WHERE user_id = ?", (user_id,))
        m_count = cursor.fetchone()["cnt"]
        if m_count >= 4:
            cursor.execute("SELECT 1 FROM game_achievements WHERE user_id = ? AND achievement_id = 'body_systems_explorer'", (user_id,))
            if not cursor.fetchone():
                ach_def = next(a for a in ACHIEVEMENT_DEFINITIONS if a["id"] == "body_systems_explorer")
                cursor.execute("""
                    INSERT INTO game_achievements (id, user_id, achievement_id, title, description, icon)
                    VALUES (?, ?, 'body_systems_explorer', ?, ?, ?)
                """, (f"gach_{uuid.uuid4().hex[:12]}", user_id, ach_def["title"], ach_def["description"], ach_def["icon"]))
                new_achievements.append({**ach_def, "unlocked": True, "unlocked_at": datetime.now(timezone.utc).isoformat()})

        # 5. Master Explorer (Level 5)
        if new_level >= 5:
            cursor.execute("SELECT 1 FROM game_achievements WHERE user_id = ? AND achievement_id = 'master_explorer'", (user_id,))
            if not cursor.fetchone():
                ach_def = next(a for a in ACHIEVEMENT_DEFINITIONS if a["id"] == "master_explorer")
                cursor.execute("""
                    INSERT INTO game_achievements (id, user_id, achievement_id, title, description, icon)
                    VALUES (?, ?, 'master_explorer', ?, ?, ?)
                """, (f"gach_{uuid.uuid4().hex[:12]}", user_id, ach_def["title"], ach_def["description"], ach_def["icon"]))
                new_achievements.append({**ach_def, "unlocked": True, "unlocked_at": datetime.now(timezone.utc).isoformat()})

        conn.commit()

        return {
            "success": True,
            "mission_id": mission_id,
            "xp_earned": xp_to_award,
            "total_xp": new_total_xp,
            "level": new_level,
            "level_title": new_title,
            "level_up": level_up,
            "new_achievements": new_achievements,
            "message": f"Mission '{mission_def['title'] if mission_def else mission_id}' completed! +{xp_to_award} XP awarded."
        }


def submit_quiz_answer(user_id: str, quiz_id: str, question_id: str, selected_option: int) -> Dict[str, Any]:
    """Verify question answer, award +10 XP if correct and not previously answered correctly."""
    q_data = QUIZ_QUESTION_BANK.get(question_id)
    if not q_data:
        return {
            "quiz_id": quiz_id,
            "question_id": question_id,
            "is_correct": False,
            "xp_awarded": 0,
            "total_xp": 0,
            "explanation": "Question not found in the game question bank.",
            "correct_option": -1
        }

    is_correct = (selected_option == q_data["correct_option"])
    xp_to_award = 0

    with get_db() as conn:
        cursor = conn.cursor()

        # Check prior correct answers
        cursor.execute("""
            SELECT is_correct FROM game_quiz_answers
            WHERE user_id = ? AND question_id = ? AND is_correct = 1
        """, (user_id, question_id))
        prior_correct = cursor.fetchone()

        if is_correct and not prior_correct:
            xp_to_award = 10

        # Log answer attempt
        cursor.execute("""
            INSERT INTO game_quiz_answers (id, user_id, quiz_id, question_id, is_correct, xp_awarded)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f"ans_{uuid.uuid4().hex[:12]}", user_id, quiz_id, question_id, 1 if is_correct else 0, xp_to_award))

        # Award XP if any
        if xp_to_award > 0:
            cursor.execute("SELECT xp FROM game_player_progress WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            curr_xp = row["xp"] if row else 0
            new_xp = curr_xp + xp_to_award
            new_level, new_title, _, _ = calculate_level_info(new_xp)

            cursor.execute("""
                INSERT INTO game_player_progress (user_id, xp, level, level_title, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    xp = ?,
                    level = ?,
                    level_title = ?,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, new_xp, new_level, new_title, new_xp, new_level, new_title))

        conn.commit()

        cursor.execute("SELECT xp FROM game_player_progress WHERE user_id = ?", (user_id,))
        final_xp = cursor.fetchone()["xp"]

        return {
            "quiz_id": quiz_id,
            "question_id": question_id,
            "is_correct": is_correct,
            "xp_awarded": xp_to_award,
            "total_xp": final_xp,
            "explanation": q_data["explanation"],
            "correct_option": q_data["correct_option"]
        }


def record_challenge_completion(user_id: str, challenge_id: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Award +50 XP for interactive mini-challenges (Plate Building, Circulation route, Organ Explorer)."""
    with get_db() as conn:
        cursor = conn.cursor()

        xp_award = 50
        cursor.execute("SELECT xp FROM game_player_progress WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        curr_xp = row["xp"] if row else 0
        new_xp = curr_xp + xp_award
        new_level, new_title, _, _ = calculate_level_info(new_xp)

        cursor.execute("""
            INSERT INTO game_player_progress (user_id, xp, level, level_title, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                xp = ?,
                level = ?,
                level_title = ?,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, new_xp, new_level, new_title, new_xp, new_level, new_title))

        new_achievements = []
        if challenge_id in {"organ_explorer", "3d_body_map"}:
            cursor.execute("SELECT 1 FROM game_achievements WHERE user_id = ? AND achievement_id = 'organ_explorer'", (user_id,))
            if not cursor.fetchone():
                ach_def = next(a for a in ACHIEVEMENT_DEFINITIONS if a["id"] == "organ_explorer")
                cursor.execute("""
                    INSERT INTO game_achievements (id, user_id, achievement_id, title, description, icon)
                    VALUES (?, ?, 'organ_explorer', ?, ?, ?)
                """, (f"gach_{uuid.uuid4().hex[:12]}", user_id, ach_def["title"], ach_def["description"], ach_def["icon"]))
                new_achievements.append({**ach_def, "unlocked": True, "unlocked_at": datetime.now(timezone.utc).isoformat()})

        conn.commit()

        return {
            "challenge_id": challenge_id,
            "success": True,
            "xp_earned": xp_award,
            "total_xp": new_xp,
            "feedback": f"Challenge '{challenge_id.replace('_', ' ').title()}' completed! +{xp_award} XP awarded.",
            "new_achievements": new_achievements
        }


def reset_demo_game_progress(user_id: str = "usr_demo_001") -> Dict[str, Any]:
    """Reset demo game progress for fresh academic walkthroughs."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM game_missions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM game_achievements WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM game_quiz_answers WHERE user_id = ?", (user_id,))
        cursor.execute("""
            INSERT OR REPLACE INTO game_player_progress (user_id, xp, level, level_title, current_mission, completed_missions_count, updated_at)
            VALUES (?, 0, 1, 'Health Beginner', 'liver_lab', 0, CURRENT_TIMESTAMP)
        """, (user_id,))
        conn.commit()

    return get_or_create_player_progress(user_id)
