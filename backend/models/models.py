"""
Database models for the MVP.

For Sprint 1 we only need the Medicine model.

Each medicine has:
- Trade name (e.g., "Paracetamol 500mg")
- Generic name (e.g., "Paracetamol")
- Brand/lab (e.g., "Genfar")
- Strength/presentation (e.g., "500mg" or "120ml")
- Expiry date
- Quantity available
- Reorder level (threshold for 'low stock')
- Last scan timestamp
- Created/updated timestamps
"""

from datetime import datetime, date
from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password: str):
        """Hash and store a plain password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    trade_name = db.Column(db.String(120), nullable=False)   # Commercial name
    generic_name = db.Column(db.String(120), nullable=False) # Generic name
    brand = db.Column(db.String(120))                        # Brand or lab
    strength = db.Column(db.String(80))                      # Presentation/strength
    expiry_date = db.Column(db.Date)                         # Expiration date
    quantity = db.Column(db.Integer, default=0, nullable=False)
    reorder_level = db.Column(db.Integer, default=2, nullable=False)
    last_scan_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow, nullable=False
    )

    # --- Helper methods ---

    def days_to_expiry(self):
        """
        Returns the number of days until the medicine expires.
        - Negative value if already expired.
        - None if expiry_date is not set.
        """
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days

    def status(self) -> str:
        """
        Returns a detailed status string for the medicine.
        - "OUT_OF_STOCK" if quantity = 0
        - "EXPIRED" if already expired
        - "EXPIRES_SOON" if expiry_date ≤ 7 days
        - "EXPIRES_30" if expiry_date ≤ 30 days
        - "LOW_STOCK" if quantity ≤ reorder_level
        - Otherwise "OK"
        """
        if self.quantity <= 0:
            return "OUT_OF_STOCK"

        days = self.days_to_expiry()
        if days is not None:
            if days < 0:
                return "EXPIRED"
            if days <= 7:
                return "EXPIRES_SOON"
            if days <= 30:
                return "EXPIRES_30"

        if self.quantity <= self.reorder_level:
            return "LOW_STOCK"

        return "OK"

    def to_dict(self) -> dict:
        """
        Serialize the model to a dictionary (for JSON responses).
        """
        return {
            "id": self.id,
            "trade_name": self.trade_name,
            "generic_name": self.generic_name,
            "brand": self.brand,
            "strength": self.strength,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "quantity": self.quantity,
            "reorder_level": self.reorder_level,
            "last_scan_at": self.last_scan_at.isoformat() if self.last_scan_at else None,
            "status": self.status(),
            "days_to_expiry": self.days_to_expiry(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }