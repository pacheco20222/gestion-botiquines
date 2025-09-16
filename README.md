# Gestión de Botiquines Inteligentes

*Smart First Aid Kit Management System - MVP*

## 📋 Project Description

An intelligent medicine inventory management system designed to monitor and manage medications stored in smart first aid kits. This MVP focuses on a web-based dashboard that displays critical medication information and generates automatic alerts to optimize medical inventory control.

The system is designed for occupational safety officers, HR representatives, or first aid coordinators who need to maintain proper medication inventory with minimal technical knowledge required.

## 🎯 Key Features

### ✅ Current Features (Sprint 1 - COMPLETED)
- **Flask Backend**: RESTful API with health check and medicine management
- **MySQL Database**: Robust medication data storage with SQLAlchemy ORM
- **Docker Support**: Containerized application with docker-compose
- **CRUD Operations**: Partial CRUD (Create + List implemented; Update/Delete planned for Sprint 2)
- **User Authentication**: Secure single-user access system
- **Smart Status Logic**: Automatic calculation of medication status
- **Database Seeding**: Sample data for development and testing

### 🚧 Upcoming Features (Sprints 2-4)
- **Bootstrap Dashboard**: Responsive web interface with modern UI
- **Alert System**: Critical, preventive, and informative medication alerts
- **Visual Indicators**: Color-coded status displays and progress bars
- **Inventory Management**: Advanced medication tracking and threshold configuration
- **Production Deployment**: DigitalOcean or setup

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python + Flask
- **Database**: MySQL (current) 
- **Frontend**: HTML5 + CSS3 + JavaScript + Bootstrap
- **Containerization**: Docker + Docker Compose
- **Deployment**: DigitalOcean Droplet (recommended)

### Project Structure
```
gestion-botiquines/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── db.py               # Database configuration
│   ├── models/
│   │   └── models.py       # Medicine model with business logic
│   ├── routes/
│   │   └── medicines.py    # API endpoints
│   ├── seed.py             # Database seeding script
│   └── requirements.txt    # Python dependencies
│   └── Dockerfile
│   └── ca-certificate.crt
├── docker-compose.yml      # Container orchestration            # Application container
├── README.md              # This file
└── WARP.md               # Development guidance
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gestion-botiquines
   ```
   (Note you need to use the ca-certificate.crt provided by Digital Ocean, and place it in /backend)

   “⚠️ Make sure backend/ca-certificate.crt is listed in .gitignore so the certificate is not pushed to version control.”

2. **Start the application**
   ```bash
   # Start all services (database + application)
   docker-compose up -d
   
   # View logs
   docker-compose logs -f app
   ```

3. **Seed the database**
   ```bash
   # Add sample data
   docker-compose exec app python seed.py
   ```

4. **Access the application**
   - Health Check: http://localhost:5000/health
   - API Endpoint: http://localhost:5000/api/medicines/

## 💻 Development

### Docker Commands
```bash
# Start services in background
docker-compose up -d

# View application logs
docker-compose logs -f app

# Stop all services
docker-compose down

# Rebuild containers
docker-compose build

# Access database directly
docker-compose exec db mysql -u botuser -p botiquines
# Password: botpass
```

### Local Development (Alternative)
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
echo "DATABASE_URL=mysql+pymysql://botuser:botpass@localhost:3306/botiquines" > .env

# Run Flask development server
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

## 📊 Data Model

### Medicine Entity
Each medication in the system contains:

**Primary Information:**
- Unique ID (auto-generated)
- Commercial name (e.g., "Dolex")
- Generic name (e.g., "Paracetamol")
- Brand/laboratory
- Concentration/presentation (e.g., "500mg", "120ml syrup")
- Expiration date
- Batch number (optional)

**Control Information:**
- Current quantity (available units)
- Minimum stock threshold (configurable)
- Last update timestamp
- Calculated status (OUT_OF_STOCK, EXPIRED, EXPIRES_SOON, LOW_STOCK, OK)

