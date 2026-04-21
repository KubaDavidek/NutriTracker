"""
auth_utils.py – Pomocné funkce pro autentizaci.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, flash


def hash_password(plain: str) -> str:
    return generate_password_hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return check_password_hash(hashed, plain)


# ── Dekorátory ────────────────────────────────────────────────────────────────

def login_required(f):
    """Přesměruje nepřihlášeného uživatele na /login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Pro přístup se musíš přihlásit.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def advisor_required(f):
    """Povolí přístup pouze uživatelům s rolí 'advisor'."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Pro přístup se musíš přihlásit.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "advisor":
            flash("Tato sekce je určena pouze pro poradce.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated


def premium_required(f):
    """Povolí přístup pouze premium uživatelům."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_premium"):
            flash("Tato funkce je dostupná pouze pro Premium uživatele.", "warning")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated


def user_required(f):
    """Blokuje poradce – tato sekce je pouze pro běžné uživatele."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Pro přístup se musíš přihlásit.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") == "advisor":
            flash("Jako poradce nemáš přístup do osobního deníku.", "warning")
            return redirect(url_for("advisor.index"))
        return f(*args, **kwargs)
    return decorated
