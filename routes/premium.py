"""
routes/premium.py – Premium předplatné: aktivace kódem, mikroživiny, recepty.
"""

from datetime import date

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)

from utils.json_db         import USERS_FILE, update_one, get_log, compute_day_totals
from utils.auth_utils      import login_required, user_required
from utils.nutrition_utils import estimate_micronutrients, get_healthy_recipes

premium_bp = Blueprint("premium", __name__, url_prefix="/premium")

# ── Platné aktivační kódy ──────────────────────────────────────────────────
PREMIUM_CODES = {"NUTRI2026", "PREMIUM", "FITLIFE2026", "SKOLA123"}


# ── GET /premium ──────────────────────────────────────────────────────────

@premium_bp.route("/", methods=["GET"])
@user_required
def index():
    is_premium = session.get("is_premium", False)
    recipes    = []
    micros     = {}
    totals     = {}

    if is_premium:
        day    = str(date.today())
        log    = get_log(session["user_id"], day)
        totals = compute_day_totals(log) if log else {}
        micros = estimate_micronutrients(totals)
        recipes = get_healthy_recipes(3)

    return render_template(
        "premium.html",
        is_premium=is_premium,
        recipes=recipes,
        micros=micros,
        totals=totals,
    )


# ── POST /premium/activate ─────────────────────────────────────────────────

@premium_bp.route("/activate", methods=["POST"])
@user_required
def activate():
    code = request.form.get("code", "").strip().upper()

    if code not in PREMIUM_CODES:
        flash("Neplatný aktivační kód. Zkuste znovu.", "danger")
        return redirect(url_for("premium.index"))

    if session.get("is_premium"):
        flash("Váš účet již má Premium aktivováno.", "info")
        return redirect(url_for("premium.index"))

    # Ulož do DB
    uid = session["user_id"]
    updated = update_one(
        USERS_FILE,
        lambda u: u["id"] == uid,
        lambda u: {**u, "is_premium": True},
    )

    if updated:
        session["is_premium"] = True
        flash("Premium aktivováno.", "success")
    else:
        flash("Při aktivaci nastala chyba. Zkuste to znovu.", "danger")

    return redirect(url_for("premium.index"))
