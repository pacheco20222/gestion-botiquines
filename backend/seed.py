from datetime import datetime, timedelta
from db import db
from models.models import Medicine, User
from app import app
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    # Medicines covering all states with realistic names
    medicines = [
        # Expired
        Medicine(
            trade_name="Paracetamol",
            generic_name="Paracetamolum",
            brand="Lab A",
            strength="500mg",
            expiry_date=datetime.utcnow() - timedelta(days=10),
            quantity=10,
            reorder_level=2,
            last_scan_at=datetime.utcnow() - timedelta(days=15)
        ),
        # Expiring Soon (≤7 days)
        Medicine(
            trade_name="Ibuprofeno",
            generic_name="Ibuprofenum",
            brand="Lab B",
            strength="250mg",
            expiry_date=datetime.utcnow() + timedelta(days=5),
            quantity=5,
            reorder_level=2,
            last_scan_at=datetime.utcnow() - timedelta(days=3)
        ),
        # Low stock (quantity ≤ reorder_level, > 0)
        Medicine(
            trade_name="Amoxicilina",
            generic_name="Amoxicillinum",
            brand="Lab C",
            strength="100mg",
            expiry_date=datetime.utcnow() + timedelta(days=200),
            quantity=1,
            reorder_level=3,
            last_scan_at=datetime.utcnow() - timedelta(days=7)
        ),
        # Out of stock (quantity = 0)
        Medicine(
            trade_name="Omeprazol",
            generic_name="Omeprazolum",
            brand="Lab D",
            strength="20mg",
            expiry_date=datetime.utcnow() + timedelta(days=365),
            quantity=0,
            reorder_level=2,
            last_scan_at=datetime.utcnow() - timedelta(days=1)
        ),
        # Normal / OK
        Medicine(
            trade_name="Loratadina",
            generic_name="Loratadinum",
            brand="Lab E",
            strength="10mg",
            expiry_date=datetime.utcnow() + timedelta(days=400),
            quantity=50,
            reorder_level=5,
            last_scan_at=datetime.utcnow()
        ),
    ]

    db.session.add_all(medicines)

    # Demo and extra users
    demo_user = User(
        username="demo",
        password_hash=generate_password_hash("demo123")
    )
    admin_user = User(
        username="admin",
        password_hash=generate_password_hash("admin123")
    )
    user1 = User(
        username="user1",
        password_hash=generate_password_hash("user123")
    )
    db.session.add_all([demo_user, admin_user, user1])

    db.session.commit()

    print("Database seeded with demo medicines and demo user.")