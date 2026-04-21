"""
json_db.py - PostgreSQL backend (Supabase).
Zachovává všechna veřejná API tak, aby routy nemusely být měněny.
"""

import os
import uuid
from datetime import datetime
from typing import Callable, Dict, List, Optional

import psycopg2
import psycopg2.pool
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

# ── Konstanty (zachovány kvůli kompatibilitě s routami) ──────────────────────
FOODS_FILE           = "foods"
USERS_FILE           = "users"
LOGS_FILE            = "logs"
ADVISOR_CLIENTS_FILE = "advisor_clients"
MESSAGES_FILE        = "messages"
WEIGHT_FILE          = "weight_entries"

# ── DB config + connection pool ───────────────────────────────────────────────
_POOL = None


def _get_pool():
    global _POOL
    if _POOL is None:
        _POOL = psycopg2.pool.ThreadedConnectionPool(
            1, 5,
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dbname=os.getenv("DB_NAME"),
            sslmode="require",
            connect_timeout=10,
        )
    return _POOL


def _conn():
    """Vrátí spojení z poolu pro aktuální Flask request (přes g)."""
    try:
        from flask import g
        if not hasattr(g, "_db_conn") or g._db_conn.closed:
            g._db_conn = _get_pool().getconn()
        return g._db_conn
    except RuntimeError:
        return _get_pool().getconn()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch_all(sql: str, params: tuple = ()) -> List[Dict]:
    cnx = _conn()
    cur = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    result = [dict(r) for r in cur.fetchall()]
    cur.close()
    return result


def _fetch_one(sql: str, params: tuple = ()) -> Optional[Dict]:
    cnx = _conn()
    cur = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else None


def _execute(sql: str, params: tuple = ()) -> None:
    cnx = _conn()
    cur = cnx.cursor()
    cur.execute(sql, params)
    cnx.commit()
    cur.close()


# ── Row → dict konverze ───────────────────────────────────────────────────────

def _user_from_row(row: Dict) -> Dict:
    settings = {
        "age":            row.get("age"),
        "weight":         row.get("weight"),
        "height":         row.get("height"),
        "gender":         row.get("gender"),
        "activity":       row.get("activity", 1.55),
        "goal":           row.get("goal", "maintain"),
        "kcal_target":    row.get("kcal_target", 2000),
        "protein_target": row.get("protein_target", 150),
        "carbs_target":   row.get("carbs_target", 250),
        "fat_target":     row.get("fat_target", 70),
        "water_goal_ml":  row.get("water_goal_ml", 2500),
        "goal_weight":    row.get("goal_weight"),
    }
    return {
        "id":            row["id"],
        "name":          row.get("name"),
        "email":         row["email"],
        "password_hash": row["password_hash"],
        "role":          row["role"],
        "is_premium":    bool(row["is_premium"]),
        "settings":      settings,
    }


def _message_from_row(row: Dict) -> Dict:
    sent = row.get("sent_at", "")
    return {
        "id":            str(row["id"]),
        "advisor_id":    str(row["advisor_id"]),
        "advisor_email": row["advisor_email"],
        "client_id":     str(row["client_id"]),
        "text":          row["text"],
        "timestamp":     str(sent) if sent else "",
        "read":          bool(row["is_read"]),
        "sender":        row.get("sender", "advisor"),
    }


def _log_from_rows(log_row: Dict, meal_rows: list, activity_rows: list, water_rows: list) -> Dict:
    meals: Dict[str, list] = {
        "snidane": [], "svacina": [], "obed": [], "svacina2": [], "vecere": []
    }
    for m in meal_rows:
        entry = {
            "entry_id":    m["id"],
            "food_id":     m.get("food_id", ""),
            "name":        m["name"],
            "grams":       float(m["grams"]),
            "kcal":        float(m["kcal"]),
            "protein":     float(m["protein"]),
            "carbs":       float(m["carbs"]),
            "fat":         float(m["fat"]),
            "fiber":       float(m.get("fiber") or 0),
            "sugars":      float(m.get("sugars") or 0),
            "sat_fat":     float(m.get("sat_fat") or 0),
            "vitamin_c":   float(m.get("vitamin_c") or 0),
            "vitamin_b12": float(m.get("vitamin_b12") or 0),
            "sodium":      float(m.get("sodium") or 0),
            "calcium":     float(m.get("calcium") or 0),
            "iron":        float(m.get("iron") or 0),
            "potassium":   float(m.get("potassium") or 0),
            "magnesium":   float(m.get("magnesium") or 0),
            "phosphorus":  float(m.get("phosphorus") or 0),
        }
        slot = m.get("meal_slot", "snidane")
        meals.setdefault(slot, []).append(entry)

    activities = [
        {
            "activity_id":     a["id"],
            "name":            a["name"],
            "calories_burned": float(a.get("calories_burned") or 0),
        }
        for a in activity_rows
    ]

    water = [
        {"id": w["id"], "ml": int(w["amount_ml"])}
        for w in water_rows
    ]

    return {
        "id":         log_row["id"],
        "user_id":    log_row["user_id"],
        "date":       str(log_row["date"]),
        "meals":      meals,
        "activities": activities,
        "water":      water,
    }


