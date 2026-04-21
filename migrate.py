"""
migrate.py – Přenese data z JSON souborů do MySQL databáze.
Spusť jednou: python migrate.py
"""

import json
import os
import uuid
from datetime import datetime

import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        autocommit=False,
    )


def load(name):
    path = os.path.join(DATA_DIR, name + ".json")
    if not os.path.exists(path):
        print(f"  [SKIP] {name}.json nenalezen")
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def migrate_users(cur):
    users = load("users")
    print(f"\n[users] Migruji {len(users)} uživatelů...")
    for u in users:
        s = u.get("settings") or {}
        try:
            cur.execute(
                "INSERT IGNORE INTO users "
                "(id, name, email, password_hash, role, is_premium, "
                "age, weight, height, gender, activity, goal, "
                "kcal_target, protein_target, carbs_target, fat_target, "
                "water_goal_ml, goal_weight) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    u["id"],
                    u.get("name"),
                    u["email"],
                    u["password_hash"],
                    u.get("role", "user"),
                    bool(u.get("is_premium", False)),
                    s.get("age"),
                    s.get("weight"),
                    s.get("height"),
                    s.get("gender"),
                    s.get("activity", 1.55),
                    s.get("goal", "maintain"),
                    s.get("kcal_target", 2000),
                    s.get("protein_target", 150),
                    s.get("carbs_target", 250),
                    s.get("fat_target", 70),
                    s.get("water_goal_ml", 2500),
                    s.get("goal_weight"),
                ),
            )
        except Exception as e:
            print(f"  [WARN] user {u.get('email')}: {e}")
    print(f"  Hotovo.")


def migrate_foods(cur):
    foods = load("foods")
    print(f"\n[foods] Migruji {len(foods)} potravin...")
    for f in foods:
        fid = str(f.get("id", "")) or str(uuid.uuid4())
        try:
            cur.execute(
                "INSERT IGNORE INTO foods "
                "(id, name, kcal, protein, carbs, fat, fiber, sugars, sat_fat, "
                "vitamin_c, vitamin_b12, sodium, calcium, iron, potassium, magnesium, phosphorus) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    fid,
                    f.get("name", ""),
                    f.get("kcal", 0),
                    f.get("protein", 0),
                    f.get("carbs", 0),
                    f.get("fat", 0),
                    f.get("fiber"),
                    f.get("sugars"),
                    f.get("sat_fat"),
                    f.get("vitamin_c"),
                    f.get("vitamin_b12"),
                    f.get("sodium"),
                    f.get("calcium"),
                    f.get("iron"),
                    f.get("potassium"),
                    f.get("magnesium"),
                    f.get("phosphorus"),
                ),
            )
        except Exception as e:
            print(f"  [WARN] food {f.get('name')}: {e}")
    print(f"  Hotovo.")


def migrate_advisor_clients(cur):
    rows = load("advisor_clients")
    print(f"\n[advisor_clients] Migruji {len(rows)} vazeb...")
    for r in rows:
        try:
            cur.execute(
                "INSERT IGNORE INTO advisor_clients (advisor_id, client_id) VALUES (%s,%s)",
                (r["advisor_id"], r["client_id"]),
            )
        except Exception as e:
            print(f"  [WARN] {e}")
    print("  Hotovo.")


def migrate_messages(cur):
    msgs = load("messages")
    print(f"\n[messages] Migruji {len(msgs)} zpráv...")
    for m in msgs:
        mid = m.get("id") or str(uuid.uuid4())
        sent = m.get("timestamp") or m.get("sent_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cur.execute(
                "INSERT IGNORE INTO messages "
                "(id, advisor_id, advisor_email, client_id, text, sent_at, is_read) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (
                    mid,
                    m["advisor_id"],
                    m.get("advisor_email", ""),
                    m["client_id"],
                    m.get("text", ""),
                    sent,
                    bool(m.get("read", False)),
                ),
            )
        except Exception as e:
            print(f"  [WARN] message {mid}: {e}")
    print("  Hotovo.")


