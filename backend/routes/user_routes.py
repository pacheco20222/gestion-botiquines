from flask import Blueprint, request, jsonify
from db import db
from models.models import User

bp = Blueprint("users", __name__)

@bp.post("/register")
def register():
    data = request.get_json or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"Error":"Username and Password are both required"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"Error":"Username is already registered"}), 400
    
    user = User(username=username)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"Message":"The user has been created successfully"})

@bp.post("/login")
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"Error":"Username and Password are both required"}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"Error":"Invalid Credentials"})

    # For MVP: just return a success message
    return jsonify({"message": f"Welcome, {username}!"}), 200