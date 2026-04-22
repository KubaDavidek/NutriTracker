"""
seed_user_data.py – Naplní 14 dní reálných jídel pro zadaný email.
Spuštění: python seed_user_data.py
"""

import os, uuid, random
from datetime import date, timedelta
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

# ── Připojení ─────────────────────────────────────────────────────────────────
cnx = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 5432)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME"),
    sslmode="require",
)
cur = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

TARGET_EMAIL = "jdnouzov@gmail.com"

# ── Najdi uživatele ───────────────────────────────────────────────────────────
cur.execute("SELECT id FROM users WHERE email = %s", (TARGET_EMAIL,))
row = cur.fetchone()
if not row:
    print(f"CHYBA: Uživatel {TARGET_EMAIL} nebyl nalezen v databázi!")
    exit(1)
user_id = str(row["id"])
print(f"Nalezen uživatel: {TARGET_EMAIL} (id={user_id})")

# ── Jídla (hodnoty na 100 g) ──────────────────────────────────────────────────
# Formát: (name, kcal, protein, carbs, fat, fiber, sugars, sat_fat, vitamin_c, vitamin_b12, sodium, calcium, iron, potassium, magnesium, phosphorus)

SNIDANE = [
    ("Ovesná kaše s banánem",          117, 4.0, 20.0,  2.0, 2.5, 8.0,  0.5, 4.0,  0.0, 30,  15,  1.0, 200, 30, 90),
    ("Celozrnný toast s vejcem",        198, 11.0, 22.0, 7.0, 3.0, 3.0,  2.0, 0.0,  0.5, 250, 60,  2.0, 180, 25, 130),
    ("Jogurt s granolou",               140,  6.0, 20.0, 4.0, 1.5, 9.0,  1.5, 1.5,  0.3, 60,  120, 0.5, 170, 20, 110),
    ("Cottage cheese s jahodami",        95, 11.0,  8.0, 2.0, 0.5, 5.0,  0.5, 20.0, 0.1, 300, 90,  0.2, 130, 10, 100),
    ("Müsli s mlékem",                  130,  5.0, 22.0, 3.0, 3.0, 8.0,  0.8, 1.0,  0.2, 55,  120, 1.5, 200, 35, 120),
    ("Vejce s celozrnným chlebem",      185,  9.0, 18.0, 8.0, 2.5, 2.0,  2.2, 0.0,  0.4, 200, 50,  1.8, 160, 20, 140),
    ("Palačinky s tvarohem a borůvkami",165,  9.0, 22.0, 5.0, 0.8, 7.0,  1.5, 4.0,  0.3, 110, 100, 0.8, 150, 15, 120),
]

SVACINA = [
    ("Jablko",                           52,  0.3, 14.0, 0.2, 2.4, 10.0, 0.0, 4.6,  0.0, 1,   6,   0.1, 107, 5,  11),
    ("Banán",                            89,  1.1, 23.0, 0.3, 2.6, 12.0, 0.1, 8.7,  0.0, 1,   5,   0.3, 358, 27, 22),
    ("Tvaroh s ovocem",                  85, 12.0,  6.0, 1.0, 0.5, 4.0,  0.5, 5.0,  0.2, 60,  90,  0.2, 140, 12, 100),
    ("Řecký jogurt s medem",             97,  9.0,  6.0, 5.0, 0.0, 5.0,  1.5, 0.5,  0.2, 40,  110, 0.0, 141, 11, 108),
    ("Ořechy (mix)",                    600, 15.0, 14.0,54.0, 6.0, 3.0, 10.0, 0.5,  0.0, 5,   90,  2.5, 470, 155, 380),
    ("Celozrnný chléb s máslem",         245,  6.0, 38.0, 8.0, 4.0, 2.0,  2.5, 0.0,  0.0, 320, 25,  1.8, 130, 30, 100),
    ("Hruška",                           57,  0.4, 15.0, 0.1, 3.1, 9.5,  0.0, 4.3,  0.0, 1,   9,   0.2, 116, 7,  12),
]

