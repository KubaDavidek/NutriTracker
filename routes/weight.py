"""
routes/weight.py – Sledování hmotnosti.
"""

from datetime import date
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)

from utils.auth_utils import login_required, user_required
from utils.json_db import (WEIGHT_FILE, USERS_FILE,
                            find_all, insert, delete_one,
                            update_one, get_user_settings, save_user_settings,
                            _execute)

weight_bp = Blueprint("weight", __name__)


@weight_bp.route("/hmotnost")
@user_required
def index():
    uid = session["user_id"]

    # Všechny záznamy uživatele, seřazené od nejstaršího
    entries = sorted(
        find_all(WEIGHT_FILE, lambda e: e["user_id"] == uid),
        key=lambda e: e["date"]
    )

    settings = get_user_settings(uid)
    goal_weight = settings.get("goal_weight")

    # Data pro graf
    chart_labels = [e["date"] for e in entries]
    chart_data   = [e["weight"] for e in entries]

    # Poslední záznam
    last_entry = entries[-1] if entries else None

    # Změna oproti prvnímu záznamu
    diff = None
    if len(entries) >= 2:
        diff = round(entries[-1]["weight"] - entries[0]["weight"], 1)

    return render_template(
        "weight.html",
        entries=list(reversed(entries)),   # tabulka – nejnovější nahoře
        chart_labels=chart_labels,
        chart_data=chart_data,
        goal_weight=goal_weight,
        last_entry=last_entry,
        diff=diff,
        today=date.today().isoformat(),
    )


@weight_bp.route("/hmotnost/pridat", methods=["POST"])
@user_required
def add_entry():
    uid = session["user_id"]
    day = request.form.get("date", date.today().isoformat())
    try:
        weight_val = round(float(request.form.get("weight", 0)), 1)
    except (ValueError, TypeError):
        flash("Neplatná hodnota hmotnosti.", "danger")
        return redirect(url_for("weight.index"))

    if weight_val <= 0 or weight_val > 500:
        flash("Zadej hmotnost v rozsahu 1–500 kg.", "danger")
        return redirect(url_for("weight.index"))

    # Pokud pro daný den záznam existuje, aktualizuj ho
    existing = next(
        (e for e in find_all(WEIGHT_FILE, lambda e: e["user_id"] == uid)
         if e["date"] == day), None
    )
    if existing:
        update_one(WEIGHT_FILE,
                   lambda e: e["id"] == existing["id"],
                   lambda e: {**e, "weight": weight_val})
        flash(f"Hmotnost pro {day} aktualizována na {weight_val} kg.", "success")
    else:
        insert(WEIGHT_FILE, {
            "user_id": uid,
            "date":    day,
            "weight":  weight_val,
        })
        flash(f"Záznam {weight_val} kg přidán.", "success")

    return redirect(url_for("weight.index"))


@weight_bp.route("/hmotnost/smazat/<entry_id>", methods=["POST"])
@user_required
def delete_entry(entry_id):
    uid = session["user_id"]
    deleted = delete_one(WEIGHT_FILE,
                         lambda e: e["id"] == entry_id and e["user_id"] == uid)
    if deleted:
        flash("Záznam smazán.", "success")
    else:
        flash("Záznam nenalezen.", "danger")
    return redirect(url_for("weight.index"))


@weight_bp.route("/hmotnost/cil", methods=["POST"])
@user_required
def set_goal():
    uid = session["user_id"]
    try:
        goal = round(float(request.form.get("goal_weight", 0)), 1)
    except (ValueError, TypeError):
        flash("Neplatná hodnota cílové hmotnosti.", "danger")
        return redirect(url_for("weight.index"))

    if goal <= 0 or goal > 500:
        flash("Zadej cílovou hmotnost v rozsahu 1–500 kg.", "danger")
        return redirect(url_for("weight.index"))

    settings = get_user_settings(uid)
    settings["goal_weight"] = goal
    _execute("UPDATE users SET goal_weight=%s WHERE id=%s", (goal, uid))
    session.pop("settings_cache", None)
    flash(f"Cílová hmotnost nastavena na {goal} kg.", "success")
    return redirect(url_for("weight.index"))
