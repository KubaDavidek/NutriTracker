"""
routes/dashboard.py – Uživatelský dashboard: přehled dne, přidání/odebrání jídla,
                       přidání aktivity, přehled historie.
"""

import uuid
from datetime import date, timedelta, datetime
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session, jsonify)

from utils.json_db       import (FOODS_FILE, LOGS_FILE, MESSAGES_FILE,
                                  USERS_FILE, ADVISOR_CLIENTS_FILE,
                                  load_table, get_or_create_log,
                                  save_log, compute_day_totals, find_all,
                                  update_one, find_one, insert, get_user_settings,
                                  save_user_settings, add_meal_entry_direct,
                                  _fetch_one, set_advisor_client_status,
                                  get_pending_invitations, get_my_advisors,
                                  delete_one, get_conversation_messages)
from utils.auth_utils    import login_required, user_required

dashboard_bp = Blueprint("dashboard", __name__)

MEAL_SLOTS = [
    ("snidane",  "Snídáně",             "primary"),
    ("svacina",  "Dopolední svačina",   "primary"),
    ("obed",     "Oběd",               "primary"),
    ("svacina2", "Odpoledni svačina",   "primary"),
    ("vecere",   "Večeře",             "primary"),
]


# ── /dashboard ────────────────────────────────────────────────────────────────

@dashboard_bp.route("/dashboard")
@user_required
def index():
    today     = date.today()
    is_premium = session.get("is_premium", False)
    days_back  = 365 if is_premium else 14
    min_date   = today - timedelta(days=days_back)
    min_iso    = str(min_date)
    today_iso  = str(today)

    day = request.args.get("date", today_iso)
    # Enforce limit server-side
    if day < min_iso:
        day = min_iso
    if day > today_iso:
        day = today_iso

    user_id = session["user_id"]
    log    = get_or_create_log(user_id, day)
    totals = compute_day_totals(log)

    # Mikroživiny jsou součástí totals (reálná data z USDA)
    micros = totals if is_premium else {}

    # Nepřečtené zprávy od poradce
    row = _fetch_one(
        "SELECT COUNT(*) AS cnt FROM messages WHERE client_id=%s AND sender='advisor' AND (is_read=FALSE OR is_read IS NULL)",
        (user_id,)
    )
    unread_count = row["cnt"] if row else 0

    # Cíle uživatele z nastavení (cachujeme v session)
    if "settings_cache" not in session:
        session["settings_cache"] = get_user_settings(user_id)
    settings = session["settings_cache"]
    targets = {
        "kcal":    settings.get("kcal_target",    2000),
        "protein": settings.get("protein_target", 150),
        "carbs":   settings.get("carbs_target",   250),
        "fat":     settings.get("fat_target",     70),
    }

    # Voda
    water_entries = log.get("water", [])
    water_total   = sum(w["ml"] for w in water_entries)
    water_goal    = settings.get("water_goal_ml", 2500)

    # Čekající pozvánky od poradců
    pending_invitations = get_pending_invitations(user_id)

    return render_template(
        "dashboard.html",
        day=day,
        today_iso=today_iso,
        min_iso=min_iso,
        is_premium=is_premium,
        log=log,
        totals=totals,
        meal_slots=MEAL_SLOTS,
        micros=micros,
        unread_count=unread_count,
        targets=targets,
        water_entries=water_entries,
        water_total=water_total,
        water_goal=water_goal,
        pending_invitations=pending_invitations,
    )


# ── /add_meal ─────────────────────────────────────────────────────────────────

