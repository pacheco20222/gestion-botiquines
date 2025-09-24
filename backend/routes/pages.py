"""
Frontend page routes with botiquin support.
Handles dashboard views for multiple first aid kits.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session
from models.models import Medicine, Botiquin, Company, User
from datetime import datetime
from db import db

bp = Blueprint("pages", __name__)

@bp.route("/")
def index():
    """Redirect to login or dashboard based on session"""
    if "user_id" in session:
        return redirect(url_for("pages.dashboard"))
    return redirect(url_for("users.login"))


@bp.get("/dashboard")
def dashboard():
    """
    Main dashboard showing all botiquines for the user's company.
    Super admin sees all botiquines from all companies.
    """
    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    
    # Get user and determine access level
    user = User.query.get(session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("users.login"))
    
    # Get botiquines based on user type
    if user.is_super_admin():
        # Super admin sees all
        botiquines = Botiquin.query.filter_by(active=True).all()
        companies = Company.query.filter_by(active=True).all()
        show_company = True
    else:
        # Company admin sees only their company's botiquines
        if not user.company_id:
            return "User not assigned to any company", 403
        botiquines = Botiquin.query.filter_by(
            company_id=user.company_id, 
            active=True
        ).all()
        companies = [user.company]
        show_company = False
    
    # Collect statistics
    total_medicines = 0
    critical_count = 0
    warning_count = 0
    
    botiquines_data = []
    for bot in botiquines:
        medicines = bot.medicines
        bot_critical = sum(1 for m in medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"])
        bot_warning = sum(1 for m in medicines if m.status() in ["EXPIRES_SOON", "LOW_STOCK"])
        
        total_medicines += len(medicines)
        critical_count += bot_critical
        warning_count += bot_warning
        
        botiquines_data.append({
            "id": bot.id,
            "name": bot.name,
            "location": bot.location,
            "company": bot.company.name if show_company else None,
            "medicines_count": len(medicines),
            "critical": bot_critical,
            "warning": bot_warning,
            "compartments_used": sum(1 for m in medicines if m.compartment_number),
            "compartments_total": bot.total_compartments,
            "last_sync": bot.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if bot.last_sync_at else "Never"
        })
    
    summary = {
        "total_botiquines": len(botiquines),
        "total_medicines": total_medicines,
        "critical": critical_count,
        "warning": warning_count,
        "companies": len(companies) if show_company else None
    }
    
    return render_template(
        "dashboard.html",
        user=user,
        summary=summary,
        botiquines=botiquines_data,
        show_company=show_company
    )


@bp.get("/botiquin/<int:botiquin_id>")
def botiquin_detail(botiquin_id):
    """Detailed view of a specific botiquin with compartment visualization"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    
    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("users.login"))
    
    botiquin = Botiquin.query.get(botiquin_id)
    if not botiquin:
        return "Botiquin not found", 404
    
    # Check access permissions
    if not user.is_super_admin() and botiquin.company_id != user.company_id:
        return "Access denied", 403
    
    # Get filter parameters
    status_filter = request.args.get("status")
    
    # Build compartment grid
    grid = []
    compartment_map = {}
    
    # Map medicines to compartments
    for medicine in botiquin.medicines:
        if medicine.compartment_number:
            compartment_map[medicine.compartment_number] = medicine
    
    # Build visual grid
    compartment_num = 1
    for row in range(botiquin.compartment_rows):
        grid_row = []
        for col in range(botiquin.compartment_cols):
            if compartment_num <= botiquin.total_compartments:
                medicine = compartment_map.get(compartment_num)
                grid_row.append({
                    "number": compartment_num,
                    "medicine": medicine.to_dict() if medicine else None,
                    "occupied": medicine is not None
                })
            else:
                grid_row.append(None)
            compartment_num += 1
        grid.append(grid_row)
    
    # Get medicines list
    medicines = botiquin.medicines
    if status_filter:
        medicines = [m for m in medicines if m.status() == status_filter]
    
    medicines_dict = [m.to_dict() for m in medicines]
    
    # Build summary
    all_medicines = botiquin.medicines
    summary = {
        "total": len(all_medicines),
        "critical": sum(1 for m in all_medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"]),
        "warning": sum(1 for m in all_medicines if m.status() in ["EXPIRES_SOON", "LOW_STOCK"]),
        "ok": sum(1 for m in all_medicines if m.status() == "OK"),
        "compartments_used": sum(1 for m in all_medicines if m.compartment_number),
        "compartments_free": botiquin.total_compartments - sum(1 for m in all_medicines if m.compartment_number),
        "last_sync": botiquin.last_sync_at.strftime("%Y-%m-%d %H:%M:%S") if botiquin.last_sync_at else "Never"
    }
    
    return render_template(
        "botiquin_detail.html",
        user=user,
        botiquin=botiquin,
        grid=grid,
        medicines=medicines_dict,
        summary=summary,
        current_status=status_filter
    )


@bp.get("/inventory")
def inventory():
    """Legacy route - redirects to dashboard"""
    return redirect(url_for("pages.dashboard"))


@bp.get("/companies")
def companies():
    """Company management view (super admin only)"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    
    user = User.query.get(session["user_id"])
    if not user or not user.is_super_admin():
        return "Access denied", 403
    
    companies = Company.query.all()
    companies_data = []
    
    for company in companies:
        companies_data.append({
            "id": company.id,
            "name": company.name,
            "email": company.contact_email,
            "phone": company.contact_phone,
            "active": company.active,
            "botiquines_count": len(company.botiquines),
            "users_count": len(company.users),
            "created": company.created_at.strftime("%Y-%m-%d")
        })
    
    return render_template(
        "companies.html",
        user=user,
        companies=companies_data
    )