"""
app.py – Hlavní vstupní bod Flask aplikace.
"""

import os
from flask import Flask

# nacti .env pokud existuje
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

from utils.json_db import init_db
from routes.auth      import auth_bp
from routes.dashboard import dashboard_bp
from routes.advisor   import advisor_bp
from routes.api       import api_bp
from routes.premium   import premium_bp
from routes.recipes   import recipes_bp
from routes.weight    import weight_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Bezpečnostní klíč (v produkci nastav přes env proměnnou!) ────────────
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.environ.get("SECRET_KEY", "change-me-in-production-please"))

    # ── Inicializace JSON souborů ─────────────────────────────────────────────
    init_db()

    # ── Uzavři DB spojení po každém requestu ──────────────────────────────────
    @app.teardown_appcontext
    def close_db(error):
        from flask import g
        from utils.json_db import _get_pool
        cnx = g.pop("_db_conn", None)
        if cnx is not None and not cnx.closed:
            try:
                _get_pool().putconn(cnx)
            except Exception:
                cnx.close()

    # ── Registrace Blueprintů ─────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(advisor_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(premium_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(weight_bp)

    # ── Globální context: počet nepřečtených zpráv (pro nav badge) ───────────
    from flask import session as _session
    from utils.json_db import _fetch_one

    @app.context_processor
    def inject_unread():
        uid = _session.get("user_id")
        if uid:
            try:
                row = _fetch_one(
                    "SELECT COUNT(*) AS cnt FROM messages WHERE client_id=%s AND is_read=false AND sender='advisor'",
                    (uid,)
                )
                count = int(row["cnt"]) if row else 0
            except Exception:
                count = 0
        else:
            count = 0
        return {"nav_unread": count}

    # ── Kořenová přesměrování ─────────────────────────────────────────────────
    from flask import redirect, url_for, jsonify
    @app.route("/")
    def index():
        return redirect(url_for("dashboard.index"))

    # ── Keep-alive ping (zabraňuje uspání na Render free tier) ───────────────
    @app.route("/ping")
    def ping():
        return jsonify({"ok": True}), 200

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
