# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

**Gestión de Botiquines Inteligentes (Smart First Aid Kit Management)**

This is an intelligent medicine inventory management system MVP designed to monitor and manage medications stored in smart first aid kits. The system will eventually integrate with hardware sensors (weight, door opening, infrared) but currently focuses on the software dashboard that processes and displays critical medication information through an intuitive web interface.

### Project Objectives
- Develop a functional, simple, and web-accessible software solution
- Display critical medication information and generate automatic alerts
- Optimize medical inventory control through real-time monitoring
- Provide an intuitive interface requiring minimal technical knowledge

### Target User Profile
- **Primary Role**: First Aid Kit Manager (occupational safety officer, HR representative, or first aid coordinator)
- **Technical Level**: Basic - no advanced technical knowledge required
- **Access**: Simple authentication with username and password
- **Training Required**: Minimal - intuitive interface design

## Architecture

**Backend Structure:**
- `backend/app.py` - Flask application factory with health check endpoint
- `backend/db.py` - Database configuration and SQLAlchemy setup
- `backend/models/models.py` - Medicine model with business logic for status determination
- `backend/routes/medicines.py` - REST API endpoints for medicine CRUD operations
- `backend/seed.py` - Database seeding script with sample data

**Key Components:**
- **Medicine Model**: Core entity with fields for trade_name, generic_name, brand, strength, expiry_date, quantity, reorder_level
- **Status Logic**: Automatic status calculation (OUT_OF_STOCK, EXPIRED, EXPIRES_SOON, EXPIRES_30, LOW_STOCK, OK)
- **Blueprint Architecture**: Modular route organization using Flask blueprints

## Medication Data Structure

### Primary Data Fields
- **Unique ID**: Auto-generated medication identifier
- **Commercial Name**: Brand name (e.g., "Dolex")
- **Generic Name**: Active ingredient (e.g., "Paracetamol")
- **Brand/Laboratory**: Manufacturer information
- **Concentration/Presentation**: Dosage and format (e.g., "500mg", "120ml syrup", "box x10 tablets")
- **Expiration Date**: Product expiry date
- **Batch Number**: Optional, for hardware integration

### Control Data Fields
- **Current Quantity**: Available units
- **Minimum Stock Threshold**: Configurable per medication
- **Last Update Timestamp**: Latest scan/update time
- **Medication Status**: Available/Low Stock/Out of Stock/Expiring Soon/Expired

## Dashboard Specifications

### Main Dashboard View

#### Summary Panel (Top Section)
- Total registered medications
- Active critical alerts count
- Medications with low stock
- Last system update timestamp

#### Critical Information Sections

**1. Critical Alerts (Maximum Priority)**
- 🔴 **Critical**: Out of stock or expired medications
- 🟡 **Preventive**: Low stock or expiring within 30 days
- ℹ️ **Informative**: Medications requiring review

**2. Current Inventory**
- Complete medication list with:
  - Commercial and generic names
  - Available quantity vs. minimum threshold
  - Expiration date
  - Visual status (progress bars or color indicators)
  - Days remaining until expiration

**3. Medications by Status**
- **Available**: Adequate stock and valid
- **Low Stock**: Below minimum threshold
- **Out of Stock**: Quantity = 0
- **Expiring Soon**: Expire within ≤ 30 days
- **Expired**: Past expiration date

### Alert Criteria

**Expiration Alerts:**
- 🔴 **Critical (Red)**: Expired or expiring within ≤ 7 days
- 🟡 **Preventive (Yellow)**: Expiring within 8-30 days
- 🟢 **Normal (Green)**: More than 30 days remaining

**Stock Alerts:**
- **Critical Stock**: Quantity = 0 (out of stock)
- **Low Stock**: Quantity ≤ defined minimum threshold
- **Normal Stock**: Quantity > minimum threshold

## Development Commands

