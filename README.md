# SaigonBite RAD Project

## 1. Project Overview

SaigonBite is a web-based food ordering and management system developed for the Rapid Application Development (RAD) project.

The project is organized into role-based portals:

| Role | Portal | Main Responsibilities |
|---|---|---|
| Customer | `/customer/` | Browse hubs and menu items, place orders, and view order information |
| Kitchen Staff | `/kitchen/` | View incoming orders, confirm or reject orders, and update preparation status |
| Admin | `/admin/` | Manage vouchers and simulate delivery completion for READY orders |
| Manager | `/manager/` | View sales, hub workload, and delivery reports |

The Admin module is documented in [docs/TV3_ADMIN_OVERVIEW.md](docs/TV3_ADMIN_OVERVIEW.md).

## 2. Technology Stack

- **Backend:** Python, FastAPI
- **Database access:** SQLAlchemy ORM and Repository Pattern
- **Database:** MySQL
- **Frontend:** HTML, CSS, JavaScript
- **API documentation:** FastAPI Swagger UI

## 3. Run the Project Locally

### Linux / macOS (Bash, Zsh, or Fish)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Windows PowerShell

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## 4. Available Portals

After starting the backend, open:

| Page | URL |
|---|---|
| Shared Login | http://localhost:8000/ |
| Customer Portal | http://localhost:8000/customer/ |
| Kitchen Portal | http://localhost:8000/kitchen/ |
| Admin Portal | http://localhost:8000/admin/ |
| Manager Portal | http://localhost:8000/manager/ |
| API Documentation | http://localhost:8000/docs |

Users should sign in through the shared login page. The backend assigns the role and redirects each account to its corresponding portal.

## 5. Demo Authentication

The current project uses temporary mock accounts and in-memory sessions.

Default demo credentials can be configured through environment variables:

- `SAIGONBITE_CUSTOMER_EMAIL`
- `SAIGONBITE_CUSTOMER_PASSWORD`
- `SAIGONBITE_DEMO_EMAIL`
- `SAIGONBITE_DEMO_PASSWORD`
- `SAIGONBITE_ADMIN_EMAIL`
- `SAIGONBITE_ADMIN_PASSWORD`
- `SAIGONBITE_MANAGER_EMAIL`
- `SAIGONBITE_MANAGER_PASSWORD`

The backend validates the credentials and assigns one of the supported roles:

- `CUSTOMER`
- `KITCHEN_STAFF`
- `ADMIN`
- `MANAGER`

The session uses a server-side random session ID stored in process memory and an `HttpOnly`, `SameSite=Lax` cookie named `saigonbite_session`. The session lifetime is eight hours.

**Limitations:** Sessions are cleared when the backend restarts. The current mock authentication does not provide database-backed user accounts, password hashing, password reset, registration, or persistent multi-process sessions. It is intended for local demonstration, not production deployment.

For HTTPS deployment, configure `SAIGONBITE_COOKIE_SECURE=1` and use non-demo credentials.

## 6. Database Configuration

1. Copy `.env.example` to `.env` in the repository root.
2. Configure the database connection using:
   - `DB_DRIVER`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
3. Alternatively, configure `DATABASE_URL`. Reserved characters in the username and password must be URL-encoded.
4. Start the backend from the `backend/` directory.

**Important:** Do not run `database/schema.sql` or `database/seed.sql` during normal application startup. The schema script recreates the database and may overwrite existing data.

Do not commit real `.env` files or database credentials to Git.

## 7. Current Implementation Scope and Limitations

### Customer

- Reads hubs and menu items.
- Creates orders and views order information.
- The current demo implementation maps Customer accounts to customer ID `1`.
- Delivery distance (`3.5 km`) and delivery fee (`15,000 VND`) are fixed demo values.
- The current Customer UI does not submit a voucher code.
- Recipient, phone, and note information are currently included in the delivery address string because the shared schema does not provide separate fields for them.

### Kitchen Staff

- Views orders in the Kitchen queue.
- Filters orders by selected hub and status.
- Confirms or rejects pending orders.
- Updates confirmed orders to `PREPARING` and then `READY`.
- Successful status transitions are recorded in order status history.

### Admin

- Views, searches, and filters vouchers.
- Creates and edits vouchers.
- Archives eligible vouchers.
- Views orders that have reached `READY`.
- Provides a demo action to mark a `READY` order as `DELIVERED`.

The Admin delivery action is a simulation for the project demonstration. It does not represent a complete real-world shipper or delivery-management workflow.

### Manager

- Generates Sales Reports.
- Generates Hub Workload Reports.
- Generates Delivery Performance Reports.
- Selects a start date and end date for each report.
- Views report KPIs, charts, and detail tables.

Report values are calculated from the current database records. Some reports may show `—` when the required delivery timestamps are not available.

## 8. Order Status Flow

The main order preparation flow is:

```text
PENDING
   |
   +----> REJECTED
   |
   v
CONFIRMED
   |
   v
PREPARING
   |
   v
READY
   |
   v
DELIVERED
```

Kitchen Staff handles the order up to `READY`. The current Admin demo action can then change an eligible order from `READY` to `DELIVERED`.

## 9. Run Automated Tests

Run the following commands from the `backend/` directory:

```bash
python -m compileall -q app tests
python -m pytest -q
```

The automated tests include isolated database fixtures. Check the test output in the current checkout before reporting a test result.

JavaScript syntax checks can be run with:

```bash
node --check ../frontend/admin/app.js
node --check ../frontend/manager/app.js
```

## 10. Documentation

| Document | Description |
|---|---|
| `docs/RAD_REPORT.docx` | Original RAD project report |
| `docs/TV3_ADMIN_OVERVIEW.md` | Overview of the implemented Admin module |
| `docs/API_CONTRACT.md` | Shared API contract |

The authentication document describes the current temporary mock authentication behavior and should be read together with the actual backend implementation.

## 11. Project Status

The project contains integrated Customer, Kitchen, Admin, and Manager portals. The current implementation supports the main demonstration flows, but some features remain demo-level or depend on shared integration decisions.

Do not interpret a successful local run or isolated automated test as proof that the complete system has passed end-to-end testing on the shared MySQL database.