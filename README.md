# NutriTracker – Webová aplikace pro správu jídelníčku

Jednoduchá Flask aplikace pro sledování denního příjmu jídla, aktivit a kalorické
bilance. Data se ukládají do JSON souborů (žádná databáze).

---

## Struktura projektu

```
nutritracker/
├── app.py                     # Vstupní bod aplikace
├── requirements.txt
├── README.md
│
├── data/                      # JSON "databáze" (vytvoří se automaticky)
│   ├── foods.json             # Potraviny a živiny na 100 g
│   ├── users.json             # Uživatelé
│   ├── logs.json              # Denní záznamy jídel a aktivit
│   └── advisor_clients.json   # Vazby poradce → klient
│
├── utils/
│   ├── __init__.py
│   ├── json_db.py             # Load/save, CRUD, file-lock, seed data
│   └── auth_utils.py          # Hash hesla, login_required dekorátory
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                # /register  /login  /logout
│   ├── dashboard.py           # /dashboard  /add_meal  /remove_meal
│   │                          # /add_activity  /remove_activity  /history
│   ├── advisor.py             # /advisor  /advisor/client/<id>  /advisor/assign
│   └── api.py                 # /api/foods  /api/history  /api/day_totals
│
├── templates/
│   ├── base.html              # Sdílený layout (Navbar, Flash, Footer)
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html         # Denní přehled + grafy + jidla + aktivity
│   ├── history.html           # Tabulka + sloupcový graf 7 dní
│   ├── advisor.html           # Seznam klientů poradce
│   └── advisor_client.html    # Read-only pohled do dne klienta
│
└── static/
    ├── css/style.css
    └── js/charts.js           # Chart.js helper funkce
```

---

## Schémata JSON souborů

### `foods.json` – seznam potravin
```json
[
  {
    "id":      "f01",
    "name":    "Kuřecí prsa",
    "kcal":    165,
    "protein": 31.0,
    "carbs":   0.0,
    "fat":     3.6
  }
]
```
> Hodnoty `kcal`, `protein`, `carbs`, `fat` jsou **na 100 g** potraviny.

---

### `users.json` – uživatelé
```json
[
  {
    "id":            "uuid4",
    "email":         "user@example.com",
    "password_hash": "scrypt:...",
    "role":          "user",        // "user" | "advisor"
    "is_premium":    false
  }
]
```

---

### `logs.json` – denní záznamy
```json
[
  {
    "id":      "uuid4",
    "user_id": "uuid4",
    "date":    "2026-02-28",
    "meals": {
      "snidane":  [
        {
          "entry_id": "uuid4",
          "food_id":  "f01",
          "name":     "Kuřecí prsa",
          "grams":    150,
          "kcal":     165,
          "protein":  31.0,
          "carbs":    0.0,
          "fat":      3.6
        }
      ],
      "svacina":  [],
      "obed":     [],
      "svacina2": [],
      "vecere":   []
    },
    "activities": [
      {
        "activity_id":     "uuid4",
        "name":            "Běh",
        "calories_burned": 350
      }
    ]
  }
]
```
> Makra v položce jsou hodnoty **na 100 g**; skutečné hodnoty = `(hodnota * grams) / 100`.

---

### `advisor_clients.json` – vazba poradce → klient
```json
[
  {
    "id":         "uuid4",
    "advisor_id": "uuid4",
    "client_id":  "uuid4"
  }
]
```

---

## Postup spuštění

### 1. Klonování / rozbalení projektu
```bash
cd nutritracker
```

### 2. Vytvoření a aktivace virtuálního prostředí

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalace závislostí
```bash
pip install -r requirements.txt
```

### 4. Spuštění vývojového serveru
```bash
flask --app app run --debug
```

Aplikace poběží na **http://127.0.0.1:5000**.

Při prvním spuštění se automaticky vytvoří adresář `data/` a všechny JSON soubory
(seeds 12 potravin).

### 5. Volitelná konfigurace přes env proměnné
```bash
# Windows PowerShell
$env:SECRET_KEY = "moje-tajne-heslo-pro-session"
$env:FLASK_ENV  = "production"   # vypne debug mode

# Linux / macOS
export SECRET_KEY="moje-tajne-heslo-pro-session"
```

---

## Poznámky k bezpečnosti a souběžnému zápisu

`utils/json_db.py` používá **`threading.Lock()`** – chrání před souběžným zápisem
uvnitř jednoho procesu (standardní `flask run` s jedním workerem).

**⚠️ Pokud spustíš více procesů** (Gunicorn multi-worker, uWSGI), je nutné nahradit
`_LOCK` za meziprocesový file-lock:

```bash
pip install filelock
```

```python
# utils/json_db.py  –  nahraď threading.Lock() za:
from filelock import FileLock
_LOCK = FileLock(os.path.join(DATA_DIR, ".nutritracker.lock"))
```

Zápis do JSON souborů je **atomický** díky `os.replace(tmp, target)` –
přejmenování je atomické na stejném souborovém systému (POSIX i Windows NTFS).

---

## Jak přejít na MySQL (bodový přehled)

1. **Nainstalovat driver**: `pip install flask-sqlalchemy pymysql`
2. **Nastavit `SQLALCHEMY_DATABASE_URI`** v konfiguraci Flask.
3. **Převést JSON schémata na SQLAlchemy modely** (třídy `User`, `Food`, `Log`,
   `LogMealItem`, `LogActivity`, `AdvisorClient`).
4. **`meals` a `activities`** – v JSON jsou nested lists; v MySQL to budou
   samostatné tabulky `meal_items` a `activities` s FK na `logs.id`.
5. **Nahradit volání `json_db.*`** za SQLAlchemy session queries
   (`db.session.query(...)`, `db.session.add(...)`, `db.session.commit()`).
6. **`init_db()`** → `db.create_all()` + seed data přes `db.session.add_all(...)`.
7. **Odstranit file-lock** – MySQL transakce zajišťují konzistenci sama.
8. **Migrace schématu** – použít `flask-migrate` (`Alembic`) pro správu změn DB.
9. **Hesla** – žádná změna, `werkzeug.security` funguje stejně.
10. **Session** – uvážit přechod na `flask-session` s DB store pro škálování.