@dashboard_bp.route("/add_meal", methods=["POST"])
@user_required
def add_meal():
    day      = request.form.get("date", str(date.today()))
    slot     = request.form.get("meal_slot", "snidane")
    food_id  = request.form.get("food_id", "")
    grams_s  = request.form.get("grams", "0")

    try:
        grams = float(grams_s)
        if grams <= 0:
            raise ValueError
    except ValueError:
        flash("Zadej platné množství v gramech (> 0).", "danger")
        return redirect(url_for("dashboard.index", date=day))

    # Ověr platný meal slot
    valid_slots = [s for s, *_ in MEAL_SLOTS]
    if slot not in valid_slots:
        flash("Neplatný slot jídla.", "danger")
        return redirect(url_for("dashboard.index", date=day))

    # Přijmi nutriční data z formuláře
    MICRO_KEYS = ("fiber", "sugars", "sat_fat", "vitamin_c", "vitamin_b12",
                  "sodium", "calcium", "iron", "potassium", "magnesium", "phosphorus")
    food = None
    if not food:
        food_name    = request.form.get("food_name", "").strip()
        food_kcal_s  = request.form.get("food_kcal",    "0")
        food_prot_s  = request.form.get("food_protein", "0")
        food_carbs_s = request.form.get("food_carbs",   "0")
        food_fat_s   = request.form.get("food_fat",     "0")
        if not food_name:
            flash("Potravina nenalezena.", "danger")
            return redirect(url_for("dashboard.index", date=day))
        try:
            food = {
                "id":      "",
                "name":    food_name,
                "kcal":    float(food_kcal_s),
                "protein": float(food_prot_s),
                "carbs":   float(food_carbs_s),
                "fat":     float(food_fat_s),
            }
            for k in MICRO_KEYS:
                food[k] = float(request.form.get(f"food_{k}", "0") or "0")
        except ValueError:
            flash("Neplatná nutriční data.", "danger")
            return redirect(url_for("dashboard.index", date=day))

    entry = {
        "entry_id": str(uuid.uuid4()),
        "food_id":  food.get("id", ""),
        "name":     food["name"],
        "grams":    grams,
        "kcal":     food["kcal"],
        "protein":  food["protein"],
        "carbs":    food["carbs"],
        "fat":      food["fat"],
        **{k: food.get(k, 0) for k in MICRO_KEYS},
    }
    add_meal_entry_direct(session["user_id"], day, slot, entry)

    slot_label = {s: l for s, l, *_ in MEAL_SLOTS}.get(slot, slot)
    flash(f"Přidáno: {food['name']} ({grams} g) do {slot_label}.", "success")
    return redirect(url_for("dashboard.index", date=day))


# ── /edit_meal ────────────────────────────────────────────────────────────────

@dashboard_bp.route("/edit_meal", methods=["POST"])
@user_required
def edit_meal():
    day      = request.form.get("date", str(date.today()))
    slot     = request.form.get("meal_slot", "")
    entry_id = request.form.get("entry_id", "")
    grams_s  = request.form.get("grams", "0")

    try:
        grams = float(grams_s)
        if grams <= 0:
            raise ValueError
    except ValueError:
        flash("Zadej platné množství v gramech (> 0).", "danger")
        return redirect(url_for("dashboard.index", date=day))

    log = get_or_create_log(session["user_id"], day)
    slot_items = log["meals"].get(slot, [])
    found = False
    for item in slot_items:
        if item.get("entry_id") == entry_id:
            item["grams"] = grams
            found = True
            break

    if found:
        save_log(log)
        flash("Množství upraveno.", "success")
    else:
        flash("Položka nenalezena.", "warning")

    return redirect(url_for("dashboard.index", date=day))


# ── /remove_meal ──────────────────────────────────────────────────────────────

@dashboard_bp.route("/remove_meal", methods=["POST"])
@user_required
def remove_meal():
    day      = request.form.get("date", str(date.today()))
    slot     = request.form.get("meal_slot", "")
    entry_id = request.form.get("entry_id", "")

    log = get_or_create_log(session["user_id"], day)

    slot_items = log["meals"].get(slot, [])
    new_items  = [i for i in slot_items if i.get("entry_id") != entry_id]

    if len(new_items) == len(slot_items):
        flash("Záznam nenalezen.", "warning")
    else:
        log["meals"][slot] = new_items
        save_log(log)
        flash("Položka odebrána.", "success")

    return redirect(url_for("dashboard.index", date=day))


# ── /add_activity ─────────────────────────────────────────────────────────────