# ── load_table ────────────────────────────────────────────────────────────────

def load_table(path: str) -> List[Dict]:
    if path == FOODS_FILE:
        return _fetch_all("SELECT * FROM foods")
    if path == USERS_FILE:
        return [_user_from_row(r) for r in _fetch_all("SELECT * FROM users")]
    if path == MESSAGES_FILE:
        return [_message_from_row(r) for r in
                _fetch_all("SELECT * FROM messages ORDER BY sent_at DESC")]
    if path == ADVISOR_CLIENTS_FILE:
        return _fetch_all("SELECT * FROM advisor_clients")
        # status: 'pending' | 'accepted'
    if path == WEIGHT_FILE:
        return _fetch_all("SELECT * FROM weight_entries")
    if path == LOGS_FILE:
        return _fetch_all("SELECT * FROM logs")
    return []


# ── find_one / find_all ───────────────────────────────────────────────────────

def find_one(path: str, predicate: Callable) -> Optional[Dict]:
    for rec in load_table(path):
        if predicate(rec):
            return rec
    return None


def find_all(path: str, predicate: Callable) -> List[Dict]:
    return [r for r in load_table(path) if predicate(r)]


# ── insert ────────────────────────────────────────────────────────────────────

def insert(path: str, record: Dict) -> Dict:
    if not record.get("id"):
        record = {**record, "id": str(uuid.uuid4())}

    if path == USERS_FILE:
        _execute(
            "INSERT INTO users (id, name, email, password_hash, role, is_premium) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (record["id"], record.get("name"), record["email"],
             record["password_hash"], record.get("role", "user"),
             bool(record.get("is_premium", False)))
        )

    elif path == MESSAGES_FILE:
        _execute(
            "INSERT INTO messages (id, advisor_id, advisor_email, client_id, text, sent_at, is_read, sender) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (record["id"], record["advisor_id"], record["advisor_email"],
             record["client_id"], record["text"],
             record.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M")),
             bool(record.get("read", False)),
             record.get("sender", "advisor"))
        )

    elif path == ADVISOR_CLIENTS_FILE:
        _execute(
            "INSERT INTO advisor_clients (advisor_id, client_id, status) VALUES (%s,%s,%s)",
            (record["advisor_id"], record["client_id"], record.get("status", "pending"))
        )

    elif path == WEIGHT_FILE:
        _execute(
            "INSERT INTO weight_entries (id, user_id, date, weight) VALUES (%s,%s,%s,%s)",
            (record["id"], record["user_id"], record["date"], record["weight"])
        )

    elif path == FOODS_FILE:
        _execute(
            "INSERT INTO foods (id, name, kcal, protein, carbs, fat, fiber, sugars, sat_fat, "
            "vitamin_c, vitamin_b12, sodium, calcium, iron, potassium, magnesium, phosphorus) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (record["id"], record["name"],
             record.get("kcal", 0), record.get("protein", 0),
             record.get("carbs", 0), record.get("fat", 0),
             record.get("fiber"), record.get("sugars"), record.get("sat_fat"),
             record.get("vitamin_c"), record.get("vitamin_b12"),
             record.get("sodium"), record.get("calcium"), record.get("iron"),
             record.get("potassium"), record.get("magnesium"), record.get("phosphorus"))
        )

    return record


# ── update_one ────────────────────────────────────────────────────────────────

