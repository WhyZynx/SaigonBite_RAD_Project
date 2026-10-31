# SaigonBite Kitchen Module (TV2)

## Run locally (Windows PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Kitchen UI: <http://localhost:8000/>  
FastAPI Swagger: <http://localhost:8000/docs>

Run tests from `backend` with `python -m pytest -q`.

The order repository is temporary in-memory data and resets when the process restarts. Replace `app/repositories/mock_orders.py` with the MySQL/SQLAlchemy repository once TV3 delivers the database schema and seed data; preserve the repository operations and API response schemas. `GET /api/orders/{id}` is a temporary mock-compatible implementation for TV1's shared detail contract and should be removed when TV1's order service is integrated.