### Docker Development (Recommended)
```bash
# Start the application and database
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Database Operations
```bash
# Seed the database with sample data (run from backend/ directory)
docker-compose exec app python seed.py

# Access database directly
docker-compose exec db mysql -u botuser -p botiquines
# Password: botpass
```

### Local Development (Alternative)
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment
# Create .env file with DATABASE_URL=mysql+pymysql://user:pass@host:port/db

# Run Flask development server
flask run --host=0.0.0.0 --port=5000
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/medicines/` - List all medicines with status
- `POST /api/medicines/` - Create new medicine entry

## Database Configuration

The application uses MySQL with PyMySQL driver. Connection configuration:
- **Docker**: Connects to `db` service on port 3306
- **Local**: Configure via `DATABASE_URL` environment variable
- **Default credentials**: botuser/botpass, database: botiquines

## Environment Variables

- `DATABASE_URL` - MySQL connection string (primary configuration method)
- `FLASK_APP` - Set to `app.py`

## File Structure Notes

- All Python models import the shared `db` instance from `db.py`
- Routes are organized in blueprints under `routes/` directory
- The application uses the factory pattern in `app.py`
- Database models include automatic timestamp tracking and business logic methods

## Technology Stack

### Backend
- **Language**: Python
- **Framework**: Flask (lightweight and fast for MVP)
- **API**: REST for future hardware communication
- **Database**: MySQL with PyMySQL driver (current), PostgreSQL planned for production

### Frontend
- **Technologies**: HTML5, CSS3, JavaScript
- **CSS Framework**: Bootstrap (responsive and modern interface)
- **Charts/Visualization**: Chart.js or similar for basic visualizations

### Deployment
- **Recommended**: DigitalOcean Droplet (fixed cost, simple configuration)
- **Alternative**: AWS Lightsail (AWS ecosystem integration)

## Sprint Planning & Development Timeline

**Project Duration**: September 11 - October 10, 2025 (4 weeks)
**Sprint Structure**: 3 weekly sprints + 1 extended final sprint (9 days with buffer)

### Sprint Overview

#### Sprint 1: Foundation & Backend (COMPLETED)
- ✅ Flask application setup with factory pattern
- ✅ MySQL database configuration and models
- ✅ Medicine CRUD operations
- ✅ Docker containerization
- ✅ Basic API endpoints (/health, /api/medicines/)
- ✅ Database seeding functionality

#### Sprint 2: Frontend Dashboard (Week 2)
- Bootstrap integration and responsive layout
- Main dashboard with summary panel
- Medication inventory display
- Basic status visualization (cards/tables)
- User authentication system

#### Sprint 3: Alert System & Advanced Features (Week 3)
- Alert generation logic (expiration and stock)
- Visual alert indicators (colors, icons, priorities)
- Dashboard filtering by medication status
- Configuration panel for thresholds
- Enhanced medication management interface

#### Sprint 4: Testing, Polish & Deployment (Week 4 + Buffer)
- Comprehensive testing and bug fixes
- UI/UX refinements and polish
- Production deployment setup
- Documentation completion
- User acceptance testing
- Buffer time for unexpected issues

### Team Configuration
**Current Setup**: 1-3 developers
- **Developer 1**: Backend (Flask, Database, Authentication, CRUD)
- **Developer 2**: Frontend (Bootstrap, Dashboard, Visual Alerts)
- **Developer 3** (Optional): DevOps, Testing, Documentation

## MVP Scope

### Included Features
✅ Functional dashboard with critical visualizations
✅ Automatic alert system
✅ Basic inventory management
✅ Single-user authentication
✅ Responsive web interface
✅ Docker containerization

### Future Versions (Not in MVP)
- Hardware integration (sensors communication)
- Multiple users and role management
- Advanced reporting
- Detailed historical tracking
- Email/SMS notifications

## Testing

The project uses standard Python testing patterns (pytest cache directories are in .gitignore). No specific test framework is currently configured in the MVP.
