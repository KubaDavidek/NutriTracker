"""
routes/advisor.py – Poradce: seznam klientů, náhled do jejich denního logu.
"""

from datetime import date, datetime, timedelta
from flask import (Blueprint, render_template, request,
                   flash, redirect, url_for, session, jsonify)

from utils.json_db    import (ADVISOR_CLIENTS_FILE, USERS_FILE, LOGS_FILE,
                               MESSAGES_FILE,
                               find_all, find_one, insert, delete_one,
                               get_log, compute_day_totals, get_or_create_log,
                               get_user_settings, set_advisor_client_status,
                               update_one, get_conversation_messages)
from utils.auth_utils    import advisor_required


advisor_bp = Blueprint("advisor", __name__, url_prefix="/advisor")

MEAL_SLOTS = [
    ("snidane",  "Snídáně",             "primary"),
    ("svacina",  "Dopoledńí svačina",   "primary"),
    ("obed",     "Oběd",               "primary"),
    ("svacina2", "Odpoledni svačina",   "primary"),
    ("vecere",   "Večeře",             "primary"),
]


# ── /advisor ──────────────────────────────────────────────────────────────────

@advisor_bp.route("/")
@advisor_required
def index():
    advisor_id = session["user_id"]

    # Načti vazby poradce → klient (jen přijaté)
    relations = find_all(ADVISOR_CLIENTS_FILE,
                         lambda r: r["advisor_id"] == advisor_id
                                   and r.get("status") == "accepted")
    client_ids = [r["client_id"] for r in relations]

    # Čekající pozvánky
    pending = find_all(ADVISOR_CLIENTS_FILE,
                       lambda r: r["advisor_id"] == advisor_id
                                 and r.get("status") == "pending")
    pending_clients = []
    for p in pending:
        u = find_one(USERS_FILE, lambda x, cid=p["client_id"]: x["id"] == cid)
        if u:
            pending_clients.append({"id": u["id"], "email": u["email"]})

    # Načti profily klientů + dnešní statistiky
    today = str(date.today())
    clients = []
    for cid in client_ids:
        user = find_one(USERS_FILE, lambda u, c=cid: u["id"] == c)
        if not user:
            continue
        # Dnešní log + součty
        today_log    = get_log(cid, today)
        today_totals = compute_day_totals(today_log) if today_log else {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}
        # Cíle klienta
        settings     = get_user_settings(cid)
        kcal_target  = settings.get("kcal_target", 2000)
        # Počet nepřečtených zpráv OD klienta (sender='client')
        unread = len(find_all(MESSAGES_FILE,
                              lambda m, c=cid: m["client_id"] == c
                              and m["advisor_id"] == advisor_id
                              and not m.get("read", False)
                              and m.get("sender", "advisor") == "client"))
        clients.append({
            "id":          user["id"],
            "email":       user["email"],
            "is_premium":  user.get("is_premium", False),
            "today_kcal":  today_totals["kcal"],
            "kcal_target": kcal_target,
            "unread":      unread,
        })

    return render_template("advisor.html", clients=clients, pending_clients=pending_clients)


# ── /advisor/client/<client_id> ───────────────────────────────────────────────

@advisor_bp.route("/client/<client_id>")
@advisor_required
def client_detail(client_id):
    advisor_id = session["user_id"]

    # Ověř, že klient patří tomuto poradci a pozvánka je přijatá
    relation = find_one(ADVISOR_CLIENTS_FILE,
                        lambda r: r["advisor_id"] == advisor_id
                                  and r["client_id"] == client_id
                                  and r.get("status") == "accepted")
    if not relation:
        flash("Přístup odepřen – klient není ve vašem portfoliu.", "danger")
        return redirect(url_for("advisor.index"))

    client = find_one(USERS_FILE, lambda u: u["id"] == client_id)
    if not client:
        flash("Klient nenalezen.", "danger")
        return redirect(url_for("advisor.index"))

    day    = request.args.get("date", str(date.today()))
    day_dt = date.fromisoformat(day)
    prev_day = str(day_dt - timedelta(days=1))
    next_day = str(day_dt + timedelta(days=1))
    log    = get_log(client_id, day) or get_or_create_log(client_id, day)
    totals = compute_day_totals(log)
    micros = totals

    # Cíle klienta
    settings = get_user_settings(client_id)
    targets = {
        "kcal":    settings.get("kcal_target", 2000),
        "protein": settings.get("protein_target", 150),
        "carbs":   settings.get("carbs_target", 250),
        "fat":     settings.get("fat_target", 65),
    }

    # Zprávy – obě strany, chronologicky
    messages = get_conversation_messages(advisor_id, client_id)

    # Označ zprávy OD klienta jako přečtené
    for m in messages:
        if not m.get("read") and m.get("sender", "advisor") == "client":
            update_one(MESSAGES_FILE,
                       lambda r, mid=m["id"]: r["id"] == mid,
                       lambda r: {**r, "read": True})

    return render_template(
        "advisor_client.html",
        client=client,
        day=day,
        prev_day=prev_day,
        next_day=next_day,
        log=log,
        totals=totals,
        meal_slots=MEAL_SLOTS,
        messages=messages,
        micros=micros,
        targets=targets,
        readonly=True,
    )


