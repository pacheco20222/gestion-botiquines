"""
Routes for hardware integration.
Receives sensor data and updates medicine inventory.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from db import db
from models.models import Botiquin, Medicine, HardwareLog

bp = Blueprint("hardware", __name__)


@bp.post("/sensor_data")
def receive_sensor_data():
    """
    Main endpoint to receive data from hardware sensors.
    
    Expected JSON format:
    {
        "hardware_id": "BOT001",
        "timestamp": "2025-09-23T10:30:00",
        "sensor_type": "weight",
        "compartments": [
            {"compartment": 1, "weight": 45.5, "unit": "grams"},
            {"compartment": 2, "weight": 30.2, "unit": "grams"},
            {"compartment": 3, "weight": 0.0, "unit": "grams"}
        ]
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Log raw data for debugging
    log_entry = HardwareLog(
        raw_data=json.dumps(data),
        sensor_type=data.get("sensor_type", "unknown"),
        created_at=datetime.utcnow()
    )
    
    try:
        # Validate required fields
        required = ["hardware_id", "compartments"]
        missing = [f for f in required if f not in data]
        if missing:
            log_entry.error_message = f"Missing fields: {missing}"
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": f"Missing required fields: {missing}"}), 400
        
        # Find botiquin by hardware_id
        botiquin = Botiquin.query.filter_by(hardware_id=data["hardware_id"]).first()
        if not botiquin:
            log_entry.error_message = f"Botiquin with hardware_id '{data['hardware_id']}' not found"
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": f"Botiquin not found for hardware_id: {data['hardware_id']}"}), 404
        
        log_entry.botiquin_id = botiquin.id
        
        results = []
        errors = []
        
        # Iterate through compartments
        for comp in data["compartments"]:
            compartment_number = comp.get("compartment")
            weight = comp.get("weight")
            
            # Create individual log entries per compartment
            comp_log = HardwareLog(
                botiquin_id=botiquin.id,
                compartment_number=compartment_number,
                weight_reading=weight,
                sensor_type=data.get("sensor_type", "unknown"),
                raw_data=json.dumps(comp),
                created_at=datetime.utcnow()
            )
            
            if compartment_number is None or weight is None:
                comp_log.error_message = "Missing compartment or weight data"
                comp_log.processed = False
                db.session.add(comp_log)
                errors.append({
                    "compartment": compartment_number,
                    "error": "Missing compartment or weight data"
                })
                continue
            
            # Find medicine in the compartment
            medicine = Medicine.query.filter_by(
                botiquin_id=botiquin.id,
                compartment_number=compartment_number
            ).first()
            
            if not medicine:
                comp_log.error_message = f"No medicine found in compartment {compartment_number}"
                comp_log.processed = False
                db.session.add(comp_log)
                errors.append({
                    "compartment": compartment_number,
                    "warning": f"No medicine assigned to compartment {compartment_number}"
                })
                results.append({
                    "compartment": compartment_number,
                    "status": "empty",
                    "weight": weight
                })
                continue
            
            # Update medicine weight and calculate new quantity
            old_quantity = medicine.quantity
            old_weight = medicine.current_weight
            
            # Update from sensor
            new_quantity = medicine.update_from_sensor(weight)
            
            # Mark compartment log as processed
            comp_log.processed = True
            db.session.add(comp_log)
            
            results.append({
                "compartment": compartment_number,
                "medicine": medicine.trade_name,
                "old_weight": old_weight,
                "new_weight": medicine.current_weight,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "quantity_change": new_quantity - old_quantity,
                "status": medicine.status(),
                "unit_weight": medicine.unit_weight
            })
        
        # Update botiquin sync timestamp
        botiquin.last_sync_at = datetime.utcnow()
        
        # Mark main log as processed
        log_entry.processed = True
        
        db.session.add(log_entry)
        db.session.commit()
        
        # Prepare response
        response = {
            "success": len(errors) == 0,
            "botiquin": {
                "id": botiquin.id,
                "name": botiquin.name,
                "hardware_id": botiquin.hardware_id
            },
            "results": results,
            "errors": errors if errors else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add alerts if any medicine has critical or warning status
        alerts = []
        for res in results:
            status = res.get("status")
            if status in ["OUT_OF_STOCK", "EXPIRED"]:
                alerts.append({
                    "type": "critical",
                    "message": f"{res.get('medicine')} is {status}"
                })
            elif status in ["LOW_STOCK", "EXPIRES_SOON"]:
                alerts.append({
                    "type": "warning", 
                    "message": f"{res.get('medicine')} is {status}"
                })
        if alerts:
            response["alerts"] = alerts
        
        return jsonify(response), 200
        
    except Exception as e:
        log_entry.error_message = str(e)
        log_entry.processed = False
        db.session.add(log_entry)
        db.session.commit()
        return jsonify({"error": f"Processing error: {str(e)}"}), 500


# Removed /batch_sensor_data endpoint as per instructions


@bp.get("/logs")
def get_hardware_logs():
    """
    Get hardware communication logs for debugging.
    Can filter by botiquin_id, processed status, or date range.
    """
    botiquin_id = request.args.get("botiquin_id")
    processed = request.args.get("processed")
    limit = request.args.get("limit", 100, type=int)
    
    query = HardwareLog.query
    
    if botiquin_id:
        query = query.filter_by(botiquin_id=botiquin_id)
    
    if processed is not None:
        query = query.filter_by(processed=processed.lower() == "true")
    
    logs = query.order_by(HardwareLog.created_at.desc()).limit(limit).all()
    
    return jsonify([log.to_dict() for log in logs]), 200


@bp.post("/test_connection")
def test_hardware_connection():
    """
    Test endpoint for hardware to verify connection.
    Hardware can ping this to confirm API is reachable.
    """
    data = request.get_json() or {}
    hardware_id = data.get("hardware_id", "unknown")
    
    # Check if botiquin exists
    botiquin = None
    if hardware_id != "unknown":
        botiquin = Botiquin.query.filter_by(hardware_id=hardware_id).first()
    
    return jsonify({
        "status": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "hardware_id": hardware_id,
        "botiquin_found": botiquin is not None,
        "botiquin_name": botiquin.name if botiquin else None,
        "message": "Hardware connection successful"
    }), 200


@bp.post("/register_hardware")
def register_hardware():
    """
    Register new hardware with the system.
    Creates a new botiquin if it doesn't exist.
    
    Expected JSON:
    {
        "hardware_id": "BOT001",
        "name": "Botiquín Principal",
        "location": "Planta Baja",
        "compartments": 12
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Check required fields
    required = ["hardware_id", "name"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    
    # Check if already exists
    existing = Botiquin.query.filter_by(hardware_id=data["hardware_id"]).first()
    if existing:
        return jsonify({
            "status": "already_registered",
            "botiquin": existing.to_dict()
        }), 200
    
    # company_id is optional
    company_id = data.get("company_id", None)
    
    compartments = data.get("compartments", 12)
    
    botiquin = Botiquin(
        hardware_id=data["hardware_id"],
        name=data["name"],
        location=data.get("location", ""),
        company_id=company_id,
        total_compartments=compartments,
        active=True,
        last_sync_at=datetime.utcnow()
    )
    
    db.session.add(botiquin)
    db.session.commit()
    
    return jsonify({
        "status": "registered",
        "botiquin": botiquin.to_dict(),
        "message": f"Hardware registered successfully as '{botiquin.name}'"
    }), 201