OBED = [
    ("Kuřecí prsa s rýží a zeleninou",  130, 15.0, 14.0, 2.0, 0.8, 1.5,  0.5, 5.0,  0.2, 60,  20,  0.8, 220, 20, 120),
    ("Těstoviny s boloňskou omáčkou",   137,  8.0, 16.0, 4.5, 1.2, 3.0,  1.5, 4.0,  0.3, 180, 40,  1.5, 260, 25, 110),
    ("Losos se sladkými bramborami",    128, 12.0, 12.0, 4.0, 1.5, 4.0,  1.0, 8.0,  1.0, 80,  30,  1.0, 350, 28, 180),
    ("Hovězí guláš s chlebem",          137, 10.0, 12.0, 5.0, 1.0, 2.5,  1.8, 2.0,  1.5, 210, 30,  2.5, 280, 22, 140),
    ("Svíčková s houskový knedlíkem",   150,  8.0, 17.0, 5.5, 0.6, 2.0,  2.0, 1.0,  0.8, 230, 45,  1.8, 200, 18, 110),
    ("Čočkový vývar s celozrnným chlebem", 95, 7.0, 14.0, 1.0, 4.0, 2.0, 0.2, 2.0,  0.0, 150, 40,  2.8, 320, 35, 130),
    ("Kuřecí polévka s nudlemi",         68,  6.0,  8.0, 1.0, 0.5, 1.0,  0.3, 1.0,  0.1, 350, 20,  0.5, 150, 10, 60),
]

SVACINA2 = [
    ("Proteinový jogurt",                97,  9.0,  6.0, 5.0, 0.0, 5.0,  1.5, 0.5,  0.2, 40,  110, 0.0, 141, 11, 108),
    ("Celozrnný chléb s avokádem",      167,  4.0, 17.0, 9.0, 4.0, 1.5,  1.5, 6.0,  0.0, 150, 15,  0.8, 300, 25, 70),
    ("Tvaroh",                           98, 11.0,  3.5, 4.0, 0.0, 3.5,  2.5, 0.0,  0.5, 55,  95,  0.1, 130, 10, 160),
    ("Mandarinky",                       53,  0.8, 13.0, 0.3, 1.8, 10.0, 0.0, 26.7, 0.0, 2,   37,  0.2, 166, 12, 20),
    ("Rýžové chlebíčky s arašídovým máslem", 310, 11.0, 35.0, 14.0, 3.0, 6.0, 3.0, 0.0, 0.0, 140, 25, 1.5, 350, 40, 160),
    ("Smoothie (jahody, banán, mléko)", 65,  2.5, 12.0, 1.0, 1.5, 9.0,  0.5, 25.0, 0.2, 30,  80,  0.4, 250, 15, 60),
    ("Sýr s celozrnným krekrem",        280, 13.0, 24.0,14.0, 2.0, 1.0,  6.0, 0.0,  0.5, 420, 200, 0.5, 130, 15, 200),
]

VECERE = [
    ("Grilovaný losos se zeleninou",    127, 17.0,  4.0, 5.0, 1.5, 2.0,  1.0, 8.0,  2.5, 70,  25,  0.8, 380, 30, 210),
    ("Kuřecí salát s olivovým olejem",  107, 14.0,  4.0, 4.0, 1.5, 2.5,  0.7, 10.0, 0.2, 90,  30,  1.0, 260, 20, 130),
    ("Krůtí steak se zeleninovým mixem",117, 15.0,  5.0, 3.0, 2.0, 3.0,  0.8, 12.0, 0.3, 60,  25,  1.5, 300, 22, 150),
    ("Tvarohový nákyp s ovocem",        130, 11.0, 14.0, 3.0, 0.5, 8.0,  1.0, 5.0,  0.5, 80,  100, 0.3, 180, 12, 130),
    ("Pečená krůta s brokolicí",        120, 16.0,  5.0, 3.0, 2.5, 2.5,  0.9, 40.0, 0.3, 55,  40,  1.2, 320, 25, 170),
    ("Vaječná omeleta se šunkou a sýrem",148, 12.0,  2.0,10.0, 0.3, 1.0,  3.5, 0.5,  0.8, 300, 80,  1.5, 140, 12, 160),
    ("Rybí filet s vařenými bramborami",115, 12.0, 12.0, 3.0, 1.5, 1.0,  0.8, 7.0,  0.5, 120, 20,  0.7, 350, 22, 130),
]

# Kcal spálené plavání: cca 7 kcal/min
PLAVANI_KCAL_PER_MIN = 7

# Cílové kcal na den – náhodně 2300–2800 (nastaví se per-day)
TARGET_KCAL = 2600  # fallback
SLOT_SHARE = {
    "snidane":  0.23,   # ~600 kcal
    "svacina":  0.10,   # ~260 kcal
    "obed":     0.35,   # ~910 kcal
    "svacina2": 0.10,   # ~260 kcal
    "vecere":   0.22,   # ~570 kcal
}

def grams_for_target(food_kcal_per_100g: float, target_kcal: float) -> int:
    """Vrátí gramy potřebné k dosažení target_kcal, zaokrouhleno na 10 g."""
    if food_kcal_per_100g <= 0:
        return 100
    raw = (target_kcal / food_kcal_per_100g) * 100
    return max(30, round(raw / 10) * 10)

# ── Hlavní loop: 14 dní ───────────────────────────────────────────────────────
today = date.today()
regular_cur = cnx.cursor()