def update_one(path: str, predicate: Callable, updater: Callable) -> bool:
    rec = find_one(path, predicate)
    if rec is None:
        return False
    updated = updater(dict(rec))

    if path == USERS_FILE:
        s = updated.get("settings") or {}
        _execute(
            "UPDATE users SET name=%s, email=%s, password_hash=%s, role=%s, is_premium=%s, "
            "age=%s, weight=%s, height=%s, gender=%s, activity=%s, goal=%s, "
            "kcal_target=%s, protein_target=%s, carbs_target=%s, fat_target=%s, "
            "water_goal_ml=%s, goal_weight=%s WHERE id=%s",
            (updated.get("name"), updated["email"], updated["password_hash"],
             updated["role"], bool(updated.get("is_premium", False)),
             s.get("age"), s.get("weight"), s.get("height"),
             s.get("gender"), s.get("activity", 1.55), s.get("goal", "maintain"),
             s.get("kcal_target", 2000), s.get("protein_target", 150),
             s.get("carbs_target", 250), s.get("fat_target", 70),
             s.get("water_goal_ml", 2500), s.get("goal_weight"),
             updated["id"])
        )

    elif path == WEIGHT_FILE:
        _execute(
            "UPDATE weight_entries SET weight=%s WHERE id=%s",
            (updated["weight"], updated["id"])
        )

    elif path == MESSAGES_FILE:
        _execute(
            "UPDATE messages SET is_read=%s WHERE id=%s",
            (bool(updated.get("read", False)), updated["id"])
        )

    return True


# ── delete_one ────────────────────────────────────────────────────────────────

def delete_one(path: str, predicate: Callable) -> bool:
    rec = find_one(path, predicate)
    if rec is None:
        return False

    if path == WEIGHT_FILE:
        _execute("DELETE FROM weight_entries WHERE id=%s", (rec["id"],))
    elif path == MESSAGES_FILE:
        _execute("DELETE FROM messages WHERE id=%s", (rec["id"],))
    elif path == ADVISOR_CLIENTS_FILE:
        _execute(
            "DELETE FROM advisor_clients WHERE advisor_id=%s AND client_id=%s",
            (rec["advisor_id"], rec["client_id"])
        )

    return True


# ── Log: načtení ─────────────────────────────────────────────────────────────

def _load_log_by_row(log_row: Dict) -> Dict:
    log_id = log_row["id"]
    meals  = _fetch_all("SELECT * FROM meal_entries WHERE log_id=%s", (log_id,))
    acts   = _fetch_all("SELECT * FROM activities WHERE log_id=%s", (log_id,))
    water  = _fetch_all("SELECT * FROM water_entries WHERE log_id=%s", (log_id,))
    return _log_from_rows(log_row, meals, acts, water)


def get_log(user_id: str, day: str) -> Optional[Dict]:
    row = _fetch_one("SELECT * FROM logs WHERE user_id=%s AND date=%s", (user_id, day))
    if row is None:
        return None
    return _load_log_by_row(row)


def get_or_create_log(user_id: str, day: str) -> Dict:
    log = get_log(user_id, day)
    if log is None:
        log_id = str(uuid.uuid4())
        _execute(
            "INSERT INTO logs (id, user_id, date) VALUES (%s,%s,%s)",
            (log_id, user_id, day)
        )
        log = {
            "id":         log_id,
            "user_id":    user_id,
            "date":       day,
            "meals":      {"snidane": [], "svacina": [], "obed": [], "svacina2": [], "vecere": []},
            "activities": [],
            "water":      [],
        }
    return log


def save_log(log: Dict) -> None:
    log_id = log["id"]
    cnx = _conn()
    cur = cnx.cursor()

    cur.execute("DELETE FROM meal_entries WHERE log_id=%s", (log_id,))
    cur.execute("DELETE FROM activities WHERE log_id=%s", (log_id,))
    cur.execute("DELETE FROM water_entries WHERE log_id=%s", (log_id,))

    meal_rows = []
    for slot, items in log.get("meals", {}).items():
        for item in items:
            meal_rows.append((
                item.get("entry_id") or str(uuid.uuid4()), log_id, slot,
                item.get("food_id", ""), item["name"], item["grams"],
                item["kcal"], item["protein"], item["carbs"], item["fat"],
                item.get("fiber", 0), item.get("sugars", 0), item.get("sat_fat", 0),
                item.get("vitamin_c", 0), item.get("vitamin_b12", 0),
                item.get("sodium", 0), item.get("calcium", 0), item.get("iron", 0),
                item.get("potassium", 0), item.get("magnesium", 0), item.get("phosphorus", 0),
            ))
    if meal_rows:
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO meal_entries "
            "(id, log_id, meal_slot, food_id, name, grams, kcal, protein, carbs, fat, "
            "fiber, sugars, sat_fat, vitamin_c, vitamin_b12, "
            "sodium, calcium, iron, potassium, magnesium, phosphorus) VALUES %s",
            meal_rows,
        )

    act_rows = [
        (act.get("activity_id") or str(uuid.uuid4()), log_id,
         act["name"], act["calories_burned"])
        for act in log.get("activities", [])
    ]
    if act_rows:
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO activities (id, log_id, name, calories_burned) VALUES %s",
            act_rows,
        )

    water_rows = [
        (w.get("id") or str(uuid.uuid4()), log_id, w["ml"])
        for w in log.get("water", [])
    ]
    if water_rows:
        psycopg2.extras.execute_values(
            cur,
            "INSERT INTO water_entries (id, log_id, amount_ml) VALUES %s",
            water_rows,
        )

    cnx.commit()
    cur.close()