def migrate_weight(cur):
    entries = load("weight")
    print(f"\n[weight] Migruji {len(entries)} záznamů...")
    for e in entries:
        eid = e.get("id") or str(uuid.uuid4())
        try:
            cur.execute(
                "INSERT IGNORE INTO weight_entries (id, user_id, date, weight) VALUES (%s,%s,%s,%s)",
                (eid, e["user_id"], e["date"], e["weight"]),
            )
        except Exception as e2:
            print(f"  [WARN] weight {eid}: {e2}")
    print("  Hotovo.")


def migrate_logs(cur):
    logs = load("logs")
    print(f"\n[logs] Migruji {len(logs)} denních záznamů...")
    VALID_SLOTS = {"snidane", "svacina", "obed", "svacina2", "vecere"}
    for log in logs:
        log_id = log.get("id") or str(uuid.uuid4())
        try:
            cur.execute(
                "INSERT IGNORE INTO logs (id, user_id, date) VALUES (%s,%s,%s)",
                (log_id, log["user_id"], log["date"]),
            )
        except Exception as e:
            print(f"  [WARN] log {log_id}: {e}")
            continue

        # meal entries
        for slot, items in log.get("meals", {}).items():
            if slot not in VALID_SLOTS:
                continue
            for item in items:
                entry_id = item.get("entry_id") or str(uuid.uuid4())
                try:
                    cur.execute(
                        "INSERT IGNORE INTO meal_entries "
                        "(id, log_id, meal_slot, food_id, name, grams, kcal, protein, carbs, fat, "
                        "fiber, sugars, sat_fat, vitamin_c, vitamin_b12, "
                        "sodium, calcium, iron, potassium, magnesium, phosphorus) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            entry_id, log_id, slot,
                            item.get("food_id", ""),
                            item.get("name", ""),
                            item.get("grams", 100),
                            item.get("kcal", 0),
                            item.get("protein", 0),
                            item.get("carbs", 0),
                            item.get("fat", 0),
                            item.get("fiber", 0),
                            item.get("sugars", 0),
                            item.get("sat_fat", 0),
                            item.get("vitamin_c", 0),
                            item.get("vitamin_b12", 0),
                            item.get("sodium", 0),
                            item.get("calcium", 0),
                            item.get("iron", 0),
                            item.get("potassium", 0),
                            item.get("magnesium", 0),
                            item.get("phosphorus", 0),
                        ),
                    )
                except Exception as e:
                    print(f"  [WARN] meal_entry {entry_id}: {e}")

        # activities
        for act in log.get("activities", []):
            aid = act.get("activity_id") or str(uuid.uuid4())
            try:
                cur.execute(
                    "INSERT IGNORE INTO activities (id, log_id, name, calories_burned) VALUES (%s,%s,%s,%s)",
                    (aid, log_id, act.get("name", ""), act.get("calories_burned", 0)),
                )
            except Exception as e:
                print(f"  [WARN] activity {aid}: {e}")

        # water
        for w in log.get("water", []):
            wid = w.get("id") or str(uuid.uuid4())
            try:
                cur.execute(
                    "INSERT IGNORE INTO water_entries (id, log_id, amount_ml) VALUES (%s,%s,%s)",
                    (wid, log_id, w.get("ml", 0)),
                )
            except Exception as e:
                print(f"  [WARN] water {wid}: {e}")

    print("  Hotovo.")


def main():
    print("=== NutriTracker migrace JSON → MySQL ===")
    cnx = conn()
    cur = cnx.cursor()

    migrate_users(cur)
    migrate_foods(cur)
    migrate_advisor_clients(cur)
    migrate_messages(cur)
    migrate_weight(cur)
    migrate_logs(cur)

    cnx.commit()
    cur.close()
    cnx.close()
    print("\n✓ Migrace dokončena!")


if __name__ == "__main__":
    main()
