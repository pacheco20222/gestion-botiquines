"""
Routes for the Medicine resource.

Sprint 2 goals:
- Full CRUD (list, create, get, update, delete)
- Validations for required fields and dates
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
from db import db
from models.models import Medicine

bp = Blueprint("medicines", __name__)

# -------- Helpers --------
def parse_date(value):
    if isinstance(value, date):
        return value
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

def validate_payload(data, *, partial=False):
    errors = []
    required = ["trade_name", "generic_name", "strength", "expiry_date", "quantity"]
    if not partial:
        for f in required:
            if f not in data or data.get(f) in (None, ""):
                errors.append(f"'{f}' is required")

    for num_field in ["quantity", "reorder_level"]:
        if num_field in data and data[num_field] is not None:
            try:
                v = int(data[num_field])
                if v < 0:
                    errors.append(f"'{num_field}' must be >= 0")
            except (TypeError, ValueError):
                errors.append(f"'{num_field}' must be an integer")

    if "expiry_date" in data and data.get("expiry_date"):
        if parse_date(data["expiry_date"]) is None:
            errors.append("'expiry_date' must be YYYY-MM-DD")

    return (len(errors) == 0, errors)

def to_dict(m: Medicine):
    return {
        "id": m.id,
        "trade_name": m.trade_name,
        "generic_name": m.generic_name,
        "brand": m.brand,
        "strength": m.strength,
        "expiry_date": m.expiry_date.isoformat() if m.expiry_date else None,
        "quantity": m.quantity,
        "reorder_level": m.reorder_level,
        "last_scan_at": m.last_scan_at.isoformat() if m.last_scan_at else None,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        "status": m.status(),
    }

# -------- Routes --------

@bp.get("/")
def list_medicines():
    meds = Medicine.query.order_by(Medicine.id.asc()).all()
    return jsonify([to_dict(m) for m in meds]), 200

@bp.post("/")
def create_medicine():
    data = request.get_json() or {}
    ok, errors = validate_payload(data, partial=False)
    if not ok:
        return jsonify({"errors": errors}), 400

    med = Medicine(
        trade_name=data.get("trade_name"),
        generic_name=data.get("generic_name"),
        brand=data.get("brand"),
        strength=data.get("strength"),
        expiry_date=parse_date(data.get("expiry_date")),
        quantity=int(data.get("quantity")),
        reorder_level=int(data.get("reorder_level", 0)),
        last_scan_at=datetime.utcnow(),
    )
    db.session.add(med)
    db.session.commit()
    return jsonify(to_dict(med)), 201

@bp.get("/<int:med_id>")
def get_medicine(med_id):
    med = Medicine.query.get(med_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404
    return jsonify(to_dict(med)), 200

@bp.put("/<int:med_id>")
def update_medicine(med_id):
    med = Medicine.query.get(med_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404

    data = request.get_json() or {}
    ok, errors = validate_payload(data, partial=True)
    if not ok:
        return jsonify({"errors": errors}), 400

    fields = ["trade_name", "generic_name", "brand", "strength", "expiry_date", "quantity", "reorder_level", "last_scan_at"]
    for f in fields:
        if f in data:
            if f == "expiry_date":
                setattr(med, f, parse_date(data[f]))
            elif f in ["quantity", "reorder_level"]:
                setattr(med, f, int(data[f]) if data[f] is not None else None)
            elif f == "last_scan_at":
                val = data[f]
                if val is True:
                    setattr(med, f, datetime.utcnow())
                elif isinstance(val, str):
                    try:
                        setattr(med, f, datetime.fromisoformat(val))
                    except ValueError:
                        pass
            else:
                setattr(med, f, data[f])

    db.session.commit()
    return jsonify(to_dict(med)), 200

@bp.delete("/<int:med_id>")
def delete_medicine(med_id):
    med = Medicine.query.get(med_id)
    if not med:
        return jsonify({"error": "Medicine not found"}), 404

    db.session.delete(med)
    db.session.commit()
    return jsonify({"message": "Medicine deleted"}), 200
