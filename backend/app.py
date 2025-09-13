"""
Flask application factory for the MVP.

- Creates the Flask app
- Initializes the database (via db.py)
- Registers blueprints (routes)
"""

from flask import Flask, jsonify
from datetime import datetime

from db import init_db   # our init_db function
from db import db        # the shared SQLAlchemy instance

from routes.medicines import bp as medicines_bp
from routes.user_routes import bp as users_bp


def create_app():
    """
    Application factory: builds and configures the Flask app.
    """
    app = Flask(__name__)

    # 1) Database setup
    init_db(app)

    # 2) Register blueprints
    app.register_blueprint(medicines_bp, url_prefix="/api/medicines")
    app.register_blueprint(users_bp, url_prefix="/api/users")

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