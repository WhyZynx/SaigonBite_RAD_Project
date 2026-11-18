# SaigonBite Kitchen, Admin & Manager Modules

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
- Kitchen Portal: <http://localhost:8000/kitchen/>
- Admin Portal (Manage Vouchers): <http://localhost:8000/admin/>
- Manager Portal (Management Reports): <http://localhost:8000/manager/>
- FastAPI Swagger: <http://localhost:8000/docs>

### Temporary shared login

The shared SaigonBite login currently uses these temporary mock accounts:

| Role | Email | Password | Destination |
|---|---|---|---|
| Customer | `customer@saigonbite.com` | `password123` | `/customer/` |
| Kitchen Staff | `kitchen@saigonbite.com` | `password123` | `/kitchen/` |
| Admin | `admin@saigonbite.com` | `password123` | `/admin/` |
| Manager | `manager@saigonbite.com` | `password123` | `/manager/` |

The backend maps credentials to roles and destinations; the browser does not select a role. Successful sign-in routes `CUSTOMER` to the temporary Customer placeholder, `KITCHEN_STAFF` to the Kitchen Portal, `ADMIN` to the Admin Portal, and `MANAGER` to the Manager Portal. The separate demo-session endpoint remains available for development, but is not exposed as a button on the shared Login page.

Override credentials with `SAIGONBITE_CUSTOMER_EMAIL`, `SAIGONBITE_CUSTOMER_PASSWORD`, `SAIGONBITE_DEMO_EMAIL`, `SAIGONBITE_DEMO_PASSWORD`, `SAIGONBITE_ADMIN_EMAIL`, `SAIGONBITE_ADMIN_PASSWORD`, `SAIGONBITE_MANAGER_EMAIL`, and `SAIGONBITE_MANAGER_PASSWORD` before starting Uvicorn. Credentials are checked by FastAPI and are not embedded in frontend JavaScript.

Authentication uses random server-side session IDs stored in process memory and an `HttpOnly`, `SameSite=Lax` cookie named `saigonbite_session`, with an eight-hour lifetime. Logout invalidates the session and expires the cookie. Sessions are lost when the backend restarts. This mock has no user database, password hashing/reset, registration, CSRF token, or multi-process session store and is not production authentication. For HTTPS deployment, set `SAIGONBITE_COOKIE_SECURE=1`; do not use the documented default credentials in production.

Proposed authentication endpoints, responses, and session behavior are documented in [docs/AUTHENTICATION_PROPOSAL.md](docs/AUTHENTICATION_PROPOSAL.md), and REST API specifications are documented in [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

Run tests from `backend` with `python -m pytest -q`.

The order, voucher, and report repositories currently use temporary in-memory data and reset when the process restarts. Replace `app/repositories/mock_orders.py` and the in-memory stores in `app/routers/vouchers.py` and `app/routers/reports.py` with MySQL/SQLAlchemy repositories once the database schema and seed data are integrated; preserve the repository operations and API response schemas. `GET /api/orders/{id}` is a temporary mock-compatible implementation for TV1's shared detail contract and should be removed when TV1's order service is integrated.