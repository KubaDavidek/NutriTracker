# NutriTracker – Webová aplikace pro správu jídelníčku

Moderní Flask aplikace pro sledování denního příjmu jídla, kalorické bilance, váhy a aktivit. Backend využívá PostgreSQL databázi přes Supabase, frontend je postaven na Bootstrap 5 a Chart.js.

**Live demo:** https://nutritracker-iudn.onrender.com

---

## Funkce

- **Denní tracking jídel** – 5 jídel denně (snídaně, svačina, oběd, svačina2, večeře) s automatickým výpočtem maker (kcal, bílkoviny, sacharidy, tuky)
- **Sledování váhy** – záznamy váhy s grafem vývoje a možností nastavení cílové váhy
- **Sledování vody a aktivit** – denní příjem vody a spálené kalorie
- **Historie** – přehled za posledních 14 dní (nebo 365 dní pro premium)
- **Nutriční poradce** – poradce může sledovat logy klientů a komunikovat s nimi přes zprávy
- **Premium** – mikronutrienty (vitamíny, minerály), rozšířená historie, recepty
- **Databáze potravin** – vyhledávání s podporou diakritiky

---

## Technický stack

| Vrstva | Technologie |
|--------|-------------|
| Framework | Flask 3.0+ |
| Databáze | PostgreSQL (Supabase) |
| DB driver | psycopg2-binary |
| Frontend | Bootstrap 5.3.3, Chart.js 4.4.2 |
| Autentizace | Werkzeug (hashování hesel), Flask session |
| Šablony | Jinja2 |
| Produkční server | Gunicorn |
| Konfigurace | python-dotenv |

---

## Struktura projektu

```
nutritrack/
├── app.py                  # Vstupní bod aplikace, registrace blueprintů
├── requirements.txt
├── README.md
│
├── routes/                 # Blueprinty – jednotlivé části aplikace
│   ├── __init__.py
│   ├── auth.py             # /register  /login  /logout
│   ├── dashboard.py        # /dashboard  /add_meal  /history  /settings  ...
│   ├── advisor.py          # /advisor/  /advisor/client/<id>  ...
│   ├── weight.py           # /hmotnost  /hmotnost/pridat  ...
│   ├── premium.py          # /premium  /premium/activate
│   ├── recipes.py          # /recepty/
│   └── api.py              # /api/food_search  /api/history  /api/day_totals
│
├── utils/
│   ├── __init__.py
│   ├── json_db.py          # Abstrakce SQL dotazů (find_one, insert, update_one...)
│   ├── auth_utils.py       # Dekorátory: login_required, advisor_required...
│   └── nutrition_utils.py  # Odhad mikronutrientů
│
├── templates/              # Jinja2 HTML šablony
│   ├── base.html
│   ├── dashboard.html
│   ├── advisor.html
│   ├── advisor_client.html
│   ├── weight.html
│   ├── history.html
│   ├── messages.html
│   ├── premium.html
│   ├── recipes.html
│   ├── settings.html
│   ├── login.html
│   └── register.html
│
└── static/
    ├── css/style.css
    └── js/charts.js
```

---

## Databázové tabulky

| Tabulka | Popis |
|---------|-------|
| `users` | Uživatelské účty (profil, nastavení, premium status) |
| `logs` | Denní záznamy výživy |
| `meal_entries` | Jednotlivé potraviny v rámci jídla |
| `activities` | Pohybové aktivity a spálené kalorie |
| `water_entries` | Příjem vody |
| `foods` | Databáze potravin s nutričními hodnotami |
| `messages` | Zprávy mezi poradcem a klientem |
| `advisor_clients` | Vazba poradce → klient (pending / accepted) |
| `weight_entries` | Historie záznamu váhy |

---

## Instalace a spuštění

### 1. Klonování projektu
```bash
git clone <repo-url>
cd nutritrack
```

### 2. Vytvoření virtuálního prostředí

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

### 4. Nastavení prostředí

Vytvoř soubor `.env` v kořeni projektu:
```env
SECRET_KEY=tvoje-tajne-heslo
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

> Pro Supabase najdeš connection string v panelu projektu pod **Settings → Database → Connection string**.

### 5. Spuštění vývojového serveru
```bash
flask --app app run --debug
```

Aplikace poběží na **http://127.0.0.1:5000**.

---

## Role uživatelů

| Role | Přístup |
|------|---------|
| `user` | Osobní dashboard, tracking jídel, váhy, aktivit |
| `advisor` | Dashboard poradce – přehled klientů, jejich logy a komunikace |

### Premium funkce

Aktivace přes kód na stránce `/premium`. Platné kódy:

| Kód | |
|-----|-|
| `NUTRI2026` | ✓ |
| `PREMIUM` | ✓ |
| `FITLIFE2026` | ✓ |
| `SKOLA123` | ✓ |

Premium odemkne: mikronutrienty (vitamíny, minerály), historii za 365 dní a recepty.

---

## API endpointy

| Endpoint | Metoda | Popis |
|----------|--------|-------|
| `/api/food_search?q=` | GET | Vyhledávání v databázi potravin (podporuje diakritiku) |
| `/api/history?days=N` | GET | Historické součty pro Chart.js |
| `/api/day_totals?date=YYYY-MM-DD` | GET | Součty za konkrétní den |

---

## Produkční nasazení (Gunicorn)

```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

> Při více workerech zajišťuje konzistenci dat PostgreSQL – žádný file-lock není potřeba.

---

## Závislosti

```
Flask>=3.0.0
Werkzeug>=3.0.0
requests>=2.31.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
gunicorn>=20.1.0
```
