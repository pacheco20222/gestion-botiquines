from datetime import date, datetime, timedelta
from app import app, db
from models.models import Medicine, User


with app.app_context():
    db.create_all()
    
    # Seed medicines
    if Medicine.query.count() == 0:
        samples = [
            Medicine(trade_name="Paracetamol 500mg", generic_name="Paracetamol", brand="Genfar",
                    strength="500mg", expiry_date=date.today() + timedelta(days=90),
                    quantity=15, reorder_level=5, last_scan_at=datetime.utcnow()),
            Medicine(trade_name="Ibuprofeno 200mg", generic_name="Ibuprofeno", brand="MK",
                     strength="200mg", expiry_date=date.today() + timedelta(days=5),
                     quantity=2, reorder_level=4, last_scan_at=datetime.utcnow()),
            Medicine(trade_name="Gasas estériles", generic_name="Material de curación", brand="3M",
                     strength="10x10cm", expiry_date=date.today() + timedelta(days=200),
                     quantity=0, reorder_level=2, last_scan_at=datetime.utcnow()),
        ]
        db.session.add_all(samples)
        db.session.commit()
        print("✅ Seed cargado: 3 medicamentos de ejemplo")
    else:
        print("ℹ️ Ya existen medicamentos, seed omitido")

    # Seed default user
    if User.query.count() == 0:
        user = User(username="admin")
        user.set_password("admin123")  # hashed automatically
        db.session.add(user)
        db.session.commit()
        print("✅ Usuario por defecto creado: admin / admin123")
    else:
        print("ℹ️ Ya existe al menos un usuario, seed de usuarios omitido")
