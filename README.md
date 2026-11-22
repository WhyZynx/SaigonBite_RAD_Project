# SaigonBite RAD Project

SaigonBite is a Requirement Analysis Development (RAD) project for food ordering and cloud-kitchen operations. It brings the Customer, Kitchen Staff, Administrator, and Manager workflows together in one web application.

## Table of Contents

- [Project Overview](#project-overview)
- [System Requirements](#system-requirements)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Database Configuration](#database-configuration)
- [Running the Application](#running-the-application)
- [Demo Accounts](#demo-accounts)
- [System Modules](#system-modules)
- [Main Workflows](#main-workflows)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Project Team](#project-team)
- [Project Documentation](#project-documentation)
- [License and Academic Use](#license-and-academic-use)

## Project Overview

The system provides four role-based portals:

| Role | Portal | Main implemented functions |
|---|---|---|
| Customer | `/customer/` | Browse hubs and menus, place orders, apply vouchers, view order details and status history, and view Kitchen rejection notifications |
| Kitchen Staff | `/kitchen/` | Filter the order queue by hub and status, confirm or reject orders, and move accepted orders through preparation to ready for pickup |
| Administrator | `/admin/` | Create, edit, list, and archive vouchers; view ready orders and simulate delivery completion |
| Manager | `/manager/` | Generate sales, hub workload, and delivery performance reports |

The backend is a FastAPI layered monolith. Routers handle HTTP requests, SQLAlchemy repositories perform persistence operations, and SQLAlchemy models map to MySQL tables. Delivery and notification flows also use small application services. The browser frontend uses HTML, CSS, and JavaScript and is served by FastAPI; there is no frontend build step.

## System Requirements

- Python 3.10 or newer. The code uses Python 3.10 type syntax; the current `backend/requirements.txt` contains the Python dependencies.
- MySQL Server for application data, plus the MySQL command-line client to initialize the schema and sample data.
- Git to clone the repository.
- A modern browser.
- Node.js is optional and is only needed for the JavaScript syntax checks shown under [Testing](#testing).
- Internet access is needed for normal Customer delivery quotes (public Nominatim and OSRM services) and to load external Bootstrap and Google Fonts assets. Hub map links open Google Maps.

Python package ranges are declared in [`backend/requirements.txt`](backend/requirements.txt). MySQL E2E behavior is not established by the SQLite-backed automated tests.

## Project Structure

```text
SaigonBite_RAD_Project/
├── backend/
│   ├── app/
│   │   ├── routers/          # FastAPI routes for Customer, Kitchen, Admin, and reports
│   │   ├── repositories/     # SQLAlchemy database operations
│   │   ├── models.py         # Shared SQLAlchemy models
│   │   ├── schemas.py        # Request and response schemas
│   │   ├── database.py       # .env and SQLAlchemy connection configuration
│   │   ├── auth.py           # Demo accounts and in-memory sessions
│   │   └── delivery_fee_service.py
│   ├── tests/                # Pytest tests using isolated SQLite fixtures
│   └── requirements.txt
├── database/
│   ├── schema.sql            # Full schema for a fresh/disposable database
│   ├── seed.sql              # Sample records for a fresh database
│   └── migrations/           # Additive migration for existing databases
├── docs/
│   ├── INTEGRATION_ISSUES.md # Integration findings and open verification items
│   └── RAD_REPORT.pdf        # RAD project report
├── frontend/
│   ├── customer/
│   ├── kitchen/
│   ├── admin/
│   ├── manager/
│   └── img/                  # Food image assets used by the Customer portal
├── .env.example
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

Run from the directory where you keep projects:

```bash
git clone https://github.com/WhyZynx/SaigonBite_RAD_Project.git
cd SaigonBite_RAD_Project
```

### 2. Create and activate a Python environment

Run these commands from the repository root.

**Windows PowerShell:**

```powershell
py -3 -m venv backend/.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

If PowerShell blocks activation, use a new terminal with an allowed execution policy or run the commands from Git Bash instead.

**macOS / Linux Bash:**

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

### 3. Create the local environment file

Run from the repository root. The real `.env` is ignored by Git; keep credentials there and never commit it.

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Bash / Git Bash:**

```bash
cp .env.example .env
```

Edit `.env` with the local MySQL connection values. See [Database Configuration](#database-configuration). `backend/app/database.py` loads the repository-root `.env` and also checks `backend/.env` as a fallback.

## Database Configuration

The application reads these `DB_*` settings from `.env`:

| Variable | Example value in `.env.example` | Purpose |
|---|---|---|
| `DB_DRIVER` | `mysql+pymysql` | SQLAlchemy MySQL driver |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | `your_mysql_password` | Local MySQL password; replace the example value |
| `DB_HOST` | `localhost` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `SaigonBiteDB` | Database name |

Alternatively, `DATABASE_URL` can be set; it takes precedence over the individual `DB_*` variables. URL-encode reserved characters in the username or password when placing them in `DATABASE_URL` (for example, `@` becomes `%40`). The separate `DB_PASSWORD` setting is passed through SQLAlchemy's URL builder and does not need manual URL encoding.

Other optional settings are read by the application but are not included in `.env.example`:

- `SAIGONBITE_COOKIE_SECURE=1` marks the session cookie Secure; use it when serving the app over HTTPS. It defaults to `0` for local HTTP development.
- `DELIVERY_DEMO_DISTANCE_KM`, `DELIVERY_DEMO_FEE_VND`, and `DELIVERY_DEMO_SURCHARGE_VND` set the sample values for the Customer's explicit demo-quote option. Their defaults are 3.0 km, 18,000 VND, and 0 VND. They are not used as measured route results.
- Authentication override variables are listed under [Demo Accounts](#demo-accounts).

### Initialize a new or disposable database

The current [`database/schema.sql`](database/schema.sql) creates ten tables, including `notifications`. **It starts with `DROP DATABASE IF EXISTS SaigonBiteDB`; running it deletes the existing `SaigonBiteDB` database and all its data.** Use these commands only for a new or disposable database that you are authorized to recreate.

Run from the repository root in Bash or Git Bash, with the MySQL client on `PATH`:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

Enter the MySQL password at each prompt. The schema must run first; the seed script selects `SaigonBiteDB` and inserts sample data.

If `mysql` is not on `PATH` on Windows, the following Git Bash commands use the default MySQL Server 8.0 installation path. Adjust the path if MySQL is installed elsewhere:

```bash
"/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe" -u root -p < database/schema.sql
"/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe" -u root -p < database/seed.sql
```

To verify the selected database and its tables:

```bash
mysql -u root -p -D SaigonBiteDB -e "SELECT DATABASE(); SHOW TABLES;"
```

With the full executable path, replace `mysql` in the verification command with `"/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"`.

### Existing databases

Do not rerun `schema.sql` or `seed.sql` on a database containing data. The checked-in migration [`database/migrations/20261121_create_notifications.sql`](database/migrations/20261121_create_notifications.sql) is additive and only creates the Notifications table; it contains `USE SaigonBiteDB`. Back up the database, verify the selected target, and confirm that the table is absent before applying it to an existing database. This migration does not reconcile other schema differences and has not been run as part of this README update.

The application does not automatically run SQL scripts or create tables when it starts.

## Running the Application

### Start the backend

The virtual environment must be active, dependencies installed, and MySQL running with the configured database available. Start the server from the `backend/` directory:

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Keep this terminal running. Open a second terminal for tests or other commands. If port 8000 is occupied, choose another port and use that port in the browser URLs.

### Open the portals

FastAPI serves the HTML, CSS, and JavaScript. No separate frontend server or `npm install` is required.

| Page | Local URL |
|---|---|
| Sign-in page | <http://127.0.0.1:8000/> |
| Customer | <http://127.0.0.1:8000/customer/> |
| Kitchen Staff | <http://127.0.0.1:8000/kitchen/> |
| Administrator | <http://127.0.0.1:8000/admin/> |
| Manager | <http://127.0.0.1:8000/manager/> |
| Swagger API documentation | <http://127.0.0.1:8000/docs> |

Sign in at `/`. The authenticated role determines the redirect destination. Direct portal access is also protected by role checks.

## Demo Accounts

The current implementation defines local demo accounts in [`backend/app/auth.py`](backend/app/auth.py). Unless overridden by environment variables, the defaults are:

| Role | Default email | Default password |
|---|---|---|
| Customer | `customer@saigonbite.com` | `password123` |
| Kitchen Staff | `kitchen@saigonbite.com` | `password123` |
| Administrator | `admin@saigonbite.com` | `password123` |
| Manager | `manager@saigonbite.com` | `password123` |

These are source-code demo defaults, not production credentials. The Customer email matches the sample Customer record in `database/seed.sql`; Customer API access also requires exactly one database Customer profile matching the signed-in email. Accounts can be overridden with `SAIGONBITE_CUSTOMER_EMAIL`, `SAIGONBITE_CUSTOMER_EMAILS`, `SAIGONBITE_CUSTOMER_PASSWORD`, `SAIGONBITE_DEMO_EMAIL`, `SAIGONBITE_DEMO_PASSWORD`, `SAIGONBITE_ADMIN_EMAIL`, `SAIGONBITE_ADMIN_PASSWORD`, `SAIGONBITE_MANAGER_EMAIL`, and `SAIGONBITE_MANAGER_PASSWORD`.

Authentication is currently a mock account list with server-side sessions held in process memory. Sessions expire after eight hours and are lost when the backend process restarts.

## System Modules

### Customer

- Browse hubs and available menu items.
- Build a cart, request a delivery quote, and place an order.
- Apply eligible vouchers; the backend recalculates discounts and totals on submission.
- View order details, delivery information, status history, and Kitchen rejection notifications.
- Cancel an order while it is still `PENDING`.

### Kitchen Staff

- View orders by hub and status.
- Confirm a `PENDING` order or reject it with a required reason.
- Move a confirmed order to `PREPARING`, then to `READY`.
- Record each successful status transition in `order_status_history`.
- Rejection triggers a best-effort Customer notification; notification storage failure does not reverse the order rejection.

### Administrator

- List, search, filter, create, update, and archive vouchers.
- View orders that are ready for pickup and use the demo action to mark a ready order as delivered.
- Dashboard, Hubs & Menu, and Users navigation entries are placeholders and do not manage those records.

The delivery action is a demonstration simulation, not a real shipper workflow. It records delivery completion but does not record an actual pickup event.

### Manager

- Generate Sales, Hub Workload, and Delivery Performance reports for a selected date range.
- Dashboard, Hub Operations, and Order History navigation entries are placeholders.

Delivery Performance counts records with `outcome` `DELIVERED` or `LATE` as completed when `delivered_at` exists. `LATE` means the delivery completed after its expected time; it is not a failed delivery. Average Delivery Time is calculated only when both `pickup_at` and `delivered_at` are present and valid, with `delivered_at` not earlier than `pickup_at`.

## Main Workflows

1. **Customer places an order:** sign in, select a hub and items, enter delivery details, optionally apply a voucher, and submit. The backend creates a `PENDING` order and calculates route distance and fees through Nominatim and OSRM.
2. **Kitchen reviews the order:** Kitchen Staff filters the queue and either confirms the pending order or rejects it with a reason. The status and history are stored; a rejection also attempts to create a Customer notification.
3. **Kitchen prepares the order:** a confirmed order moves to `PREPARING`, then `READY` for pickup.
4. **Customer tracks progress:** open order details, tracking, or status history to see the current status and updates. A rejected order includes its reason when available.
5. **Administrator manages vouchers:** create, edit, search, filter, or archive voucher records.
6. **Manager reviews reports:** select a date range and generate sales, hub workload, or delivery performance reports.
7. **Demonstration delivery completion:** an Administrator can mark a ready order as delivered. This is a simulation; there is no separate Shipper portal.

## Testing

The backend tests use isolated SQLite fixtures; they do not write to the configured MySQL database. Run from `backend/`:

```bash
python -m compileall -q app tests
python -m pytest -q
```

For JavaScript syntax checks, run from the repository root (Node.js required):

```bash
node --check frontend/customer/app.js
node --check frontend/kitchen/app.js
node --check frontend/kitchen/login.js
node --check frontend/admin/app.js
node --check frontend/manager/app.js
```

## Troubleshooting

### `mysql` is not recognized

Install the MySQL command-line client or add its `bin` directory to `PATH`. On a default Windows MySQL Server 8.0 install, the Git Bash commands in [Database Configuration](#database-configuration) use `/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe` directly.

### MySQL reports access denied or unknown database

Check the local `.env` values (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME`) and confirm MySQL is running. Do not paste passwords into issue reports. Create a new database using the schema steps only if it is safe to recreate; the schema drops the named database first.

### The backend reports `ModuleNotFoundError: app`

Activate the virtual environment and run Uvicorn from the `backend/` directory using `python -m uvicorn app.main:app --reload --port 8000`.

### A portal returns 404 or redirects to sign-in

Check that the backend started successfully and use the portal URL and port printed for the running server. A portal redirect can also mean the browser has no valid session or is signed in with a different role.

### Orders, reports, or vouchers fail to load

Check the backend terminal and MySQL connection. Confirm that the database schema is initialized and that the relevant sample or application data exists. Do not rerun `schema.sql` on a database with data to troubleshoot an API error.

### Customer delivery quote fails

The normal delivery quote requires network access to Nominatim and OSRM. Check the typed delivery address and hub address; service coverage can vary. The backend calculates the delivery fee as 10,000 VND plus 2,500 VND per kilometer, rounded up to the next 1,000 VND, and adds a 3,000 VND surcharge for routes over 5 km. Routes over 10 km are rejected. The project also includes a demo quote option in the Customer interface, which is sample data and should not be treated as a measured route.

## Project Team

The RAD report lists these team members and use-case responsibilities:

| Member | Student ID | Project responsibility |
|---|---|---|
| Vo Ngoc Thanh Vy | `524H0040` | Customer flows, UC01 Place an Order and UC02 Track an Order |
| Nguyen Ly Bao Tran | `524H0130` | Kitchen flows, UC03 Confirm/Reject Incoming Order and UC04 Prepare Order and Mark Ready |
| Tran Thi Ngoc Nhu | `524H0021` | Admin/Manager flows, UC05 Manage Vouchers and UC06 Produce Management Reports |

All team members contribute to analysis, design, implementation, testing, documentation, and review as described in the RAD report.

## Project Documentation

- [Integration issues and verification status](docs/INTEGRATION_ISSUES.md)
- [RAD project report](docs/RAD_REPORT.pdf)

## License and Academic Use

This repository is an academic RAD project. No separate software license file is included. Ask the project team before reusing or redistributing project materials.
