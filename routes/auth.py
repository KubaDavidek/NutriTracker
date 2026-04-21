"""
routes/auth.py – Registrace, přihlášení, odhlášení.
"""

from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, session)

from utils.json_db   import USERS_FILE, find_one, insert
from utils.auth_utils import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)


# ── /register ────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")
        role     = request.form.get("role", "user")  # "user" nebo "advisor"

        if not name:
            flash("Jméno je povinné.", "danger")
            return render_template("register.html")

        if not email or not password:
            flash("E-mail a heslo jsou povinné.", "danger")
            return render_template("register.html")

        if password != password2:
            flash("Hesla se neshodují.", "danger")
            return render_template("register.html")

        if role not in ("user", "advisor"):
            role = "user"

        # Zkontroluj, zda e-mail není duplicitní
        existing = find_one(USERS_FILE, lambda u: u["email"] == email)
        if existing:
            flash("Tento e-mail je již zaregistrován.", "warning")
            return render_template("register.html")

        new_user = {
            "name":          name,
            "email":         email,
            "password_hash": hash_password(password),
            "role":          role,
            "is_premium":    False,
        }
        user = insert(USERS_FILE, new_user)

        flash("Registrace proběhla úspěšně! Přihlaš se.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ── /login ────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = find_one(USERS_FILE, lambda u: u["email"] == email)

        if not user or not verify_password(password, user["password_hash"]):
            flash("Nesprávný e-mail nebo heslo.", "danger")
            return render_template("login.html")

        # Nastav session
        session.clear()
        session["user_id"]    = user["id"]
        session["name"]       = user.get("name") or user["email"]
        session["email"]      = user["email"]
        session["role"]       = user["role"]
        session["is_premium"] = user.get("is_premium", False)

        flash(f"Vítej, {session['name']}!", "success")

        if user["role"] == "advisor":
            return redirect(url_for("advisor.index"))
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")


# ── /logout ───────────────────────────────────────────────────────────────────

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Byl jsi odhlášen.", "info")
    return redirect(url_for("auth.login"))
