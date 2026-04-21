"""
routes/api.py – Jednoduché JSON API endpointy (pro Chart.js a AJAX).
"""

import unicodedata
from datetime import date, timedelta
from flask import Blueprint, jsonify, request, session

from utils.json_db    import (FOODS_FILE, load_table, get_log, compute_day_totals)
from utils.auth_utils import login_required

api_bp = Blueprint("api", __name__, url_prefix="/api")

MICRO_KEYS = ("fiber", "sugars", "sat_fat", "vitamin_c", "vitamin_b12",
              "sodium", "calcium", "iron", "potassium", "magnesium", "phosphorus")


def _strip_accents(s: str) -> str:
    """Odstraní diakritiku – umožní hledat 'kure' a najít 'kuřecí'."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )





# ── GET /api/food_search?q=... ────────────────────────────────────────────────

@api_bp.route("/food_search")
@login_required
def food_search():
    """Vyhledá potraviny v lokální databázi. Vrátí max 8 výsledků."""
    q = request.args.get("q", "").strip()
    if not q or len(q) < 2:
        return jsonify([])

    words = _strip_accents(q.lower()).split()
    foods = load_table(FOODS_FILE)
    local = [f for f in foods
             if all(w in _strip_accents(f["name"].lower()) for w in words)][:15]

    results = []
    for f in local:
        entry = {
            "id":      f.get("id"),
            "name":    f["name"],
            "kcal":    f["kcal"],
            "protein": f["protein"],
            "carbs":   f["carbs"],
            "fat":     f["fat"],
            "source":  "local",
        }
        for k in MICRO_KEYS:
            entry[k] = f.get(k, 0)
        results.append(entry)

    return jsonify(results)


# ── GET /api/history?days=7 ───────────────────────────────────────────────────

@api_bp.route("/history")
@login_required
def history():
    """
    Vrátí denní součty za posledních N dní.
    Používá se pro Chart.js (grafická historie).
    """
    days_count = int(request.args.get("days", 7))
    user_id    = session["user_id"]
    today      = date.today()

    result = []
    for i in range(days_count - 1, -1, -1):
        d      = (today - timedelta(days=i)).isoformat()
        log    = get_log(user_id, d)
        totals = compute_day_totals(log) if log else {
            "kcal": 0, "protein": 0, "carbs": 0, "fat": 0,
            "calories_burned": 0, "balance": 0,
        }
        result.append({"date": d, "totals": totals})

    return jsonify(result)


# ── GET /api/day_totals?date=YYYY-MM-DD ───────────────────────────────────────

@api_bp.route("/day_totals")
@login_required
def day_totals():
    """Vrátí součty pro jeden den (pro aktualizaci grafu bez přenačtení stránky)."""
    day     = request.args.get("date", str(date.today()))
    user_id = session["user_id"]
    log     = get_log(user_id, day)
    totals  = compute_day_totals(log) if log else {
        "kcal": 0, "protein": 0, "carbs": 0, "fat": 0,
        "calories_burned": 0, "balance": 0,
    }
    return jsonify({"date": day, "totals": totals})