# ── User settings ─────────────────────────────────────────────────────────────

def _default_settings() -> Dict:
    return {
        "age": 25, "weight": 75, "height": 175,
        "gender": "male", "activity": 1.55, "goal": "maintain",
        "kcal_target": 2000, "protein_target": 150,
        "carbs_target": 250, "fat_target": 70, "water_goal_ml": 2500,
    }


def get_user_settings(user_id: str) -> Dict:
    row = _fetch_one("SELECT * FROM users WHERE id=%s", (user_id,))
    if row is None:
        return _default_settings()
    user = _user_from_row(row)
    s = user.get("settings") or {}
    defaults = _default_settings()
    return {k: (s[k] if s.get(k) is not None else defaults[k]) for k in defaults}


def save_user_settings(user_id: str, settings: Dict) -> None:
    _execute(
        "UPDATE users SET age=%s, weight=%s, height=%s, gender=%s, activity=%s, goal=%s, "
        "kcal_target=%s, protein_target=%s, carbs_target=%s, fat_target=%s, "
        "water_goal_ml=%s, goal_weight=%s WHERE id=%s",
        (settings.get("age"), settings.get("weight"), settings.get("height"),
         settings.get("gender"), settings.get("activity", 1.55),
         settings.get("goal", "maintain"),
         settings.get("kcal_target", 2000), settings.get("protein_target", 150),
         settings.get("carbs_target", 250), settings.get("fat_target", 70),
         settings.get("water_goal_ml", 2500), settings.get("goal_weight"),
         user_id)
    )


# ── add_meal_entry_direct ─────────────────────────────────────────────────────

def add_meal_entry_direct(user_id: str, day: str, slot: str, entry: Dict) -> None:
    """Přidá jednu položku jídla přímo (2-3 dotazy místo 10+)."""
    log_row = _fetch_one("SELECT id FROM logs WHERE user_id=%s AND date=%s", (user_id, day))
    if log_row is None:
        log_id = str(uuid.uuid4())
        _execute("INSERT INTO logs (id, user_id, date) VALUES (%s,%s,%s)", (log_id, user_id, day))
    else:
        log_id = log_row["id"]

    _execute(
        "INSERT INTO meal_entries "
        "(id, log_id, meal_slot, food_id, name, grams, kcal, protein, carbs, fat, "
        "fiber, sugars, sat_fat, vitamin_c, vitamin_b12, "
        "sodium, calcium, iron, potassium, magnesium, phosphorus) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (entry.get("entry_id") or str(uuid.uuid4()), log_id, slot,
         entry.get("food_id", ""), entry["name"], entry["grams"],
         entry["kcal"], entry["protein"], entry["carbs"], entry["fat"],
         entry.get("fiber", 0), entry.get("sugars", 0), entry.get("sat_fat", 0),
         entry.get("vitamin_c", 0), entry.get("vitamin_b12", 0),
         entry.get("sodium", 0), entry.get("calcium", 0), entry.get("iron", 0),
         entry.get("potassium", 0), entry.get("magnesium", 0), entry.get("phosphorus", 0)),
    )


# ── advisor_clients helpers ───────────────────────────────────────────────────

def set_advisor_client_status(advisor_id: str, client_id: str, status: str) -> None:
    """Nastaví status pozvánky: 'pending' | 'accepted'."""
    _execute(
        "UPDATE advisor_clients SET status=%s WHERE advisor_id=%s AND client_id=%s",
        (status, advisor_id, client_id)
    )


def get_conversation_messages(advisor_id: str, client_id: str) -> List[Dict]:
    """Načte všechny zprávy konverzace – přímý SQL dotaz, bez UUID/string problémů."""
    rows = _fetch_all(
        "SELECT * FROM messages "
        "WHERE advisor_id::text = %s AND client_id::text = %s "
        "ORDER BY sent_at ASC",
        (str(advisor_id), str(client_id))
    )
    return [_message_from_row(r) for r in rows]


def get_pending_invitations(client_id: str) -> List[Dict]:
    """Vrátí seznam čekajících pozvánek (status='pending') pro daného klienta."""
    rows = _fetch_all(
        "SELECT ac.advisor_id, ac.client_id, ac.status, u.email AS advisor_email "
        "FROM advisor_clients ac "
        "JOIN users u ON u.id = ac.advisor_id "
        "WHERE ac.client_id = %s AND ac.status = 'pending'",
        (client_id,)
    )
    return rows


