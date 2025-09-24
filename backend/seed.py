"""
Updated seed.py for SaaS structure with Company -> Botiquin -> Medicine hierarchy
Based on meeting requirements and new models structure
"""
from datetime import datetime, timedelta
from db import db
from models.models import Company, User, Botiquin, Medicine
from app import app

with app.app_context():
    db.drop_all()
    db.create_all()

    print("Creating SaaS structure with companies, users, botiquines, and medicines...")

    # --- COMPANIES ---
    company1 = Company(
        name="Empresa Demo SA",
        contact_email="admin@empresademo.com",
        contact_phone="+52-999-123-4567",
        active=True
    )
    
    company2 = Company(
        name="Corporativo XYZ",
        contact_email="contacto@xyz.com.mx",
        contact_phone="+52-999-987-6543",
        active=True
    )
    
    db.session.add_all([company1, company2])
    db.session.flush()  # Get IDs without committing

    # --- USERS ---
    # Super admin (manages all companies)
    super_admin = User(
        username="superadmin",
        email="superadmin@system.com",
        user_type="super_admin",
        company_id=None,  # Super admin doesn't belong to specific company
        active=True
    )
    super_admin.set_password("super123")

    # Company admins for company 1
    demo_admin = User(
        username="demo",
        email="demo@empresademo.com",
        user_type="company_admin",
        company_id=company1.id,
        active=True
    )
    demo_admin.set_password("demo123")

    admin_user = User(
        username="admin",
        email="admin@empresademo.com",
        user_type="company_admin",
        company_id=company1.id,
        active=True
    )
    admin_user.set_password("admin123")

    # Company admin for company 2
    xyz_admin = User(
        username="xyzadmin",
        email="admin@xyz.com.mx",
        user_type="company_admin",
        company_id=company2.id,
        active=True
    )
    xyz_admin.set_password("xyz123")

    db.session.add_all([super_admin, demo_admin, admin_user, xyz_admin])
    db.session.flush()

    # --- BOTIQUINES ---
    # Botiquines for Company 1 (Empresa Demo SA)
    botiquin1 = Botiquin(
        hardware_id="BOT001",
        name="Botiquín Principal",
        location="Planta Baja - Recepción",
        company_id=company1.id,
        total_compartments=12,
        compartment_rows=3,
        compartment_cols=4,
        active=True,
        last_sync_at=datetime.utcnow() - timedelta(hours=2)
    )

    botiquin2 = Botiquin(
        hardware_id="BOT002", 
        name="Botiquín Segundo Piso",
        location="Segundo Piso - Área Administrativa",
        company_id=company1.id,
        total_compartments=16,
        compartment_rows=4,
        compartment_cols=4,
        active=True,
        last_sync_at=datetime.utcnow() - timedelta(minutes=30)
    )

    # Botiquin for Company 2 (Corporativo XYZ)
    botiquin3 = Botiquin(
        hardware_id="BOT003",
        name="Botiquín XYZ",
        location="Oficina Principal",
        company_id=company2.id,
        total_compartments=12,
        compartment_rows=3,
        compartment_cols=4,
        active=True,
        last_sync_at=datetime.utcnow() - timedelta(hours=1)
    )

    db.session.add_all([botiquin1, botiquin2, botiquin3])
    db.session.flush()

    # --- MEDICINES ---
    now = datetime.utcnow()
    
    # Medicines for Botiquin 1 (Company 1) - covering all status types
    medicines_bot1 = [
        # EXPIRED - Compartment 1
        Medicine(
            botiquin_id=botiquin1.id,
            compartment_number=1,
            trade_name="Paracetamol",
            generic_name="Paracetamolum",
            brand="Genfar",
            strength="500mg",
            unit_weight=0.5,  # 0.5g per tablet
            current_weight=5.0,  # 10 tablets worth
            quantity=10,
            reorder_level=15,
            max_capacity=50,
            expiry_date=(now - timedelta(days=10)).date(),
            batch_number="LOT001",
            last_scan_at=now - timedelta(hours=3)
        ),
        
        # EXPIRES_SOON - Compartment 2
        Medicine(
            botiquin_id=botiquin1.id,
            compartment_number=2,
            trade_name="Ibuprofeno",
            generic_name="Ibuprofenum", 
            brand="MK",
            strength="400mg",
            unit_weight=0.6,
            current_weight=3.0,  # 5 tablets
            quantity=5,
            reorder_level=8,
            max_capacity=30,
            expiry_date=(now + timedelta(days=5)).date(),
            batch_number="LOT002",
            last_scan_at=now - timedelta(hours=1)
        ),
        
        # OUT_OF_STOCK - Compartment 3
        Medicine(
            botiquin_id=botiquin1.id,
            compartment_number=3,
            trade_name="Amoxicilina",
            generic_name="Amoxicillinum",
            brand="Sandoz",
            strength="500mg",
            unit_weight=0.7,
            current_weight=0.0,  # Empty
            quantity=0,
            reorder_level=10,
            max_capacity=40,
            expiry_date=(now + timedelta(days=200)).date(),
            batch_number="LOT003",
            last_scan_at=now - timedelta(hours=6)
        ),
        
        # LOW_STOCK - Compartment 4
        Medicine(
            botiquin_id=botiquin1.id,
            compartment_number=4,
            trade_name="Omeprazol",
            generic_name="Omeprazolum",
            brand="Pfizer",
            strength="20mg",
            unit_weight=0.4,
            current_weight=0.8,  # 2 capsules
            quantity=2,
            reorder_level=10,
            max_capacity=25,
            expiry_date=(now + timedelta(days=180)).date(),
            batch_number="LOT004",
            last_scan_at=now - timedelta(minutes=45)
        ),
        
        # EXPIRES_30 - Compartment 5
        Medicine(
            botiquin_id=botiquin1.id,
            compartment_number=5,
            trade_name="Loratadina",
            generic_name="Loratadinum",
            brand="Bayer",
            strength="10mg",
            unit_weight=0.3,
            current_weight=3.6,  # 12 tablets
            quantity=12,
            reorder_level=5,
            max_capacity=20,
            expiry_date=(now + timedelta(days=25)).date(),
            batch_number="LOT005",
            last_scan_at=now - timedelta(minutes=15)
        ),
        
        # OK Status - Compartment 6
        Medicine(
            botiquin_id=botiquin1.id,
            compartment_number=6,
            trade_name="Diclofenaco",
            generic_name="Diclofenacum",
            brand="Tecnoquímicas",
            strength="50mg",
            unit_weight=0.5,
            current_weight=10.0,  # 20 tablets
            quantity=20,
            reorder_level=8,
            max_capacity=35,
            expiry_date=(now + timedelta(days=300)).date(),
            batch_number="LOT006",
            last_scan_at=now - timedelta(minutes=5)
        )
    ]

    # Medicines for Botiquin 2 (Company 1)
    medicines_bot2 = [
        Medicine(
            botiquin_id=botiquin2.id,
            compartment_number=1,
            trade_name="Aspirina",
            generic_name="Ácido acetilsalicílico",
            brand="Bayer",
            strength="100mg",
            unit_weight=0.4,
            current_weight=8.0,  # 20 tablets
            quantity=20,
            reorder_level=10,
            max_capacity=50,
            expiry_date=(now + timedelta(days=120)).date(),
            batch_number="ASP001",
            last_scan_at=now - timedelta(minutes=30)
        ),
        
        Medicine(
            botiquin_id=botiquin2.id,
            compartment_number=2,
            trade_name="Salbutamol",
            generic_name="Salbutamolum",
            brand="GlaxoSmithKline",
            strength="100mcg/dosis",
            unit_weight=15.0,  # Inhaler weight
            current_weight=30.0,  # 2 inhalers
            quantity=2,
            reorder_level=1,
            max_capacity=5,
            expiry_date=(now + timedelta(days=400)).date(),
            batch_number="SAL001",
            last_scan_at=now - timedelta(hours=1)
        )
    ]

    # Medicines for Botiquin 3 (Company 2)
    medicines_bot3 = [
        Medicine(
            botiquin_id=botiquin3.id,
            compartment_number=1,
            trade_name="Metformina",
            generic_name="Metforminum",
            brand="Sanofi",
            strength="850mg",
            unit_weight=0.8,
            current_weight=16.0,  # 20 tablets
            quantity=20,
            reorder_level=15,
            max_capacity=60,
            expiry_date=(now + timedelta(days=250)).date(),
            batch_number="MET001",
            last_scan_at=now - timedelta(hours=2)
        )
    ]

    # Add all medicines
    all_medicines = medicines_bot1 + medicines_bot2 + medicines_bot3
    db.session.add_all(all_medicines)

    # Commit all changes
    db.session.commit()

    print("\n=== SEEDING COMPLETE ===")
    print(f"✅ Created {len([company1, company2])} companies")
    print(f"✅ Created {len([super_admin, demo_admin, admin_user, xyz_admin])} users")
    print(f"✅ Created {len([botiquin1, botiquin2, botiquin3])} botiquines")
    print(f"✅ Created {len(all_medicines)} medicines")
    
    print("\n=== LOGIN CREDENTIALS ===")
    print("Super Admin: superadmin / super123")
    print("Demo User (Company 1): demo / demo123") 
    print("Admin User (Company 1): admin / admin123")
    print("XYZ Admin (Company 2): xyzadmin / xyz123")
    
    print("\n=== COMPANIES ===")
    print(f"Company 1: {company1.name} (ID: {company1.id})")
    print(f"Company 2: {company2.name} (ID: {company2.id})")
    
    print("\n=== BOTIQUINES ===")
    print(f"BOT001: {botiquin1.name} -> Company 1")
    print(f"BOT002: {botiquin2.name} -> Company 1")
    print(f"BOT003: {botiquin3.name} -> Company 2")
    
    print("\n=== MEDICINE STATUS COVERAGE ===")
    print("✅ EXPIRED: Paracetamol (expired 10 days ago)")
    print("✅ EXPIRES_SOON: Ibuprofeno (expires in 5 days)")
    print("✅ OUT_OF_STOCK: Amoxicilina (quantity = 0)")
    print("✅ LOW_STOCK: Omeprazol (2 units, reorder at 10)")
    print("✅ EXPIRES_30: Loratadina (expires in 25 days)")
    print("✅ OK: Diclofenaco (20 units, expires in 300 days)")
    
    print("\nReady for hardware integration and testing!")