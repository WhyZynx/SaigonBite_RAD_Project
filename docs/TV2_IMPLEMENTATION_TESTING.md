# TV2 Kitchen Implementation and Verification

## Current implementation

Kitchen order operations use the layered backend flow:

```text
FastAPI router → OrderRepository → SQLAlchemy models → MySQL
```

The repository enforces `PENDING → CONFIRMED/REJECTED`, `CONFIRMED → PREPARING`, and `PREPARING → READY`. It writes an `order_status_history` row in the same transaction for each successful transition. Conditional status updates and row locking prevent competing transitions from both succeeding.

The application no longer imports or uses a mock order repository. Authentication remains a local demo implementation with in-memory sessions; the successful API smoke test used `/api/auth/demo` to obtain a Kitchen role session.

## Automated tests

Run from `backend/`:

```powershell
python -m compileall -q app tests
python -m pytest -q
```

Tests use isolated in-memory SQLite databases. They do not change MySQL data.

## Live MySQL/API smoke verification

The latest smoke run connected using the configured local environment, started Uvicorn, verified `/docs` and Kitchen route registration, and exercised list/status filters, confirm, prepare, ready, and reject-with-reason. It created temporary rows with a unique marker and removed those rows after checking status history.

After cleanup, the nine seed table counts remained at the expected values: customers 4, hubs 4, brands 3, menu_items 8, vouchers 5, orders 9, order_items 16, order_status_history 32, and deliveries 4. Seed orders 101–109 retained their original statuses.

## Remaining integration boundaries

- Authentication is still mock/local and is not database-backed.
- The shared order detail API is used by Kitchen; coordinate contract changes with TV1.
- Customer ordering/tracking (TV1) and Admin vouchers/reports (TV3) remain separate integration work.
- Customer note and item options are not present in the shared database schema, so the API does not invent those values.