## 🚨 Alert System (Coming in Sprint 3)

### Alert Categories
- 🔴 **Critical**: Out of stock or expired medications
- 🟡 **Preventive**: Low stock or expiring within 30 days
- ℹ️ **Informative**: Medications requiring review

### Alert Criteria
**Expiration Alerts:**
- Critical: Expired or ≤ 7 days remaining
- Preventive: 8-30 days remaining
- Normal: > 30 days remaining

**Stock Alerts:**
- Critical: Quantity = 0 (out of stock)
- Low: Quantity ≤ minimum threshold
- Normal: Quantity > minimum threshold

### Dashboard Usage Example
Once the dashboard is implemented, users will see:

```
🔴 CRITICAL ALERTS (2)
- Ibuprofeno 200mg: OUT OF STOCK - Last updated: 2 days ago
- Alcohol antiséptico: EXPIRED - Expired on: 15/09/2025

🟡 PREVENTIVE ALERTS (1)  
- Paracetamol 500mg: LOW STOCK (2 of 10 tablets) - Expires: 10/12/2025

✅ NORMAL MEDICATIONS (8)
- Sterile gauze: 15 units - Expires: 20/03/2026
- Elastic bandages: 5 rolls - Expires: 15/01/2026
```

## 📅 Development Timeline

**Project Duration**: September 11 - October 10, 2025 (4 weeks)

### Sprint 1: Foundation & Backend ✅ COMPLETED
- Flask application with factory pattern
- MySQL database and models
- Partial CRUD operations for medicines (Create + List; Update/Delete planned for Sprint 2)
- Docker containerization
- API endpoints (/health, /api/medicines/)
- Database seeding functionality

### Sprint 2: Frontend Dashboard (Week 2)
- Bootstrap integration and responsive design
- Main dashboard with summary panel
- Medication inventory display
- Basic status visualization
- User authentication system

### Sprint 3: Alert System & Advanced Features (Week 3)
- Alert generation logic
- Visual alert indicators
- Dashboard filtering capabilities
- Configuration panel for thresholds
- Enhanced medication management

### Sprint 4: Testing, Polish & Deployment (Week 4 + Buffer)
- Comprehensive testing and bug fixes
- UI/UX refinements
- Production deployment
- Documentation completion
- User acceptance testing

## 🎯 MVP Scope

### ✅ Included in MVP
- Functional web dashboard with critical visualizations
- Automatic alert system for expiration and stock
- Basic medication inventory management
- Single-user authentication
- Responsive web interface
- Docker containerization

### 🚫 Not Included (Future Versions)
- Hardware sensor integration
- Multiple users and role management
- Advanced reporting and analytics
- Detailed historical tracking
- Email/SMS notifications
- Mobile applications

## 📧 API Documentation

### Current Endpoints
```
GET  /health           # Health check
GET  /api/medicines/   # List all medicines
POST /api/medicines/   # Create new medicine
POST /api/users/register # Register User
POST /api/users/login # Login to account
```

### Example API Response
```json
[
  {
    "id": 1,
    "trade_name": "Dolex",
    "generic_name": "Paracetamol",
    "brand": "Genfar",
    "strength": "500mg",
    "expiry_date": "2025-12-31",
    "quantity": 20,
    "reorder_level": 5,
    "status": "OK",
    "days_to_expiry": 108
  }
]
```

## 🤝 Contributing

This is an MVP project following agile methodology with weekly sprints. Current development is focused on completing the planned sprint deliverables.

### Team Structure
- **Developer 1**: Backend (Flask, Database, Authentication)
- **Developer 2**: Frontend (Bootstrap, Dashboard, Alerts) 
- **Developer 3**: DevOps, Testing, Documentation (optional)

## 📄 License

*License information to be added*

## 📞 Support

For development guidance and technical details, see [`WARP.md`](WARP.md).

---

**Status**: Sprint 1 Completed ✅ | Sprint 2 Pending 🚧
**Last Updated**: September 13, 2025
