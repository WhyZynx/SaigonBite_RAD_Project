# SaigonBite Kitchen Module (TV2)

## Run locally (Windows PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Login: <http://localhost:8000/>  
Kitchen Portal: <http://localhost:8000/kitchen/>  
FastAPI Swagger: <http://localhost:8000/docs>

### Temporary shared login

The shared SaigonBite login currently uses these temporary mock accounts:

| Role | Email | Password |
|---|---|---|
| Customer | `customer@saigonbite.local` | `CustomerDemo2026!` |
| Kitchen Staff | `kitchen@saigonbite.local` | `KitchenDemo2026!` |
| Admin | `admin@saigonbite.local` | `AdminDemo2026!` |

The backend maps credentials to roles and destinations; the browser does not select a role. Successful sign-in routes `CUSTOMER` to the temporary Customer placeholder, `KITCHEN_STAFF` to the Kitchen Portal, and `ADMIN` to the temporary Admin placeholder. Customer/Admin interface files are not changed. The separate demo-session endpoint remains available for development, but is not exposed as a button on the shared Login page.

Override credentials with `SAIGONBITE_CUSTOMER_EMAIL`, `SAIGONBITE_CUSTOMER_PASSWORD`, `SAIGONBITE_DEMO_EMAIL`, `SAIGONBITE_DEMO_PASSWORD`, `SAIGONBITE_ADMIN_EMAIL`, and `SAIGONBITE_ADMIN_PASSWORD` before starting Uvicorn. Credentials are checked by FastAPI and are not embedded in frontend JavaScript.

Authentication uses random server-side session IDs stored in process memory and an `HttpOnly`, `SameSite=Lax` cookie named `saigonbite_session`, with an eight-hour lifetime. Logout invalidates the session and expires the cookie. Sessions are lost when the backend restarts. This mock has no user database, password hashing/reset, registration, CSRF token, or multi-process session store and is not production authentication. For HTTPS deployment, set `SAIGONBITE_COOKIE_SECURE=1`; do not use the documented default credentials in production.

Proposed authentication endpoints, responses, and session behavior are documented separately in [AUTHENTICATION_PROPOSAL.md](docs/AUTHENTICATION_PROPOSAL.md) for team review. `API_CONTRACT.md` remains unchanged.

Run tests from `backend` with `python -m pytest -q`.

The order repository is temporary in-memory data and resets when the process restarts. Replace `app/repositories/mock_orders.py` with the MySQL/SQLAlchemy repository once TV3 delivers the database schema and seed data; preserve the repository operations and API response schemas. `GET /api/orders/{id}` is a temporary mock-compatible implementation for TV1's shared detail contract and should be removed when TV1's order service is integrated.
