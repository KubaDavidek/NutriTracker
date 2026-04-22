"""Seed data pro zkouska@gmail.com: 7 dni jidla 2300-2700 kcal, aktivity 500-800 kcal, hmotnost za mesic."""
import os, uuid, random
from datetime import date, timedelta
import psycopg2, psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

cnx = psycopg2.connect(
    host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", 5432)),
    user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME"), sslmode="require",
)
cur  = cnx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
rcur = cnx.cursor()

USER_ID = "07e41702-fcb0-4689-a9db-b6027f05a520"
EMAIL   = "zkouska@gmail.com"
random.seed(99)

# ── Jídla ────────────────────────────────────────────────────────────────────
SNIDANE = [
    ("Ovesná kaše s banánem",         117, 4.0, 20.0, 2.0, 2.5, 8.0, 0.5, 4.0, 0.0, 30, 15, 1.0, 200, 30, 90),
    ("Celozrnný toast s vejcem",       198,11.0, 22.0, 7.0, 3.0, 3.0, 2.0, 0.0, 0.5,250, 60, 2.0, 180, 25,130),
    ("Jogurt s granolou",              140, 6.0, 20.0, 4.0, 1.5, 9.0, 1.5, 1.5, 0.3, 60,120, 0.5, 170, 20,110),
    ("Müsli s mlékem",                 130, 5.0, 22.0, 3.0, 3.0, 8.0, 0.8, 1.0, 0.2, 55,120, 1.5, 200, 35,120),
    ("Vejce s celozrnným chlebem",     185, 9.0, 18.0, 8.0, 2.5, 2.0, 2.2, 0.0, 0.4,200, 50, 1.8, 160, 20,140),
    ("Palačinky s tvarohem",           165, 9.0, 22.0, 5.0, 0.8, 7.0, 1.5, 4.0, 0.3,110,100, 0.8, 150, 15,120),
    ("Cottage cheese s jahodami",       95,11.0,  8.0, 2.0, 0.5, 5.0, 0.5,20.0, 0.1,300, 90, 0.2, 130, 10,100),
]
SVACINA = [
    ("Jablko",                          52, 0.3, 14.0, 0.2, 2.4,10.0, 0.0, 4.6, 0.0,  1,  6, 0.1, 107,  5, 11),
    ("Banán",                           89, 1.1, 23.0, 0.3, 2.6,12.0, 0.1, 8.7, 0.0,  1,  5, 0.3, 358, 27, 22),
    ("Řecký jogurt s medem",            97, 9.0,  6.0, 5.0, 0.0, 5.0, 1.5, 0.5, 0.2, 40,110, 0.0, 141, 11,108),
    ("Tvaroh s ovocem",                 85,12.0,  6.0, 1.0, 0.5, 4.0, 0.5, 5.0, 0.2, 60, 90, 0.2, 140, 12,100),
    ("Hruška",                          57, 0.4, 15.0, 0.1, 3.1, 9.5, 0.0, 4.3, 0.0,  1,  9, 0.2, 116,  7, 12),
    ("Smoothie (jahody, banán, mléko)", 65, 2.5, 12.0, 1.0, 1.5, 9.0, 0.5,25.0, 0.2, 30, 80, 0.4, 250, 15, 60),
    ("Proteinový jogurt",               97, 9.0,  6.0, 5.0, 0.0, 5.0, 1.5, 0.5, 0.2, 40,110, 0.0, 141, 11,108),
]
OBED = [
    ("Kuřecí prsa s rýží a zeleninou", 130,15.0, 14.0, 2.0, 0.8, 1.5, 0.5, 5.0, 0.2, 60, 20, 0.8, 220, 20,120),
    ("Těstoviny s boloňskou omáčkou",  137, 8.0, 16.0, 4.5, 1.2, 3.0, 1.5, 4.0, 0.3,180, 40, 1.5, 260, 25,110),
    ("Losos se sladkými bramborami",   128,12.0, 12.0, 4.0, 1.5, 4.0, 1.0, 8.0, 1.0, 80, 30, 1.0, 350, 28,180),
    ("Hovězí guláš s chlebem",         137,10.0, 12.0, 5.0, 1.0, 2.5, 1.8, 2.0, 1.5,210, 30, 2.5, 280, 22,140),
    ("Svíčková s knedlíkem",           150, 8.0, 17.0, 5.5, 0.6, 2.0, 2.0, 1.0, 0.8,230, 45, 1.8, 200, 18,110),
    ("Čočkový vývar s chlebem",         95, 7.0, 14.0, 1.0, 4.0, 2.0, 0.2, 2.0, 0.0,150, 40, 2.8, 320, 35,130),
    ("Kuřecí polévka s nudlemi",        68, 6.0,  8.0, 1.0, 0.5, 1.0, 0.3, 1.0, 0.1,350, 20, 0.5, 150, 10, 60),
]
SVACINA2 = [
    ("Celozrnný chléb s avokádem",     167, 4.0, 17.0, 9.0, 4.0, 1.5, 1.5, 6.0, 0.0,150, 15, 0.8, 300, 25, 70),
    ("Tvaroh",                          98,11.0,  3.5, 4.0, 0.0, 3.5, 2.5, 0.0, 0.5, 55, 95, 0.1, 130, 10,160),
    ("Mandarinky",                      53, 0.8, 13.0, 0.3, 1.8,10.0, 0.0,26.7, 0.0,  2, 37, 0.2, 166, 12, 20),
    ("Rýžové chlebíčky s arašíd. máslem",310,11.0,35.0,14.0,3.0, 6.0, 3.0, 0.0, 0.0,140, 25, 1.5, 350, 40,160),
    ("Sýr s celozrnným krekrem",       280,13.0, 24.0,14.0, 2.0, 1.0, 6.0, 0.0, 0.5,420,200, 0.5, 130, 15,200),
    ("Proteinový jogurt",               97, 9.0,  6.0, 5.0, 0.0, 5.0, 1.5, 0.5, 0.2, 40,110, 0.0, 141, 11,108),
    ("Jablko",                          52, 0.3, 14.0, 0.2, 2.4,10.0, 0.0, 4.6, 0.0,  1,  6, 0.1, 107,  5, 11),
]
VECERE = [
    ("Grilovaný losos se zeleninou",   127,17.0,  4.0, 5.0, 1.5, 2.0, 1.0, 8.0, 2.5, 70, 25, 0.8, 380, 30,210),
    ("Kuřecí salát s olivovým olejem", 107,14.0,  4.0, 4.0, 1.5, 2.5, 0.7,10.0, 0.2, 90, 30, 1.0, 260, 20,130),
    ("Krůtí steak se zeleninou",       117,15.0,  5.0, 3.0, 2.0, 3.0, 0.8,12.0, 0.3, 60, 25, 1.5, 300, 22,150),
    ("Tvarohový nákyp s ovocem",       130,11.0, 14.0, 3.0, 0.5, 8.0, 1.0, 5.0, 0.5, 80,100, 0.3, 180, 12,130),
    ("Pečená krůta s brokolicí",       120,16.0,  5.0, 3.0, 2.5, 2.5, 0.9,40.0, 0.3, 55, 40, 1.2, 320, 25,170),
    ("Vaječná omeleta se šunkou",      148,12.0,  2.0,10.0, 0.3, 1.0, 3.5, 0.5, 0.8,300, 80, 1.5, 140, 12,160),
    ("Rybí filet s bramborami",        115,12.0, 12.0, 3.0, 1.5, 1.0, 0.8, 7.0, 0.5,120, 20, 0.7, 350, 22,130),
]
AKTIVITY = [
    "Běh",
    "Kolo",
    "Plavání",
    "Posilovna",
    "HIIT trénink",
    "Eliptický trenažér",
    "Veslování (erg)",
]
SLOT_SHARE = {"snidane": 0.23, "svacina": 0.10, "obed": 0.35, "svacina2": 0.10, "vecere": 0.22}

