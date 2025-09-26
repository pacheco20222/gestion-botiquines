# Project: Smart First Aid Kit Management – Architecture & Structure

This document captures the system architecture and repository layout so an AI (or any new team member) can quickly understand how the platform is organized and how its parts interact.

## 1. Overview
- **Goal**: manage smart first-aid kits with medicine inventory, automatic alerting, and a web dashboard for super administrators and company administrators.
- **Primary stack**: Flask (Python) + SQLAlchemy + MySQL; Bootstrap-based Jinja templates on the frontend; Docker for containerization.
- **Key components**:
  - Flask API/server split into domain-specific blueprints.
  - Web dashboard rendered with Jinja, protected by Flask-Login.
- Hardware integration endpoints that ingest whole-kit sensor payloads and update inventory (minimum 4 compartments per kit and unit-weight aware for quantity calculations).
  - Seeding scripts that populate demo data for development.

## 2. Repository Structure
```
gestion-botiquines/
├── backend/
│   ├── app.py                 # Flask factory + LoginManager setup
│   ├── db.py                  # SQLAlchemy configuration & MySQL connection
│   ├── models/
│   │   ├── __init__.py        # Exports models for routes/seed usage
│   │   └── models.py          # ORM models: Company, User, Botiquin, Medicine, HardwareLog
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── botiquines.py      # Botiquin CRUD + compartment visualization
│   │   ├── companies.py       # Company management & metrics
│   │   ├── hardware.py        # Sensor ingestion & hardware logs
│   │   ├── medicines.py       # Medicine CRUD, filters, alert aggregation
│   │   ├── pages.py           # HTML views (dashboard, inventory, assignments)
│   │   └── user_routes.py     # Login/Logout & user API with Flask-Login
│   ├── requirements.txt       # Backend dependencies
│   ├── seed.py                # Demo data seeding (users, companies, botiquines)
│   ├── Dockerfile             # Backend container definition
│   └── ca-certificate.crt     # External SSL certificate (ignored in git)
├── frontend/
│   └── templates/             # Jinja templates (Bootstrap)
│       ├── base.html          # Shared layout with navbar & flash messages
│       ├── login.html         # Authentication form
│       ├── dashboard.html     # Main dashboard with summary cards & kit tiles
│       ├── inventory.html     # Global inventory view
│       ├── botiquin_detail.html
│       ├── assign_botiquines.html
│       └── assign_single.html
├── docker-compose.yml         # Service orchestration (Flask service + volumes)
├── README.md                  # Functional description & quickstart
├── Project.md                 # This architecture guide
├── PROGRESS_LOG.md, WARP.md   # Development history and notes
└── docs/*.docx                # Requirements and sprint reports
```

## 3. Backend

### 3.1 Application Factory (`backend/app.py`)
- Defines `create_app()` to initialize Flask, SQLAlchemy, and the `LoginManager`.
- Registers blueprints: `medicines`, `user_routes`, `pages`, `botiquines`, `hardware`, `companies`.
- Provides `login_manager.user_loader` to look up users by `id`.
- Exposes `/health` for environment checks.

### 3.2 Database Configuration (`backend/db.py`)
- Uses `python-dotenv` to load a local `.env` when running outside Docker.
- `get_database_uri()` prefers the `DATABASE_URL` env var, otherwise falls back to the Docker Compose DSN (`mysql+pymysql://botuser:botpass@db:3306/botiquines`).
- `init_db(app)` binds SQLAlchemy and enables connection health checks (`pool_pre_ping`, `pool_recycle`).

### 3.3 Models (`backend/models/models.py`)
- **Company**: organizations with one-to-many relations to `Botiquin` and `User`.
- **User** (`UserMixin` + `user_type` column): roles `super_admin` and `company_admin`, Flask-Login compatible via `is_active`. Stores password hash, last login, company membership.
- **Botiquin**: physical kit identified by `hardware_id`, location, compartment configuration, and relation to `Medicine`.
- **Medicine**: per-compartment inventory data with unit/current weight, automatic quantity calculation, and status computation (`status()` returns `OUT_OF_STOCK`, `EXPIRED`, `LOW_STOCK`, etc.).
- **HardwareLog**: audit trail of sensor payloads (compartment, weight, errors, raw JSON).

### 3.4 Blueprints & Responsibilities
| Blueprint | Base route(s) | Responsibility |
|-----------|---------------|----------------|
| `pages` | `/`, `/dashboard`, `/inventory`, `/botiquin/<id>`, `/botiquines/assign` | Renders HTML views, dashboards, and forms. Uses `login_required` and `current_user` to tailor data and enforce access. |
| `user_routes` | `/login`, `/logout`, `/api/users`, `/api/profile`, `/api/auth/check` | Authentication via Flask-Login plus REST endpoints to manage users. |
| `medicines` | `/api/medicines` | CRUD for medicines, filtering by botiquin, grouping alerts by status. |
| `botiquines` | `/api/botiquines` | CRUD for kits, validation of compartment layouts, grid visualization helper. |
| `companies` | `/api/companies` | Company CRUD, statistics, linked users/botiquines/alerts. |
| `hardware` | `/api/hardware` | Receives sensor readings, updates inventory, logs payloads, returns alerts. |

