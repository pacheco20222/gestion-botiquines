from flask import Blueprint, render_template, request, redirect, url_for
from models.models import Medicine
from datetime import datetime

bp = Blueprint("pages", __name__)

@bp.route("/")
def index():
    return redirect(url_for("users.login"))

@bp.get("/dashboard")
def dashboard():
    status = request.args.get("status")  # optional filter
    medicines = Medicine.query.order_by(Medicine.id.asc()).all()

    # Apply filter if status provided
    if status:
        medicines = [m for m in medicines if m.status() == status]

    medicines_dict = [m.to_dict() for m in medicines]

    # Build summary info
    summary = {
        "total": len(medicines),
        "critical": sum(1 for m in medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"]),
        "low_stock": sum(1 for m in medicines if m.status() == "LOW_STOCK"),
        "last_update": max([m.updated_at for m in medicines]).strftime("%Y-%m-%d %H:%M:%S") if medicines else "N/A"
    }

    return render_template(
        "inventory.html",
        medicines=medicines_dict,
        current_status=status,
        summary=summary
    )