@dashboard_bp.route("/add_activity", methods=["POST"])
@user_required
def add_activity():
    day            = request.form.get("date", str(date.today()))
    activity_name  = request.form.get("activity_name", "").strip()
    calories_str   = request.form.get("calories_burned", "0")

    try:
        calories = float(calories_str)
        if calories < 0:
            raise ValueError
    except ValueError:
        flash("Zadej platný počet spálených kalorií (≥ 0).", "danger")
        return redirect(url_for("dashboard.index", date=day))

    if not activity_name:
        flash("Zadej název aktivity.", "danger")
        return redirect(url_for("dashboard.index", date=day))

    log = get_or_create_log(session["user_id"], day)
    log.setdefault("activities", []).append({
        "activity_id":     str(uuid.uuid4()),
        "name":            activity_name,
        "calories_burned": calories,
    })
    save_log(log)

    flash(f"Aktivita '{activity_name}' přidána ({calories} kcal).", "success")
    return redirect(url_for("dashboard.index", date=day))


# ── /remove_activity ──────────────────────────────────────────────────────────

@dashboard_bp.route("/remove_activity", methods=["POST"])
@user_required
def remove_activity():
    day         = request.form.get("date", str(date.today()))
    activity_id = request.form.get("activity_id", "")

    log = get_or_create_log(session["user_id"], day)
    old_len = len(log.get("activities", []))
    log["activities"] = [a for a in log.get("activities", [])
                         if a.get("activity_id") != activity_id]

    if len(log["activities"]) < old_len:
        save_log(log)
        flash("Aktivita odebrána.", "success")
    else:
        flash("Aktivita nenalezena.", "warning")

    return redirect(url_for("dashboard.index", date=day))


# ── /add_water ───────────────────────────────────────────────────────────────

@dashboard_bp.route("/add_water", methods=["POST"])
@user_required
def add_water():
    day = request.form.get("date", str(date.today()))
    try:
        ml = int(request.form.get("ml", 0))
        if ml <= 0:
            raise ValueError
    except ValueError:
        flash("Zadej platné množství (ml > 0).", "danger")
        return redirect(url_for("dashboard.index", date=day))
    log = get_or_create_log(session["user_id"], day)
    log.setdefault("water", []).append({"id": str(uuid.uuid4()), "ml": ml})
    save_log(log)
    flash(f"Přidáno {ml} ml vody.", "success")
    return redirect(url_for("dashboard.index", date=day))


@dashboard_bp.route("/remove_water", methods=["POST"])
@user_required
def remove_water():
    day = request.form.get("date", str(date.today()))
    wid = request.form.get("water_id", "")
    log = get_or_create_log(session["user_id"], day)
    before = len(log.get("water", []))
    log["water"] = [w for w in log.get("water", []) if w["id"] != wid]
    if len(log["water"]) < before:
        save_log(log)
    return redirect(url_for("dashboard.index", date=day))


# ── /history ──────────────────────────────────────────────────────────────────

@dashboard_bp.route("/history")
@user_required
def history():
    user_id = session["user_id"]
    today   = date.today()
    days    = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    from utils.json_db import get_logs_range
    logs_map = get_logs_range(user_id, days)

    history_data = []
    empty = {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0, "calories_burned": 0, "balance": 0}
    for d in days:
        log    = logs_map.get(d)
        totals = compute_day_totals(log) if log else empty
        history_data.append({"date": d, "totals": totals})

    return render_template("history.html", history_data=history_data)


# ── /nastaveni ───────────────────────────────────────────────────────────────

