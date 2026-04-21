"""
routes/api.py – Jednoduché JSON API endpointy (pro Chart.js a AJAX).
"""

import unicodedata
from datetime import date, timedelta
from flask import Blueprint, jsonify, request, session

from utils.json_db    import (FOODS_FILE, load_table, get_log, compute_day_totals, _fetch_all)
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
    Optimalizováno: 3 SQL dotazy místo 28.
    """
    days_count = int(request.args.get("days", 7))
    user_id    = session["user_id"]
    today      = date.today()
    start_date = (today - timedelta(days=days_count - 1)).isoformat()

    # 1 dotaz: všechny logy v rozsahu
    logs = _fetch_all(
        "SELECT id, date FROM logs WHERE user_id=%s AND date>=%s AND date<=%s",
        (user_id, start_date, today.isoformat())
    )
    log_map = {str(r["date"]): str(r["id"]) for r in logs}
    log_ids = list(log_map.values())

    # 2 dotazy: všechny meal_entries a aktivity najednou
    if log_ids:
        ph = ",".join(["%s"] * len(log_ids))
        meals = _fetch_all(
            f"SELECT log_id, kcal, protein, carbs, fat, grams FROM meal_entries WHERE log_id IN ({ph})",
            log_ids
        )
        acts = _fetch_all(
            f"SELECT log_id, calories_burned FROM activities WHERE log_id IN ({ph})",
            log_ids
        )
    else:
        meals, acts = [], []

    # Agregace per log_id
    from collections import defaultdict
    meal_totals = defaultdict(lambda: {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0})
    for m in meals:
        lid = str(m["log_id"])
        g = float(m.get("grams") or 100) / 100
        meal_totals[lid]["kcal"]    += float(m.get("kcal") or 0) * g
        meal_totals[lid]["protein"] += float(m.get("protein") or 0) * g
        meal_totals[lid]["carbs"]   += float(m.get("carbs") or 0) * g
        meal_totals[lid]["fat"]     += float(m.get("fat") or 0) * g

    act_totals = defaultdict(float)
    for a in acts:
        act_totals[str(a["log_id"])] += float(a.get("calories_burned") or 0)

    result = []
    for i in range(days_count - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        lid = log_map.get(d)
        if lid:
            t = meal_totals[lid]
            burned = act_totals[lid]
            totals = {
                "kcal":            round(t["kcal"]),
                "protein":         round(t["protein"], 1),
                "carbs":           round(t["carbs"], 1),
                "fat":             round(t["fat"], 1),
                "calories_burned": round(burned),
                "balance":         round(t["kcal"] - burned),
            }
        else:
            totals = {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0, "calories_burned": 0, "balance": 0}
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
