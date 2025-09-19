from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from werkzeug.security import check_password_hash
from db import db
from models.models import User

bp = Blueprint("users", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        data = request.form if request.form else request.json

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Query user securely (SQLAlchemy protects from SQL injection)
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # For demo purposes, we just track in session
            session["user_id"] = user.id
            return redirect(url_for("pages.dashboard"))
        else:
            return jsonify({"error": "Invalid credentials"}), 401