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
        "compartment": 1,
        "weight": 45.5,
        "unit": "grams"
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
        required = ["hardware_id", "compartment", "weight"]
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
        log_entry.compartment_number = data["compartment"]
        log_entry.weight_reading = data["weight"]
        
        # Find medicine in the compartment
        medicine = Medicine.query.filter_by(
            botiquin_id=botiquin.id,
            compartment_number=data["compartment"]
        ).first()
        
        if not medicine:
            log_entry.error_message = f"No medicine found in compartment {data['compartment']}"
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({
                "warning": f"No medicine assigned to compartment {data['compartment']}",
                "botiquin": botiquin.name,
                "compartment": data["compartment"]
            }), 200
        
        # Update medicine weight and calculate new quantity
        old_quantity = medicine.quantity
        old_weight = medicine.current_weight
        
        # Update from sensor
        new_quantity = medicine.update_from_sensor(data["weight"])
        
        # Update botiquin sync timestamp
        botiquin.last_sync_at = datetime.utcnow()
        
        # Mark log as processed
        log_entry.processed = True
        
        db.session.add(log_entry)
        db.session.commit()
        
        # Prepare response
        response = {
            "success": True,
            "botiquin": {
                "id": botiquin.id,
                "name": botiquin.name,
                "hardware_id": botiquin.hardware_id
            },
            "medicine": {
                "id": medicine.id,
                "name": medicine.trade_name,
                "compartment": medicine.compartment_number,
                "old_weight": old_weight,
                "new_weight": medicine.current_weight,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "quantity_change": new_quantity - old_quantity,
                "status": medicine.status(),
                "unit_weight": medicine.unit_weight
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add alert if critical status
        if medicine.status() in ["OUT_OF_STOCK", "EXPIRED"]:
            response["alert"] = {
                "type": "critical",
                "message": f"{medicine.trade_name} is {medicine.status()}"
            }
        elif medicine.status() in ["LOW_STOCK", "EXPIRES_SOON"]:
            response["alert"] = {
                "type": "warning", 
                "message": f"{medicine.trade_name} is {medicine.status()}"
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        log_entry.error_message = str(e)
        log_entry.processed = False
        db.session.add(log_entry)
        db.session.commit()
        return jsonify({"error": f"Processing error: {str(e)}"}), 500


@bp.post("/batch_sensor_data")
def receive_batch_sensor_data():
    """
    Receive multiple sensor readings at once.
    Useful when hardware sends data for all compartments.
    
    Expected JSON format:
    {
        "hardware_id": "BOT001",
        "timestamp": "2025-09-23T10:30:00",
        "readings": [
            {"compartment": 1, "weight": 45.5},
            {"compartment": 2, "weight": 30.2},
            {"compartment": 3, "weight": 0.0}
        ]
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    if "hardware_id" not in data or "readings" not in data:
        return jsonify({"error": "Missing hardware_id or readings"}), 400
    
    # Find botiquin
    botiquin = Botiquin.query.filter_by(hardware_id=data["hardware_id"]).first()
    if not botiquin:
        return jsonify({"error": f"Botiquin not found for hardware_id: {data['hardware_id']}"}), 404
    
    results = []
    errors = []
    
    # Process each reading
    for reading in data.get("readings", []):
        try:
            if "compartment" not in reading or "weight" not in reading:
                errors.append({"compartment": reading.get("compartment"), "error": "Missing data"})
                continue
            
            # Log the reading
            log_entry = HardwareLog(
                botiquin_id=botiquin.id,
                compartment_number=reading["compartment"],
                weight_reading=reading["weight"],
                sensor_type="weight",
                raw_data=json.dumps(reading),
                created_at=datetime.utcnow()
            )
            
            # Find medicine
            medicine = Medicine.query.filter_by(
                botiquin_id=botiquin.id,
                compartment_number=reading["compartment"]
            ).first()
            
            if not medicine:
                log_entry.error_message = "No medicine in compartment"
                log_entry.processed = False
                db.session.add(log_entry)
                results.append({
                    "compartment": reading["compartment"],
                    "status": "empty",
                    "weight": reading["weight"]
                })
                continue
            
            # Update medicine
            old_quantity = medicine.quantity
            new_quantity = medicine.update_from_sensor(reading["weight"])
            
            log_entry.processed = True
            db.session.add(log_entry)
            
            results.append({
                "compartment": reading["compartment"],
                "medicine": medicine.trade_name,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "status": medicine.status()
            })
            
        except Exception as e:
            errors.append({
                "compartment": reading.get("compartment"),
                "error": str(e)
            })
    
    # Update botiquin sync time
    botiquin.last_sync_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        "success": len(errors) == 0,
        "botiquin": botiquin.name,
        "processed": len(results),
        "results": results,
        "errors": errors if errors else None,
        "timestamp": datetime.utcnow().isoformat()
    }), 200


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
        "company_id": 1,
        "name": "Botiquín Principal",
        "location": "Planta Baja",
        "compartments": 12
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Check required fields
    required = ["hardware_id", "company_id", "name"]
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
    
    # Create new botiquin
    from models.models import Company
    company = Company.query.get(data["company_id"])
    if not company:
        return jsonify({"error": f"Company {data['company_id']} not found"}), 404
    
    compartments = data.get("compartments", 12)
    rows = data.get("rows", 3)
    cols = data.get("cols", 4)
    
    # Auto-calculate grid if not provided
    if compartments and not (data.get("rows") and data.get("cols")):
        if compartments == 12:
            rows, cols = 3, 4
        elif compartments == 16:
            rows, cols = 4, 4
        elif compartments == 20:
            rows, cols = 4, 5
        else:
            # Default grid
            cols = 4
            rows = (compartments + 3) // 4
    
    botiquin = Botiquin(
        hardware_id=data["hardware_id"],
        name=data["name"],
        location=data.get("location", ""),
        company_id=company.id,
        total_compartments=compartments,
        compartment_rows=rows,
        compartment_cols=cols,
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