@dashboard_bp.route("/nastaveni", methods=["GET", "POST"])
@user_required
def settings():
    user_id  = session["user_id"]
    current  = get_user_settings(user_id)
    errors   = []

    if request.method == "POST":
        mode = request.form.get("mode", "manual")

        if mode == "water":
            try:
                water_goal_ml = int(request.form["water_goal_ml"])
                if water_goal_ml < 100:
                    raise ValueError
                new_settings = {**current, "water_goal_ml": water_goal_ml}
                save_user_settings(user_id, new_settings)
                session.pop("settings_cache", None)
                flash(f"Denní cíl příjmu vody nastaven na {water_goal_ml} ml.", "success")
            except (KeyError, ValueError):
                errors.append("Zadej platný cíl vody (min. 100 ml).")
            return redirect(url_for("dashboard.settings"))

        elif mode == "auto":
            try:
                age      = int(request.form["age"])
                weight   = float(request.form["weight"])
                height   = float(request.form["height"])
                gender   = request.form["gender"]
                activity = float(request.form["activity"])
                goal     = request.form["goal"]

                # BMR – Mifflin-St Jeor
                if gender == "male":
                    bmr = 10 * weight + 6.25 * height - 5 * age + 5
                else:
                    bmr = 10 * weight + 6.25 * height - 5 * age - 161

                tdee = bmr * activity

                # Úprava dle cíle
                goal_mult   = {"maintain": 1.0, "lose": 0.80, "gain": 1.15}
                kcal_target = round(tdee * goal_mult.get(goal, 1.0))

                # Makra (% z kalorií)
                splits = {
                    "maintain": (0.25, 0.50, 0.25),
                    "lose":     (0.35, 0.40, 0.25),
                    "gain":     (0.30, 0.45, 0.25),
                }
                p_pct, c_pct, f_pct = splits.get(goal, (0.25, 0.50, 0.25))
                protein_target = round(kcal_target * p_pct / 4)
                carbs_target   = round(kcal_target * c_pct / 4)
                fat_target     = round(kcal_target * f_pct / 9)

                new_settings = {
                    "age": age, "weight": weight, "height": height,
                    "gender": gender, "activity": activity, "goal": goal,
                    "kcal_target":    kcal_target,
                    "protein_target": protein_target,
                    "carbs_target":   carbs_target,
                    "fat_target":     fat_target,
                }
                save_user_settings(user_id, new_settings)
                session.pop("settings_cache", None)
                flash(f"Cíle vypočítány a uloženy: {kcal_target} kcal "
                      f"| B {protein_target} g | S {carbs_target} g | T {fat_target} g", "success")
                return redirect(url_for("dashboard.settings"))

            except (KeyError, ValueError) as e:
                errors.append(f"Chyba ve formuláři: {e}")

        else:  # manual

            try:
                protein_g = int(request.form["protein_g"])
                carbs_g   = int(request.form["carbs_g"])
                fat_g     = int(request.form["fat_g"])

                if protein_g < 0 or carbs_g < 0 or fat_g < 0:
                    raise ValueError("Hodnoty musí být kladné.")

                # Kalorie se VŽDY počítají z maker
                kcal_target = protein_g * 4 + carbs_g * 4 + fat_g * 9

                new_settings = {
                    **current,
                    "kcal_target":    kcal_target,
                    "protein_target": protein_g,
                    "carbs_target":   carbs_g,
                    "fat_target":     fat_g,
                }
                save_user_settings(user_id, new_settings)
                session.pop("settings_cache", None)
                flash(f"Cíle uloženy: {kcal_target} kcal "
                      f"| B {protein_g} g | S {carbs_g} g | T {fat_g} g", "success")
                return redirect(url_for("dashboard.settings"))

            except (KeyError, ValueError) as e:
                errors.append(f"Chyba ve formuláři: {e}")

    my_advisors = get_my_advisors(user_id)
    return render_template("settings.html", s=current, errors=errors, my_advisors=my_advisors)


# ── /zpravy ───────────────────────────────────────────────────────────────────

@dashboard_bp.route("/zpravy")
@user_required
def messages():
    user_id = session["user_id"]
    msgs = find_all(MESSAGES_FILE, lambda m: m["client_id"] == user_id)
    msgs = sorted(msgs, key=lambda m: m["timestamp"])

    # Označit jako přečtené jen zprávy OD poradce
    for m in msgs:
        if not m.get("read") and m.get("sender", "advisor") == "advisor":
            update_one(MESSAGES_FILE,
                       lambda r, mid=m["id"]: r["id"] == mid,
                       lambda r: {**r, "read": True})

    my_advisors = get_my_advisors(user_id)

    # Sestavit konverzace pro každého poradce
    conversations = {}
    for adv in my_advisors:
        msgs = get_conversation_messages(adv["advisor_id"], user_id)
        # Označit zprávy od poradce jako přečtené
        for m in msgs:
            if not m.get("read") and m.get("sender", "advisor") == "advisor":
                update_one(MESSAGES_FILE,
                           lambda r, mid=m["id"]: r["id"] == mid,
                           lambda r: {**r, "read": True})
        conversations[adv["advisor_id"]] = msgs

    return render_template("messages.html", my_advisors=my_advisors, conversations=conversations)


