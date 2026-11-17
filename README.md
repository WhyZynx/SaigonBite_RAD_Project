# SaigonBite RAD Project

SaigonBite is a student project for food ordering and kitchen operations. The backend is a layered monolith using FastAPI, SQLAlchemy models, and repositories. Kitchen order reads and status changes use the configured relational database. Authentication and session storage remain local in-memory demo implementations.

## Current integration status

| Area | Current state |
|---|---|
| Kitchen order queue and status filters | SQLAlchemy repository, backed by the configured MySQL database when the app runs |
| Kitchen confirm, reject, prepare, ready | SQLAlchemy transactions; each successful transition records `order_status_history` |
| `GET /api/orders/{id}` | SQLAlchemy-backed shared order detail endpoint, currently used by Kitchen |
| Login accounts and session tokens | Mock/local development accounts and in-memory session storage; not database-backed authentication |
| Customer ordering and tracking | Awaiting TV1 integration |
| Admin vouchers and reports | Awaiting TV3 integration |

## Technology

- Python 3.10+
- FastAPI and SQLAlchemy
- MySQL with PyMySQL for normal application database access
- SQLite in-memory fixtures for automated tests
- HTML, CSS, and JavaScript for the existing frontend

## Install dependencies

From the repository root in PowerShell:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configure the database

Copy `.env.example` to `.env` in the repository root and set the local MySQL connection values:

```dotenv
DB_DRIVER=mysql+pymysql
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=SaigonBiteDB
```

The application loads the repository root `.env` and, as a fallback, `backend/.env`. Keep real credentials in `.env`; Git ignores both locations. `DB_PASSWORD` is passed as a separate SQLAlchemy URL component, so reserved characters are encoded safely.

`DATABASE_URL` is also supported. When setting a full URL, percent-encode reserved characters in the username or password (for example, `@` as `%40`, `:` as `%3A`, and `/` as `%2F`). Prefer the `DB_*` variables when possible. No database password is stored in the source or this README.

The shared database is expected to already have its schema and data initialized. Do not run `database/schema.sql` or `database/seed.sql` as part of app startup; those scripts are not migrations, and the schema script can drop the database.

## Run the backend

With the virtual environment active and `.env` configured, from `backend/`:

```powershell
python -m uvicorn app.main:app --reload
```

Open <http://localhost:8000/> for sign-in, <http://localhost:8000/kitchen/> for the Kitchen UI, and <http://localhost:8000/docs> for the API documentation. The local demo login accounts are defined in `backend/app/auth.py`; they are not production authentication credentials.

## Run tests

From `backend/`:

```powershell
python -m pytest -q
python -m compileall -q app tests
```

Database-dependent tests create isolated in-memory SQLite databases and override `get_db`. They do not connect to or change the team's MySQL database.

## Implemented API routes

- `POST /api/auth/login`, `POST /api/auth/demo`, `GET /api/auth/me`, `POST /api/auth/logout` — local mock authentication and in-memory sessions.
- `GET /api/kitchen/orders?hub_id={id}&status={status}` — database-backed queue; status is optional and can include Kitchen statuses such as `PENDING`, `CONFIRMED`, `PREPARING`, `READY`, or `REJECTED`.
- `PATCH /api/kitchen/orders/{id}/decision` — database-backed confirm or reject; rejection requires a reason.
- `PATCH /api/kitchen/orders/{id}/status` — database-backed preparation and ready transitions.
- `GET /api/orders/{id}` — database-backed shared order detail response currently used by Kitchen. Coordinate any contract changes with TV1.

Customer ordering/tracking and Admin voucher/report endpoints are not integrated. See [docs/API_CONTRACT.md](docs/API_CONTRACT.md) for the broader agreed API contract and routes awaiting implementation.

## Order detail data limits

Order detail returns customer name and phone, delivery address and distance, item names and quantities, price totals, payment fields, status history, and a rejection reason when one is recorded. The current shared schema has no customer note/special instruction field and no per-item options/modifiers relation. The API does not fabricate those values; the Kitchen UI displays its existing fallback text when they are unavailable. Additions to the shared schema require TV1/TV3 agreement and a coordinated database migration.

## Team responsibilities

- **TV1:** Customer ordering and order tracking (UC01–UC02); coordinate on the shared `GET /api/orders/{id}` contract.
- **TV2:** Kitchen workflow (UC03–UC04).
- **TV3:** Admin voucher management and reports (UC05–UC06), plus coordination on shared database models/schema.
