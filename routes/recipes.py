"""
routes/recipes.py – Stránka se zdravými recepty (pouze pro premium uživatele).
"""

from flask import Blueprint, render_template, request, session

from utils.auth_utils      import login_required, premium_required, user_required
from utils.nutrition_utils import get_all_recipes

recipes_bp = Blueprint("recipes", __name__, url_prefix="/recepty")


@recipes_bp.route("/")
@user_required
@premium_required
def index():
    # Filtry z query parametrů
    cat_filter = request.args.get("category", "").strip()
    tag_filter = request.args.get("tag", "").strip()

    all_recipes = get_all_recipes()

    # Sbírej unikátní kategorie a tagy pro filtry
    categories = sorted({r["category"] for r in all_recipes})
    all_tags   = sorted({tag for r in all_recipes for tag in r["tags"]})

    # Filtruj
    filtered = all_recipes
    if cat_filter:
        filtered = [r for r in filtered if r["category"] == cat_filter]
    if tag_filter:
        filtered = [r for r in filtered if tag_filter in r["tags"]]

    # Seřaď podle kcal (od nejnižší)
    filtered = sorted(filtered, key=lambda r: r["kcal"])

    return render_template(
        "recipes.html",
        recipes=filtered,
        categories=categories,
        all_tags=all_tags,
        cat_filter=cat_filter,
        tag_filter=tag_filter,
        total_count=len(all_recipes),
    )