@dashboard_bp.route("/zpravy/odeslat", methods=["POST"])
@user_required
def send_message_to_advisor():
    advisor_id = request.form.get("advisor_id", "")
    text = request.form.get("text", "").strip()
    user_id = session["user_id"]

    if not text:
        flash("Zpráva nesmí být prázdná.", "warning")
        return redirect(url_for("dashboard.messages"))

    relation = find_one(ADVISOR_CLIENTS_FILE,
                        lambda r, a=advisor_id, c=user_id:
                            r.get("advisor_id") == a
                            and r.get("client_id") == c
                            and r.get("status") == "accepted")
    if not relation:
        flash("Nemáte přijatého poradce s tímto ID.", "danger")
        return redirect(url_for("dashboard.messages"))

    advisor = find_one(USERS_FILE, lambda u, a=advisor_id: u["id"] == a)
    insert(MESSAGES_FILE, {
        "advisor_id":    advisor_id,
        "advisor_email": advisor["email"] if advisor else "poradce",
        "client_id":     user_id,
        "text":          text,
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        "read":          False,
        "sender":        "client",
    })
    flash("Zpráva odeslána.", "success")
    return redirect(url_for("dashboard.messages"))


@dashboard_bp.route("/zpravy/<advisor_id>.json")
@user_required
def messages_json(advisor_id):
    user_id = session["user_id"]
    relation = find_one(ADVISOR_CLIENTS_FILE,
                        lambda r, a=advisor_id, c=user_id:
                            str(r.get("advisor_id", "")) == str(a)
                            and str(r.get("client_id", "")) == str(c)
                            and r.get("status") == "accepted")
    if not relation:
        from flask import jsonify
        return jsonify([]), 403
    from flask import jsonify
    msgs = get_conversation_messages(advisor_id, user_id)
    # Označit zprávy od poradce jako přečtené
    for m in msgs:
        if not m.get("read") and m.get("sender", "advisor") == "advisor":
            update_one(MESSAGES_FILE,
                       lambda r, mid=m["id"]: r["id"] == mid,
                       lambda r: {**r, "read": True})
    return jsonify(msgs)


# ── Pozvánky od poradců ──────────────────────────────────────────────────────

@dashboard_bp.route("/pozvanka/prijmout", methods=["POST"])
@user_required
def accept_invitation():
    advisor_id = request.form.get("advisor_id", "")
    if advisor_id:
        set_advisor_client_status(advisor_id, session["user_id"], "accepted")
        flash("Pozvánka přijata. Poradce nyní vidí váš jídelníček.", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/pozvanka/odmitnut", methods=["POST"])
@user_required
def reject_invitation():
    advisor_id = request.form.get("advisor_id", "")
    user_id = session["user_id"]
    if advisor_id:
        delete_one(ADVISOR_CLIENTS_FILE,
                   lambda r, a=advisor_id, c=user_id: r.get("advisor_id") == a and r.get("client_id") == c)
        flash("Pozvánka odmítnuta.", "info")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/muj-poradce/odvolat", methods=["POST"])
@user_required
def revoke_advisor():
    advisor_id = request.form.get("advisor_id", "")
    user_id = session["user_id"]
    if advisor_id:
        delete_one(ADVISOR_CLIENTS_FILE,
                   lambda r, a=advisor_id, c=user_id: r.get("advisor_id") == a and r.get("client_id") == c)
        flash("Přístup poradce byl odvolán.", "success")
    return redirect(url_for("dashboard.settings"))
