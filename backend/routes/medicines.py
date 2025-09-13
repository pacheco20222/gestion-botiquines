"""
Routes for the Medicine resource.

For Sprint 1 we keep it very simple:
- GET /api/medicines/ : list all medicines
- POST /api/medicines/ : create a new medicine
"""

from datetime import datetime
from flask import Blueprint, jsonify, request
from db import db
from models.models import Medicine

# Create a blueprint (a modular set of routes)
bp = Blueprint("medicines", __name__)


@bp.get("/")
def list_medicines():
    """
    List all medicines in the database.
    Returns JSON array with each medicine serialized.
    """
    meds = Medicine.query.order_by(Medicine.trade_name.asc()).all()
    return jsonify([m.to_dict() for m in meds]), 200


@bp.post("/")
def create_medicine():
    """
    Create a new medicine.
    Expects JSON body with required fields:
      - trade_name
      - generic_name
      - quantity
    Optional fields:
      - brand, strength, expiry_date (YYYY-MM-DD), reorder_level
    """
    data = request.get_json() or {}

    # Required fields check
    required = ["trade_name", "generic_name", "quantity"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    # Build the medicine object
    med = Medicine(
        trade_name=data["trade_name"],
        generic_name=data["generic_name"],
        brand=data.get("brand"),
        strength=data.get("strength"),
        quantity=int(data.get("quantity", 0)),
        reorder_level=int(data.get("reorder_level", 2)),
        last_scan_at=datetime.utcnow()
    )

    # Parse expiry_date if provided
    expiry = data.get("expiry_date")
    if expiry:
        try:
            med.expiry_date = datetime.fromisoformat(expiry).date()
        except Exception:
            return jsonify({"error": "expiry_date must be in YYYY-MM-DD format"}), 400

    # Save to DB
    db.session.add(med)
    db.session.commit()

    return jsonify(med.to_dict()), 201