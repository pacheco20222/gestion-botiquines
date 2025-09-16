from flask import Blueprint, render_template
from models.models import Medicine

bp = Blueprint("pages", __name__)

@bp.get("/dashboard")
def dashboard():
    medicines = Medicine.query.order_by(Medicine.id.asc()).all()
    return render_template("inventory.html", medicines=medicines)