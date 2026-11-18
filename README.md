# SaigonBite RAD Project

## Run locally

### Linux / macOS (Bash / Zsh / Fish)

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

- Login: <http://localhost:8000/>
- Customer Portal: <http://localhost:8000/customer/>
- Kitchen Portal: <http://localhost:8000/kitchen/>
- Admin Portal (Manage Vouchers): <http://localhost:8000/admin/>
- Manager Portal (Management Reports): <http://localhost:8000/manager/>
- FastAPI Swagger: <http://localhost:8000/docs>

### Temporary shared login

Authentication uses local demo accounts configured in `backend/app/auth.py` or overridden with environment variables. The server assigns roles and destinations; the browser does not choose a role. Successful sign-in routes `CUSTOMER` to the Customer Portal, `KITCHEN_STAFF` to the Kitchen Portal, `ADMIN` to the Admin Portal, and `MANAGER` to the Manager Portal. The separate demo-session endpoint remains available for development.

Override credentials with `SAIGONBITE_CUSTOMER_EMAIL`, `SAIGONBITE_CUSTOMER_PASSWORD`, `SAIGONBITE_DEMO_EMAIL`, `SAIGONBITE_DEMO_PASSWORD`, `SAIGONBITE_ADMIN_EMAIL`, `SAIGONBITE_ADMIN_PASSWORD`, `SAIGONBITE_MANAGER_EMAIL`, and `SAIGONBITE_MANAGER_PASSWORD` before starting Uvicorn. Credentials are checked by FastAPI and are not embedded in frontend JavaScript.

Authentication uses random server-side session IDs stored in process memory and an `HttpOnly`, `SameSite=Lax` cookie named `saigonbite_session`, with an eight-hour lifetime. Logout invalidates the session and expires the cookie. Sessions are lost when the backend restarts. This mock has no user database, password hashing/reset, registration, CSRF token, or multi-process session store and is not production authentication. For HTTPS deployment, set `SAIGONBITE_COOKIE_SECURE=1` and configure non-demo credentials.

Proposed authentication endpoints, responses, and session behavior are documented in [docs/AUTHENTICATION_PROPOSAL.md](docs/AUTHENTICATION_PROPOSAL.md), and REST API specifications are documented in [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

## Database configuration

Copy `.env.example` to `.env` in the repository root and configure `DB_DRIVER`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME`. The backend also accepts `DATABASE_URL`; URL-encode reserved characters in its username and password. Real `.env` files are ignored by Git. Do not run `database/schema.sql` or `database/seed.sql` during normal startup; the schema script recreates the database.

## Current integration boundaries

- Kitchen queue, decisions, and status transitions use `OrderRepository`; Customer and Kitchen share the database-backed order detail endpoint.
- Voucher and report APIs use SQLAlchemy repositories, while their Admin/Manager frontends are integrated.
- Customer hub/menu reads, order creation, order history, and order detail use SQLAlchemy repositories and the shared database models. Delivery distance (3.5 km) and fee (15,000 VND) are fixed demo values; Customer accounts currently map to demo customer ID 1. Voucher validation is supported by the backend when a code is submitted, but the current Customer UI does not send a voucher code. Admin’s voucher hub label is display-only because the shared schema has no hub association.
- The schema has no separate customer-note or item-options fields. The Customer UI currently appends recipient, phone, and note text to the delivery address; Kitchen receives that address as stored.
- Manager report totals are read from the database, but average preparation/delivery time labels currently use fixed demo values.
- Authentication accounts and sessions remain in-memory demo implementations.

Run automated checks from `backend` with `python -m compileall -q app tests` and `python -m pytest -q`. The intended database-dependent tests use isolated SQLite fixtures; confirm each test result in the current checkout before relying on it.
