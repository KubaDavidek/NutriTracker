"""
migrate_to_supabase.py – přesune data z Railway MySQL do Supabase PostgreSQL.
Spusť jednou: python migrate_to_supabase.py
"""
import os
import psycopg2
import psycopg2.extras
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# ── Supabase (cíl) ────────────────────────────────────────────────────────────
pg = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 6543)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME"),
    sslmode="require",
)
pg.autocommit = False
pgc = pg.cursor()

# ── Railway MySQL (zdroj) ─────────────────────────────────────────────────────
my = mysql.connector.connect(
    host="yamanote.proxy.rlwy.net",
    port=30492,
    user="root",
    password="VQRcgErPUSAOozzUZWGdEqYSDcWGSeTW",
    database="db_project",
)
myc = my.cursor(dictionary=True)


def migrate_table(name, select_sql, insert_sql, row_fn=None):
    myc.execute(select_sql)
    rows = myc.fetchall()
    if not rows:
        print(f"  {name}: 0 řádků, přeskakuji")
        return
    data = [row_fn(r) if row_fn else tuple(r.values()) for r in rows]
    psycopg2.extras.execute_values(pgc, insert_sql, data)
    pg.commit()
    print(f"  {name}: {len(data)} řádků OK")


print("Migrace dat Railway → Supabase...")

# users
migrate_table(
    "users",
    "SELECT id, name, email, password_hash, role, is_premium, age, weight, height, gender, "
    "activity, goal, kcal_target, protein_target, carbs_target, fat_target, water_goal_ml, goal_weight FROM users",
    "INSERT INTO users (id, name, email, password_hash, role, is_premium, age, weight, height, gender, "
    "activity, goal, kcal_target, protein_target, carbs_target, fat_target, water_goal_ml, goal_weight) "
    "VALUES %s ON CONFLICT (id) DO NOTHING",
    lambda r: (r["id"], r["name"], r["email"], r["password_hash"], r["role"], bool(r["is_premium"]),
               r["age"], r["weight"], r["height"], r["gender"], r["activity"], r["goal"],
               r["kcal_target"], r["protein_target"], r["carbs_target"], r["fat_target"],
               r["water_goal_ml"], r["goal_weight"]),
)

# logs
migrate_table(
    "logs",
    "SELECT id, user_id, date FROM logs",
    "INSERT INTO logs (id, user_id, date) VALUES %s ON CONFLICT (id) DO NOTHING",
    lambda r: (r["id"], r["user_id"], str(r["date"])),
)

# foods
migrate_table(
    "foods",
    "SELECT id, name, kcal, protein, carbs, fat, fiber, sugars, sat_fat, vitamin_c, vitamin_b12, "
    "sodium, calcium, iron, potassium, magnesium, phosphorus FROM foods",
    "INSERT INTO foods (id, name, kcal, protein, carbs, fat, fiber, sugars, sat_fat, vitamin_c, vitamin_b12, "
    "sodium, calcium, iron, potassium, magnesium, phosphorus) VALUES %s ON CONFLICT (id) DO NOTHING",
)

# meal_entries
migrate_table(
    "meal_entries",
    "SELECT id, log_id, meal_slot, food_id, name, grams, kcal, protein, carbs, fat, fiber, sugars, "
    "sat_fat, vitamin_c, vitamin_b12, sodium, calcium, iron, potassium, magnesium, phosphorus FROM meal_entries",
    "INSERT INTO meal_entries (id, log_id, meal_slot, food_id, name, grams, kcal, protein, carbs, fat, fiber, sugars, "
    "sat_fat, vitamin_c, vitamin_b12, sodium, calcium, iron, potassium, magnesium, phosphorus) "
    "VALUES %s ON CONFLICT (id) DO NOTHING",
)

# activities
migrate_table(
    "activities",
    "SELECT id, log_id, name, calories_burned FROM activities",
    "INSERT INTO activities (id, log_id, name, calories_burned) VALUES %s ON CONFLICT (id) DO NOTHING",
)

# water_entries
migrate_table(
    "water_entries",
    "SELECT id, log_id, amount_ml FROM water_entries",
    "INSERT INTO water_entries (id, log_id, amount_ml) VALUES %s ON CONFLICT (id) DO NOTHING",
)

# advisor_clients
migrate_table(
    "advisor_clients",
    "SELECT advisor_id, client_id FROM advisor_clients",
    "INSERT INTO advisor_clients (advisor_id, client_id) VALUES %s ON CONFLICT DO NOTHING",
)

# messages
migrate_table(
    "messages",
    "SELECT id, advisor_id, advisor_email, client_id, text, sent_at, is_read FROM messages",
    "INSERT INTO messages (id, advisor_id, advisor_email, client_id, text, sent_at, is_read) "
    "VALUES %s ON CONFLICT (id) DO NOTHING",
    lambda r: (r["id"], r["advisor_id"], r["advisor_email"], r["client_id"], r["text"],
               str(r["sent_at"]) if r["sent_at"] else None, bool(r["is_read"])),
)

# weight_entries
migrate_table(
    "weight_entries",
    "SELECT id, user_id, date, weight FROM weight_entries",
    "INSERT INTO weight_entries (id, user_id, date, weight) VALUES %s ON CONFLICT (id) DO NOTHING",
    lambda r: (r["id"], r["user_id"], str(r["date"]), r["weight"]),
)

pgc.close()
myc.close()
pg.close()
my.close()
print("\n✓ Migrace dokončena!")