def grams_for(food_kcal, target_kcal):
    if food_kcal <= 0: return 100
    return max(30, round((target_kcal / food_kcal * 100) / 10) * 10)

today = date.today()

# ── 1. Smaž stará data (7 dní) ───────────────────────────────────────────────
start7 = str(today - timedelta(days=6))
rcur.execute("SELECT id FROM logs WHERE user_id=%s AND date>=%s AND date<=%s", (USER_ID, start7, str(today)))
old_ids = [str(r[0]) for r in rcur.fetchall()]
if old_ids:
    ph = ",".join(["%s"]*len(old_ids))
    rcur.execute(f"DELETE FROM meal_entries  WHERE log_id IN ({ph})", old_ids)
    rcur.execute(f"DELETE FROM activities    WHERE log_id IN ({ph})", old_ids)
    rcur.execute(f"DELETE FROM water_entries WHERE log_id IN ({ph})", old_ids)
    rcur.execute("DELETE FROM logs WHERE user_id=%s AND date>=%s AND date<=%s", (USER_ID, start7, str(today)))
print(f"Smazáno {len(old_ids)} starých dní")

# ── 2. Vlož 7 dní jídla + aktivity ──────────────────────────────────────────
for day_off in range(7):
    d = today - timedelta(days=6 - day_off)
    d_str = str(d)
    target_kcal = random.randint(230, 270) * 10  # 2300–2700

    log_id = str(uuid.uuid4())
    rcur.execute("INSERT INTO logs (id, user_id, date) VALUES (%s,%s,%s)", (log_id, USER_ID, d_str))

    foods_by_slot = {
        "snidane":  SNIDANE[day_off % 7],
        "svacina":  SVACINA[day_off % 7],
        "obed":     OBED[day_off % 7],
        "svacina2": SVACINA2[day_off % 7],
        "vecere":   VECERE[day_off % 7],
    }

    meal_rows = []
    total_kcal = 0
    for slot, food in foods_by_slot.items():
        g = grams_for(food[1], target_kcal * SLOT_SHARE[slot])
        total_kcal += food[1] * g / 100
        name, kcal, protein, carbs, fat, fiber, sugars, sat_fat, vit_c, vit_b12, sodium, calcium, iron, potassium, magnesium, phosphorus = food
        meal_rows.append((
            str(uuid.uuid4()), log_id, slot, "", name, g,
            kcal, protein, carbs, fat,
            fiber, sugars, sat_fat, vit_c, vit_b12,
            sodium, calcium, iron, potassium, magnesium, phosphorus,
        ))
    psycopg2.extras.execute_values(
        rcur,
        "INSERT INTO meal_entries (id,log_id,meal_slot,food_id,name,grams,kcal,protein,carbs,fat,"
        "fiber,sugars,sat_fat,vitamin_c,vitamin_b12,sodium,calcium,iron,potassium,magnesium,phosphorus) VALUES %s",
        meal_rows,
    )

    # Voda
    water_ml = random.choice([2000, 2250, 2500])
    rcur.execute("INSERT INTO water_entries (id, log_id, amount_ml) VALUES (%s,%s,%s)",
                 (str(uuid.uuid4()), log_id, water_ml))

    # Aktivita 500–800 kcal
    burned = random.randint(10, 16) * 50  # 500, 550, 600, 650, 700, 750, 800
    act_name = AKTIVITY[day_off % len(AKTIVITY)]
    minutes = round(burned / 10)  # přibližné minuty (10 kcal/min)
    rcur.execute("INSERT INTO activities (id, log_id, name, calories_burned) VALUES (%s,%s,%s,%s)",
                 (str(uuid.uuid4()), log_id, f"{act_name} ({minutes} min)", burned))

    print(f"  {d_str}  ~{round(total_kcal)} kcal (cíl {target_kcal})  výdej={burned} kcal  voda={water_ml} ml")

# ── 3. Hmotnost za posledních 30 dní (cíl 75 kg) ────────────────────────────
# Smaz stare zaznamy hmotnosti
rcur.execute("DELETE FROM weight_entries WHERE user_id=%s", (USER_ID,))

# Začínáme na 82 kg, postupně klesáme k ~76.5 kg (snaha o 75 kg) – 1x týdně
start_weight = 82.0
end_weight   = 76.5
print()
for week in range(5):  # 0..4 => 4 týdny zpět + aktuální
    days_ago = (4 - week) * 7
    d = today - timedelta(days=days_ago)
    progress = week / 4
    weight = round(start_weight + (end_weight - start_weight) * progress + random.uniform(-0.2, 0.2), 1)
    rcur.execute(
        "INSERT INTO weight_entries (id, user_id, date, weight) VALUES (%s,%s,%s,%s)",
        (str(uuid.uuid4()), USER_ID, str(d), weight)
    )
    print(f"  Hmotnost {d}: {weight} kg")

cnx.commit()
rcur.close(); cur.close(); cnx.close()
print(f"\nHotovo! Data vložena pro {EMAIL}")
