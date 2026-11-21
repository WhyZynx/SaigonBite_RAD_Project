# SaigonBite RAD Project

## 1. Project Overview

SaigonBite is a web-based food ordering and management system developed for the Rapid Application Development (RAD) project.

The project is organized into role-based portals:

| Role | Portal | Main Responsibilities |
|---|---|---|
| Customer | `/customer/` | Browse hubs and menu items, place orders, and view order information |
| Kitchen Staff | `/kitchen/` | View incoming orders, confirm or reject orders, and update preparation status |
| Admin | `/admin/` | Manage vouchers, simulate delivery completion, and access planned Dashboard, Hubs & Menu, and Users pages |
| Manager | `/manager/` | Generate management reports and access planned Dashboard, Hub Operations, and Order History pages |

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
- `SAIGONBITE_CUSTOMER_EMAILS`
- `SAIGONBITE_CUSTOMER_PASSWORD`
- `SAIGONBITE_DEMO_EMAIL`
- `SAIGONBITE_DEMO_PASSWORD`
- `SAIGONBITE_ADMIN_EMAIL`
- `SAIGONBITE_ADMIN_PASSWORD`
- `SAIGONBITE_MANAGER_EMAIL`
- `SAIGONBITE_MANAGER_PASSWORD`

The backend validates credentials and assigns one of the supported roles: CUSTOMER, KITCHEN_STAFF, ADMIN, or MANAGER.

## Current integration boundaries

- Kitchen queue, decisions, and status transitions use OrderRepository; Customer and Kitchen share the database-backed order detail endpoint.
- Voucher and report APIs use SQLAlchemy repositories, with integrated Admin and Manager pages for the implemented functions.
- Customer hub/menu reads, order creation, order history, and order detail use SQLAlchemy repositories and the shared database models. The signed-in Customer email must match exactly one Customer profile in the database.
- Customer delivery addresses are geocoded through Nominatim and routed through OSRM. The backend recalculates the route quote and order totals. Admin's voucher hub label is display-only because the shared schema has no voucher-to-hub relationship.
- The schema has no separate recipient, delivery-phone, special-note, or item-options fields. Customer currently stores recipient, phone, note, and address together in the order's delivery_address; Kitchen receives that stored string.
- Admin's demo delivery action creates or updates a Delivery record with
  outcome=DELIVERED and delivered_at. It does not set pickup_at because
  the project does not implement a real Shipper workflow. For Manager
  Delivery Performance reporting, both DELIVERED and LATE count as
  completed deliveries when delivered_at exists. LATE represents a
  successful delivery completed later than expected, not a failed
  delivery. Average Delivery Time is calculated only when both
  pickup_at and delivered_at are valid and delivered_at >= pickup_at;
  otherwise, the record is excluded from the average.



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

- Reads hubs and menu items from the database, creates orders, and views order history and details.
- The signed-in Customer is matched to exactly one database Customer profile by session email; the frontend does not send a fixed Customer ID. The demo login/session mechanism is still in-memory.
- Checkout geocodes the selected Hub and typed delivery address with Nominatim, then requests a driving route from OSRM. The backend calculates the delivery fee as 10,000 VND + 2,500 VND/km, rounded up to the nearest 1,000 VND, and adds a 3,000 VND surcharge for routes over 5 km. Routes over 10 km are rejected. Delivery quotes and final order totals are recalculated by the backend.
- Nominatim and OSRM are public OpenStreetMap services; the current implementation uses no API key. Nominatim requests use an identifying SaigonBite User-Agent, are paced, and successful geocodes are cached. Checkout displays OpenStreetMap attribution. Geocoding may identify a street segment rather than the exact building entrance, depending on OpenStreetMap coverage.
- Customers can load available vouchers, apply a code for a backend-calculated preview, and submit the selected code with the order. The backend validates the voucher and recalculates the final discount and total when creating the order.
- The shared schema has no separate recipient, delivery-phone, or special-note columns. Customer stores these values with the delivery address as labeled text; Order Detail returns that string for Kitchen to parse. The schema also has no item-options field.

### Kitchen Staff

- Views orders in the Kitchen queue.
- Filters orders by selected hub and status.
- Confirms or rejects pending orders.
- Updates confirmed orders to `PREPARING` and then `READY`.
- Successful status transitions are recorded in order status history.

### Admin

**Implemented features:**

- Views, searches, and filters vouchers.
- Creates and edits vouchers.
- Archives eligible vouchers.
- Views orders that have reached `READY`.
- Provides a demo action to mark a `READY` order as `DELIVERED`.

**Future development pages (Coming Soon):**

- Dashboard: Overview of system activities and key statistics.
- Hubs & Menu: Hub and menu management.
- Users: Customer and staff account management.

The three future development pages are currently UI placeholders. They do not call backend APIs or modify database records.

The Admin delivery action is a simulation for the project demonstration. It does not represent a complete real-world shipper or delivery-management workflow.

### Manager

**Implemented features:**

- Generates Sales Reports.
- Generates Hub Workload Reports.
- Generates Delivery Performance Reports.
- Selects a start date and end date for each report.
- Views report KPIs, charts, and detail tables.

**Future development pages (Coming Soon):**

- Dashboard: Overview of business performance and key statistics.
- Hub Operations: Hub monitoring and operational management.
- Order History: Historical order search and review.

The three future development pages are currently UI placeholders. They do not call backend APIs or modify database records.

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
| `docs/TV3_ADMIN_OVERVIEW.md` | Admin implementation and planned future pages |
| `docs/TV3_MANAGER_OVERVIEW.md` | Manager reports and planned future pages |
| `docs/API_CONTRACT.md` | Shared API contract |

The authentication document describes the current temporary mock authentication behavior and should be read together with the actual backend implementation.

## 11. Project Status

The project contains integrated Customer, Kitchen, Admin, and Manager portals. The current implementation supports the main demonstration flows, but some features remain demo-level or depend on shared integration decisions.

Do not interpret a successful local run or isolated automated test as proof that the complete system has passed end-to-end testing on the shared MySQL database.
