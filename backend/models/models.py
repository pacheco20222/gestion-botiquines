from db import db


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    trade_name = db.Column(db.String(120), nullable=False)
    generic_name = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120), nullable=True)
    strength = db.Column(db.String(64), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=0)
    last_scan_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Medicine {self.trade_name} ({self.generic_name})>"
