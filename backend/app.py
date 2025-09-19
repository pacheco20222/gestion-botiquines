"""
Flask application factory for the MVP.

- Creates the Flask app
- Initializes the database (via db.py)
- Registers blueprints (routes)
"""

from flask import Flask, jsonify
from datetime import datetime
import os

from db import init_db   # our init_db function
from db import db        # the shared SQLAlchemy instance

from routes.medicines import bp as medicines_bp
from routes.user_routes import bp as users_bp
from routes.pages import bp as pages_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "frontend", "templates")
# te quiero mucho pachecon - cambranis

def create_app():
    """
    Application factory: builds and configures the Flask app.
    """
    app = Flask(__name__, template_folder=TEMPLATES_DIR)

    # 1) Database setup
    init_db(app)
    app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

    # 2) Register blueprints
    app.register_blueprint(medicines_bp, url_prefix="/api/medicines")
    app.register_blueprint(users_bp)
    app.register_blueprint(pages_bp)

    # 3) Health check route (simple MVP check)
    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "time": datetime.utcnow().isoformat()
        })

    return app


# This creates a ready-to-use app instance
app = create_app()