Each blueprint encapsulates its validations and returns JSON responses, except `pages` which renders templates.

### 3.5 Authentication & Authorization
- Handled with Flask-Login: `login_user()` in `user_routes.login`, `logout_user()` at `/logout`.
- `LoginManager` redirects unauthenticated users to `/login` whenever `login_required` triggers.
- Roles:
  - **super_admin**: unrestricted access, can assign kits, manage companies and users.
  - **company_admin**: restricted to data scoped to `current_user.company_id`.
- `pages.py` and `companies.py` leverage `current_user` to filter queries and deny cross-company access.

### 3.6 Hardware Integration (`hardware.py`)
- Endpoint `/api/hardware/sensor_data` receives JSON payloads that describe the entire kit state (all compartments reported together) and can update unit weights per compartment.
- Validates `hardware_id` and compartment data, resolves the kit, and updates associated medicines.
- Creates both main and per-compartment `HardwareLog` entries, tracking processing status and errors. Hardware registration enforces a minimum of 4 compartments per unit to match the MVP hardware design while allowing larger configurations later.
- Updates the kit’s `last_sync_at` timestamp and returns result summaries plus alert messages (`critical`, `warning`).

### 3.7 Supporting Scripts
- `seed.py`: drops & recreates tables, then seeds demo data (super admin, two companies, assigned/unassigned kits, sample medicines).
- `seed2.py`: optional additional scenarios (if present).

## 4. Frontend (Jinja Templates)
- **`base.html`**: global layout with navbar, role badge, flash messaging, Bootstrap assets.
- **`login.html`**: POST form to `/login`.
- **`dashboard.html`**: metrics cards, kit tiles with detail/API/assign buttons.
- **`inventory.html`**: grouped inventory table (by company for super admins, by kit for company admins).
- **`botiquin_detail.html`**: compartment-by-compartment breakdown and status filters.
- **`assign_botiquines.html` / `assign_single.html`**: workflows for assigning unowned kits to active companies.
- Templates rely on Bootstrap 5 and Bootstrap Icons, keeping the UI responsive without custom JS.

## 5. Key Data Flows
1. **Authentication**: `user_routes.login` verifies credentials, calls `login_user`, and populates the Flask-Login session. Protected views auto-redirect to `/login` if necessary.
2. **Dashboard**: `pages.dashboard` assembles statistics and kit summaries according to the user role; templates conditionally show assign actions and company badges.
3. **Sensor Ingestion**: Hardware posts to `/api/hardware/sensor_data`; the backend updates medicine quantities, records logs, and emits alert metadata used by the UI.
4. **Alerting & Inventory**: `medicines.py` endpoints deliver filtered inventories and alert groups consumed by inventory/dashboard views.
5. **Kit Assignment**: Super admins view `/botiquines/assign`, listing unassigned kits, and complete assignments through `/botiquin/<id>/assign`.

## 6. Persistence & State
- MySQL via SQLAlchemy; migrations are not yet integrated (database can be recreated with `seed.py`).
- `HardwareLog` preserves raw sensor payloads for debugging/audit.
- `Botiquin.last_sync_at` marks the most recent hardware update.

## 7. Environment & Deployment
- **Dependencies**: declared in `backend/requirements.txt` (Flask, Flask-Login, Flask-SQLAlchemy, PyMySQL, python-dotenv).
- **Environment variables**: `DATABASE_URL` is required; store it in `.env` for local runs and surface it via Docker Compose.
- **Docker Compose**: runs the Flask app (mounting `backend/` and `frontend/`), exposes port `5001` → `5000`, executes `flask run`. Expects a MySQL instance reachable through the configured DSN.
- **Certificates**: `backend/ca-certificate.crt` is added manually for secure DB connections and ignored by git.

## 8. Extension Points
- **Granular authorization**: add custom decorators based on `current_user.is_super_admin()` or future roles.
- **Notifications**: reuse alert logic in `hardware.py` / `medicines.py` to trigger email/SMS workflows.
- **Migrations**: introduce Flask-Migrate (Alembic) to manage schema changes instead of full reseeds.
- **Public API**: extend `botiquines.py`/`medicines.py` with token-based authentication for external integrations.

---
`Project.md` acts as a quick-reference map for the entire architecture, highlighting integration points and where to locate relevant code within the repository.
