"""
Frontend page routes with botiquin support.
Handles dashboard views for multiple first aid kits.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models.models import Medicine, Botiquin, Company, User
from datetime import datetime
from db import db

bp = Blueprint("pages", __name__)

"""
FIXES for Authentication Issues:

1. Fixed pages.py index() route - proper security check
2. Fixed user_routes.py login() route - handle both form and JSON data
"""

@bp.route("/")
def index():
    """Redirect to login or dashboard based on session - FIXED SECURITY"""
    if "user_id" in session:
        # Verify the user still exists and is active
        user = User.query.get(session["user_id"])
        if user and user.active:
            return redirect(url_for("pages.dashboard"))
        else:
            # Clear invalid session
            session.clear()
    
    # Always redirect to login if no valid session
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
    
    # Build comp_map: list of dicts with keys: number, medicine_name, status, quantity
    comp_status = botiquin.get_compartment_status()
    comp_map = {}
    for number, data in comp_status.items():
        comp_map[number] = {
            "number": number,
            "medicine_name": data.get("medicine") if data else None,
            "status": data.get("status") if data else None,
            "quantity": data.get("quantity") if data else None,
        }
    
    # Get medicines list
    medicines = botiquin.medicines
    if status_filter:
        medicines = [m for m in medicines if m.status() == status_filter]
    
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
        summary=summary,
        current_status=status_filter,
        comp_map=comp_map,
        grid_cols=botiquin.compartment_cols
    )


@bp.get("/inventory")
def inventory():
    """
    NEW: Proper inventory view showing all medicines across botiquines
    Compatible with updated inventory.html template
    """
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    
    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("users.login"))
    
    # Get filter parameters
    status_filter = request.args.get("status")
    
    # Get medicines based on user access level
    if user.is_super_admin():
        # Super admin sees all medicines from all companies
        medicines_query = Medicine.query.join(Botiquin).join(Company)
        show_company = True
    else:
        # Company admin sees only their company's medicines
        if not user.company_id:
            return "User not assigned to any company", 403
        medicines_query = Medicine.query.join(Botiquin).filter(
            Botiquin.company_id == user.company_id
        )
        show_company = False
    
    # Apply status filter if provided
    all_medicines = medicines_query.all()
    if status_filter:
        medicines = [m for m in all_medicines if m.status() == status_filter]
    else:
        medicines = all_medicines
    
    # Convert to dict format for template
    medicines_dict = []
    for med in medicines:
        med_data = med.to_dict()
        # Add company info if super admin
        if show_company:
            med_data["company_name"] = med.botiquin.company.name
        medicines_dict.append(med_data)
    
    # Group medicines by company or botiquin
    grouped_data = {}
    if show_company:
        for med in medicines_dict:
            company_name = med.get("company_name", "Unknown Company")
            grouped_data.setdefault(company_name, []).append(med)
    else:
        for med in medicines_dict:
            botiquin_name = med.get("botiquin_name") or med.get("botiquin", {}).get("name") or "Unknown Botiquin"
            grouped_data.setdefault(botiquin_name, []).append(med)
    
    # Build summary statistics
    summary = {
        "total": len(all_medicines),
        "critical": sum(1 for m in all_medicines if m.status() in ["EXPIRED", "OUT_OF_STOCK"]),
        "low_stock": sum(1 for m in all_medicines if m.status() == "LOW_STOCK"),
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return render_template(
        "inventory.html",
        user=user,
        grouped_data=grouped_data,
        summary=summary,
        current_status=status_filter,
        show_company=show_company
    )


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
    
    # NOTE: companies.html template not created yet - will show basic info for now
    return render_template(
        "dashboard.html",  # Use dashboard as fallback until companies.html is created
        user=user,
        summary={"total_companies": len(companies)},
        companies=companies_data,
        show_company=True
    )