# Smaž existující logy pro toto období (nejdřív child tabulky, pak logs)
start_date = str(today - timedelta(days=6))
end_date   = str(today)
regular_cur.execute(
    "SELECT id FROM logs WHERE user_id = %s AND date >= %s AND date <= %s",
    (user_id, start_date, end_date)
)
old_log_ids = [str(r[0]) for r in regular_cur.fetchall()]
if old_log_ids:
    placeholders = ",".join(["%s"] * len(old_log_ids))
    regular_cur.execute(f"DELETE FROM meal_entries  WHERE log_id IN ({placeholders})", old_log_ids)
    regular_cur.execute(f"DELETE FROM activities    WHERE log_id IN ({placeholders})", old_log_ids)
    regular_cur.execute(f"DELETE FROM water_entries WHERE log_id IN ({placeholders})", old_log_ids)
    regular_cur.execute(
        "DELETE FROM logs WHERE user_id = %s AND date >= %s AND date <= %s",
        (user_id, start_date, end_date)
    )
print(f"  Smazány staré záznamy ({len(old_log_ids)} dní) od {start_date} do {end_date}")

inserted_days = 0
random.seed(42)

for day_offset in range(7):
    day_date = today - timedelta(days=6 - day_offset)
    day_str = str(day_date)
    d = day_offset

    # Vytvoř log
    log_id = str(uuid.uuid4())
    regular_cur.execute(
        "INSERT INTO logs (id, user_id, date) VALUES (%s, %s, %s)",
        (log_id, user_id, day_str)
    )

    # Náhodný cíl kcal pro tento den (2300–2800)
    TARGET_KCAL = random.randint(230, 280) * 10

    # Přidej jídla – gramy vypočítány dynamicky podle TARGET_KCAL
    foods_by_slot = {
        "snidane":  SNIDANE[d % len(SNIDANE)],
        "svacina":  SVACINA[d % len(SVACINA)],
        "obed":     OBED[d % len(OBED)],
        "svacina2": SVACINA2[d % len(SVACINA2)],
        "vecere":   VECERE[d % len(VECERE)],
    }

    meals_to_insert = []
    for slot, food in foods_by_slot.items():
        target = TARGET_KCAL * SLOT_SHARE[slot]
        grams  = grams_for_target(food[1], target)
        meals_to_insert.append((slot, food, grams))

    meal_rows = []
    for slot, food, grams in meals_to_insert:
        name, kcal, protein, carbs, fat, fiber, sugars, sat_fat, vit_c, vit_b12, sodium, calcium, iron, potassium, magnesium, phosphorus = food
        meal_rows.append((
            str(uuid.uuid4()), log_id, slot, "", name, grams,
            kcal, protein, carbs, fat,
            fiber, sugars, sat_fat, vit_c, vit_b12,
            sodium, calcium, iron, potassium, magnesium, phosphorus,
        ))

    psycopg2.extras.execute_values(
        regular_cur,
        "INSERT INTO meal_entries "
        "(id, log_id, meal_slot, food_id, name, grams, kcal, protein, carbs, fat, "
        "fiber, sugars, sat_fat, vitamin_c, vitamin_b12, "
        "sodium, calcium, iron, potassium, magnesium, phosphorus) VALUES %s",
        meal_rows,
    )

    # Přidej vodu (cca 2000-2500 ml)
    water_ml = 2000 + (d % 3) * 250
    regular_cur.execute(
        "INSERT INTO water_entries (id, log_id, amount_ml) VALUES (%s, %s, %s)",
        (str(uuid.uuid4()), log_id, water_ml)
    )

    # Plavání každý den – délka 20–80 minut (různá každý den)
    swim_minutes = random.randint(2, 8) * 10  # 20, 30, 40, 50, 60, 70 nebo 80
    swim_kcal = swim_minutes * PLAVANI_KCAL_PER_MIN
    swim_name = f"Plavání ({swim_minutes} min)"
    regular_cur.execute(
        "INSERT INTO activities (id, log_id, name, calories_burned) VALUES (%s, %s, %s, %s)",
        (str(uuid.uuid4()), log_id, swim_name, swim_kcal)
    )

    # Výpočet denního příjmu pro výpis
    total_kcal = sum(
        food[1] * grams / 100
        for _, food, grams in meals_to_insert
    )
    print(f"  ✓ {day_str}  ~{round(total_kcal)} kcal (cíl {TARGET_KCAL})  plavání={swim_minutes} min  voda={water_ml} ml")
    inserted_days += 1

cnx.commit()
regular_cur.close()
cur.close()
cnx.close()

print(f"\nHotovo! Vloženo {inserted_days} dní záznamů pro {TARGET_EMAIL}.")