def get_my_advisors(client_id: str) -> List[Dict]:
    """Vrátí seznam přijatých poradců daného klienta."""
    rows = _fetch_all(
        "SELECT ac.advisor_id, ac.client_id, ac.status, u.email AS advisor_email "
        "FROM advisor_clients ac "
        "JOIN users u ON u.id = ac.advisor_id "
        "WHERE ac.client_id = %s AND ac.status = 'accepted'",
        (client_id,)
    )
    return rows


# ── recipes ───────────────────────────────────────────────────────────────────

def get_all_recipes_db() -> List[Dict]:
    """Načte všechny recepty z tabulky recipes."""
    rows = _fetch_all("SELECT * FROM recipes ORDER BY kcal ASC")
    for r in rows:
        r["tags"]        = r.get("tags") or []
        r["ingredients"] = r.get("ingredients") or []
    return rows


def get_healthy_recipes_db(n: int = 3) -> List[Dict]:
    """Vrátí n náhodně vybraných receptů z DB."""
    import random
    all_r = get_all_recipes_db()
    random.shuffle(all_r)
    return all_r[:n]


# ── init_db ───────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Inicializuje pool a ověří připojení."""
    try:
        pool = _get_pool()
        cnx = pool.getconn()
        cur = cnx.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        pool.putconn(cnx)
        print("[pg_db] Připojení k databázi OK (pool=5)")
    except Exception as e:
        print(f"[pg_db] CHYBA připojení: {e}")
        raise


# ── get_logs_range ────────────────────────────────────────────────────────────

def get_logs_range(user_id: str, days: List[str]) -> Dict[str, Dict]:
    """Načte logy pro více dní najednou (4 dotazy místo n*4)."""
    if not days:
        return {}

    placeholders = ",".join(["%s"] * len(days))
    log_rows = _fetch_all(
        f"SELECT * FROM logs WHERE user_id=%s AND date IN ({placeholders})",
        (user_id, *days),
    )
    if not log_rows:
        return {}

    log_ids = [r["id"] for r in log_rows]
    id_placeholders = ",".join(["%s"] * len(log_ids))

    meal_rows  = _fetch_all(f"SELECT * FROM meal_entries  WHERE log_id IN ({id_placeholders})", tuple(log_ids))
    act_rows   = _fetch_all(f"SELECT * FROM activities    WHERE log_id IN ({id_placeholders})", tuple(log_ids))
    water_rows = _fetch_all(f"SELECT * FROM water_entries WHERE log_id IN ({id_placeholders})", tuple(log_ids))

    meals_by_log:  Dict[str, list] = {lid: [] for lid in log_ids}
    acts_by_log:   Dict[str, list] = {lid: [] for lid in log_ids}
    water_by_log:  Dict[str, list] = {lid: [] for lid in log_ids}
    for m in meal_rows:  meals_by_log[m["log_id"]].append(m)
    for a in act_rows:   acts_by_log[a["log_id"]].append(a)
    for w in water_rows: water_by_log[w["log_id"]].append(w)

    result: Dict[str, Dict] = {}
    for log_row in log_rows:
        lid = log_row["id"]
        day = str(log_row["date"])
        result[day] = _log_from_rows(
            log_row, meals_by_log[lid], acts_by_log[lid], water_by_log[lid],
        )
    return result


# ── compute_day_totals (čistě Python, bez DB) ────────────────────────────────

def compute_day_totals(log: Dict) -> Dict:
    MICRO_KEYS = (
        "fiber", "sugars", "sat_fat", "vitamin_c", "vitamin_b12",
        "sodium", "calcium", "iron", "potassium", "magnesium", "phosphorus",
    )
    totals = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0,
              **{k: 0.0 for k in MICRO_KEYS}}
    for meal_items in log.get("meals", {}).values():
        for item in meal_items:
            ratio = item.get("grams", 0) / 100.0
            totals["kcal"]    += item.get("kcal", 0)    * ratio
            totals["protein"] += item.get("protein", 0) * ratio
            totals["carbs"]   += item.get("carbs", 0)   * ratio
            totals["fat"]     += item.get("fat", 0)     * ratio
            for k in MICRO_KEYS:
                totals[k] += item.get(k, 0) * ratio
    burned = sum(a.get("calories_burned", 0) for a in log.get("activities", []))
    totals["calories_burned"] = round(burned, 1)
    totals["balance"] = round(totals["kcal"] - burned, 1)
    return {k: round(v, 1) for k, v in totals.items()}
