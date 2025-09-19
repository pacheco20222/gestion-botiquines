from datetime import datetime, timedelta
from db import db
from models.models import Medicine, User
from app import app
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    # Medicines covering all states
    medicines = [
        # Expired
        Medicine(
            trade_name="ExpiredMed",
            generic_name="GenExpired",
            brand="Lab A",
            strength="500mg",
            expiry_date=datetime.utcnow() - timedelta(days=10),
            quantity=10,
            reorder_level=2,
            last_scan_at=datetime.utcnow()
        ),
        # Expiring Soon (≤7 days)
        Medicine(
            trade_name="SoonMed",
            generic_name="GenSoon",
            brand="Lab B",
            strength="250mg",
            expiry_date=datetime.utcnow() + timedelta(days=5),
            quantity=5,
            reorder_level=2,
            last_scan_at=datetime.utcnow()
        ),
        # Low stock (quantity ≤ reorder_level, > 0)
        Medicine(
            trade_name="LowStockMed",
            generic_name="GenLow",
            brand="Lab C",
            strength="100mg",
            expiry_date=datetime.utcnow() + timedelta(days=200),
            quantity=1,
            reorder_level=3,
            last_scan_at=datetime.utcnow()
        ),
        # Out of stock (quantity = 0)
        Medicine(
            trade_name="OutMed",
            generic_name="GenOut",
            brand="Lab D",
            strength="50mg",
            expiry_date=datetime.utcnow() + timedelta(days=365),
            quantity=0,
            reorder_level=2,
            last_scan_at=datetime.utcnow()
        ),
        # Normal / OK
        Medicine(
            trade_name="OkMed",
            generic_name="GenOk",
            brand="Lab E",
            strength="20mg",
            expiry_date=datetime.utcnow() + timedelta(days=400),
            quantity=50,
            reorder_level=5,
            last_scan_at=datetime.utcnow()
        ),
    ]

    db.session.add_all(medicines)

    # Demo user
    demo_user = User(
        username="demo",
        password_hash=generate_password_hash("demo123")
    )
    db.session.add(demo_user)

    db.session.commit()

    print("Database seeded with demo medicines and demo user.")