# ── /advisor/client/<client_id>/zprava ────────────────────────────────────────

@advisor_bp.route("/client/<client_id>/zprava", methods=["POST"])
@advisor_required
def send_message(client_id):
    advisor_id = session["user_id"]
    text = request.form.get("text", "").strip()
    if not text:
        flash("Zpráva nesmí být prázdná.", "warning")
        return redirect(url_for("advisor.client_detail", client_id=client_id))

    # Ověř, že je to opravdu klient tohoto poradce (přijatý)
    relation = find_one(ADVISOR_CLIENTS_FILE,
                        lambda r: r["advisor_id"] == advisor_id
                                  and r["client_id"] == client_id
                                  and r.get("status") == "accepted")
    if not relation:
        flash("Přístup odepřen.", "danger")
        return redirect(url_for("advisor.index"))

    advisor = find_one(USERS_FILE, lambda u: u["id"] == advisor_id)
    insert(MESSAGES_FILE, {
        "advisor_id":    advisor_id,
        "advisor_email": advisor["email"] if advisor else "poradce",
        "client_id":     client_id,
        "text":          text,
        "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        "read":          False,
    })
    flash("Zpráva odeslána.", "success")
    return redirect(url_for("advisor.client_detail", client_id=client_id))


# ── /advisor/client/<client_id>/zpravy.json ───────────────────────────────────

@advisor_bp.route("/client/<client_id>/zpravy.json")
@advisor_required
def messages_json(client_id):
    advisor_id = session["user_id"]
    relation = find_one(ADVISOR_CLIENTS_FILE,
                        lambda r: r["advisor_id"] == advisor_id
                                  and r["client_id"] == client_id
                                  and r.get("status") == "accepted")
    if not relation:
        return jsonify([]), 403
    msgs = get_conversation_messages(advisor_id, client_id)
    # Označ zprávy od klienta jako přečtené
    for m in msgs:
        if not m.get("read") and m.get("sender", "advisor") == "client":
            update_one(MESSAGES_FILE,
                       lambda r, mid=m["id"]: r["id"] == mid,
                       lambda r: {**r, "read": True})
    return jsonify(msgs)


# ── /advisor/message/<msg_id>/smazat ─────────────────────────────────────────

@advisor_bp.route("/message/<msg_id>/smazat", methods=["POST"])
@advisor_required
def delete_message(msg_id):
    advisor_id = session["user_id"]
    client_id  = request.form.get("client_id", "")
    delete_one(MESSAGES_FILE,
               lambda m: m["id"] == msg_id and m["advisor_id"] == advisor_id)
    return redirect(url_for("advisor.client_detail", client_id=client_id))


# ── /advisor/assign ────────────────────────────────────────────────────────────
# (Jednoduché přiřazení klienta poradci – POST formulářem)

@advisor_bp.route("/assign", methods=["POST"])
@advisor_required
def assign_client():
    client_email = request.form.get("client_email", "").strip().lower()
    advisor_id   = session["user_id"]

    client = find_one(USERS_FILE, lambda u: u["email"] == client_email
                                            and u["role"] == "user")
    if not client:
        flash("Uživatel s tímto e-mailem nebyl nalezen nebo není typu 'user'.", "warning")
        return redirect(url_for("advisor.index"))

    # Zkontroluj duplicitu
    existing = find_one(ADVISOR_CLIENTS_FILE,
                        lambda r: r["advisor_id"] == advisor_id
                                  and r["client_id"] == client["id"])
    if existing:
        flash("Klient je již ve vašem portfoliu.", "info")
        return redirect(url_for("advisor.index"))

    insert(ADVISOR_CLIENTS_FILE, {
        "advisor_id": advisor_id,
        "client_id":  client["id"],
        "status":     "pending",
    })
    flash(f"Pozvánka byla odeslána klientovi {client_email}. Čeká na přijetí.", "info")
    return redirect(url_for("advisor.index"))


# ── /advisor/remove ────────────────────────────────────────────────────────────

@advisor_bp.route("/remove", methods=["POST"])
@advisor_required
def remove_client():
    advisor_id = session["user_id"]
    client_id  = request.form.get("client_id", "").strip()
    if not client_id:
        flash("Chybí ID klienta.", "warning")
        return redirect(url_for("advisor.index"))

    deleted = delete_one(ADVISOR_CLIENTS_FILE,
                         lambda r: r["advisor_id"] == advisor_id
                                   and r["client_id"] == client_id)
    if deleted:
        flash("Klient byl odebrán z vašeho portfolia.", "success")
    else:
        flash("Klient nenalezen.", "warning")
    return redirect(url_for("advisor.index"))
