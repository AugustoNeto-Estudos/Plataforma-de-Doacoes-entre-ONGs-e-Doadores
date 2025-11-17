from flask import Blueprint, render_template

termos_bp = Blueprint("termos", __name__)

@termos_bp.route("/termos")
def termos():
    return render_template("termos.html")
