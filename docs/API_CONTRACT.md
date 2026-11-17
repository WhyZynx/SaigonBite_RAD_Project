# SaigonBite — REST API Contract, Authentication & Local Setup Guide

**Version:** 1.1 (Updated for TV3 Admin & Manager Implementation) | **Backend:** Python + FastAPI | **Database:** MySQL 8 | **Architecture:** MVC-inspired Layered Monolith + Repository Pattern

> **Status:** UPDATED WITH TV3 DATABASE INTEGRATION (`feature/nhu-admin`). This unified specification consolidates the local setup guide, the 4-role session authentication layer (`CUSTOMER`, `KITCHEN_STAFF`, `ADMIN`, `MANAGER`), TV1/TV2 baseline contracts, and the MySQL-backed TV3 Admin Voucher (`/api/vouchers`) and Manager Report (`/api/reports/*`) endpoints via SQLAlchemy ORM.

---

## 1. Local Setup & Temporary Shared Login

### 1.1 Run Locally

**Linux / macOS (Bash / Zsh / Fish):**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Windows PowerShell:**

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Portal & API URLs:**

- Shared Login: `http://localhost:8000/`
- Kitchen Portal: `http://localhost:8000/kitchen/`
- Admin Portal (Manage Vouchers): `http://localhost:8000/admin/`
- Manager Portal (Management Reports): `http://localhost:8000/manager/`
- FastAPI Swagger UI: `http://localhost:8000/docs`

Run automated tests from `backend` with:

```bash
python -m pytest -q
```

### 1.2 Temporary Shared Mock Accounts

| Role | Email | Password | Destination |
|---|---|---|---|
| Customer | `customer@saigonbite.com` | `password123` | `/customer/` |
| Kitchen Staff | `kitchen@saigonbite.com` | `password123` | `/kitchen/` |
| Admin | `admin@saigonbite.com` | `password123` | `/admin/` |
| Manager | `manager@saigonbite.com` | `password123` | `/manager/` |

Override default credentials via environment variables before starting Uvicorn: `SAIGONBITE_CUSTOMER_EMAIL`, `SAIGONBITE_CUSTOMER_PASSWORD`, `SAIGONBITE_DEMO_EMAIL`, `SAIGONBITE_DEMO_PASSWORD`, `SAIGONBITE_ADMIN_EMAIL`, `SAIGONBITE_ADMIN_PASSWORD`, `SAIGONBITE_MANAGER_EMAIL`, and `SAIGONBITE_MANAGER_PASSWORD`.

---

## 2. Authentication & Session Specification (Temporary Mock)

The backend maps configured mock credentials to one of `CUSTOMER`, `KITCHEN_STAFF`, `ADMIN`, or `MANAGER`. Any `role` property sent by the browser is ignored; the server assigns the role and redirect destination.

### 2.1 Authentication Endpoints

#### `POST /api/auth/login`

**Request:**

```json
{"email": "admin@saigonbite.com", "password": "password123"}
```

**Response 200:**

```json
{"email": "admin@saigonbite.com", "role": "ADMIN", "demo": false, "redirect_url": "/admin/"}
```

Invalid credentials return HTTP `401`.

#### `POST /api/auth/demo`

Creates a `KITCHEN_STAFF` demo session and returns the same identity payload with `"demo": true`.

#### `GET /api/auth/me`

Returns the active session's `email`, `role`, `demo`, and `redirect_url`. Returns HTTP `401` if unauthenticated.

#### `POST /api/auth/logout`

Invalidates the server-side session and expires the `saigonbite_session` cookie.

### 2.2 Session & Access Control Behavior

- Random session tokens are stored in server memory with an 8-hour TTL (`28800` seconds) and issued via an `HttpOnly`, `SameSite=Lax` cookie named `saigonbite_session` (`SAIGONBITE_COOKIE_SECURE=1` enables `Secure` for HTTPS).
- Protected routes enforce strict role isolation:
  - `KITCHEN_STAFF`: `/kitchen`, `/kitchen/`, `/style.css`, `/app.js`, and `/api/kitchen/*`
  - `CUSTOMER`: `/customer` and `/customer/`
  - `ADMIN`: `/admin`, `/admin/`, and `/api/vouchers/*`
  - `MANAGER`: `/manager`, `/manager/`, and `/api/reports/*`
- Missing sessions return HTTP `401` for `/api/*` routes (or `303` redirect to `/` for UI pages). Authenticated users accessing another role's route receive HTTP `403` for `/api/*` routes (or `303` redirect to their own `role_home` destination for UI pages).
- **Production Note:** Replace the in-memory credential/session store with the MySQL user table, password hashing, and persistent session/token policy before production deployment.

---

## 3. REST API Conventions & Inventory

### 3.1 Conventions

- **Base URL (local):** `http://localhost:8000`
- **Format:** All JSON requests use `Content-Type: application/json`; response JSON uses `snake_case` keys (except UI chart/summary display fields explicitly noted in §8).
- **Types:** Identifiers are positive integers; timestamps use ISO 8601 strings; monetary amounts are nonnegative VND integers (or formatted VND display strings in TV3 UI view models).
- **Error format:** `{"detail": "Human-readable error message"}`
- **HTTP status codes:** `200` GET/PATCH/PUT success; `201` POST created; `204` DELETE/archive success; `400` invalid business input; `401` authentication required; `403` forbidden role; `404` missing resource; `409` illegal state transition/conflict; `422` invalid request format; `500` unexpected server failure.
- **Normalized Order Status Codes:** `PENDING`, `CONFIRMED`, `REJECTED`, `PREPARING`, `READY`, `DELIVERED`, `FAILED`, `CANCELLED` (`READY` displays as “Ready for Pickup” in UI).

### 3.2 API Inventory

| UC | Method | Endpoint | Owner | Purpose |
|---|---|---|---|---|
| Auth | POST | `/api/auth/login` | Shared | Authenticate user and set session cookie |
| Auth | POST | `/api/auth/demo` | Shared | Start Kitchen Staff demo preview session |
| Auth | GET | `/api/auth/me` | Shared | Get current authenticated session info |
| Auth | POST | `/api/auth/logout` | Shared | Clear session and expire cookie |
| UC01 | GET | `/api/hubs` | TV1 | List hubs |
| UC01 | GET | `/api/menu-items?hub_id={id}` | TV1 | List menu items for a hub |
| UC01 | POST | `/api/orders` | TV1 | Place order |
| UC02 | GET | `/api/orders/{id}` | TV1 | Get order detail and current status |
| UC02 | GET | `/api/customers/{id}/orders` | TV1 | List customer orders |
| UC03/04 | GET | `/api/kitchen/orders?hub_id={id}` | TV2 | Kitchen order queue |
| UC03 | PATCH | `/api/kitchen/orders/{id}/decision` | TV2 | Confirm/reject incoming order |
| UC04 | PATCH | `/api/kitchen/orders/{id}/status` | TV2 | Start preparation / mark ready |
| UC05 | GET | `/api/vouchers` | TV3 | List, filter, and search vouchers (Admin Portal) |
| UC05 | POST | `/api/vouchers` | TV3 | Create new voucher (Admin Portal) |
| UC05 | PATCH | `/api/vouchers/{id}/archive` | TV3 | Soft-archive an active voucher |
| UC06 | GET | `/api/reports/sales` | TV3 | Daily sales revenue report (Manager Portal) |
| UC06 | GET | `/api/reports/hub-workload` | TV3 | Hub workload distribution report (Manager Portal) |
| UC06 | GET | `/api/reports/delivery` | TV3 | Delivery performance report (Manager Portal) |

---

## 4. Shared Data Shapes (Proposed)

### 4.1 Order Summary

```json
{
  "id": 101,
  "customer_id": 1,
  "hub_id": 1,
  "status": "PENDING",
  "total": 105000,
  "created_at": "2026-11-01T10:30:00+07:00"
}
```

### 4.2 Order Detail

```json
{
  "id": 101,
  "customer_id": 1,
  "hub_id": 1,
  "status": "PENDING",
  "items": [
    {"menu_item_id": 1, "name": "Chicken Rice", "quantity": 2, "unit_price": 50000, "line_total": 100000}
  ],
  "delivery_address": "District 1, HCMC",
  "delivery_distance_km": 3.5,
  "voucher_code": "WELCOME10",
  "payment_method": "COD",
  "payment_status": "UNPAID",
  "subtotal": 100000,
  "delivery_fee": 15000,
  "surcharge": 0,
  "discount": 10000,
  "total": 105000,
  "rejection_reason": null,
  "created_at": "2026-11-01T10:30:00+07:00",
  "status_history": [
    {"status": "PENDING", "changed_at": "2026-11-01T10:30:00+07:00", "note": null}
  ]
}
```

---

## 5. TV1 — Customer APIs (UC01 & UC02)

### 5.1 `GET /api/hubs`

**Response 200:**

```json
[
  {"id": 1, "name": "Hub A", "address": "District 1, HCMC", "accepting_orders": true}
]
```

### 5.2 `GET /api/menu-items?hub_id=1`

Required query: `hub_id`.

**Response 200:**

```json
[
  {"id": 1, "hub_id": 1, "name": "Chicken Rice", "price": 50000, "is_available": true}
]
```

### 5.3 `POST /api/orders`

**Request:**

```json
{
  "customer_id": 1,
  "hub_id": 1,
  "items": [{"menu_item_id": 1, "quantity": 2}],
  "delivery_address": "District 1, HCMC",
  "delivery_distance_km": 3.5,
  "voucher_code": "WELCOME10",
  "payment_method": "COD"
}
```

`voucher_code` is optional; maximum **one** voucher per order.

**Response 201:**

```json
{
  "id": 101,
  "status": "PENDING",
  "subtotal": 100000,
  "delivery_fee": 15000,
  "surcharge": 0,
  "discount": 10000,
  "total": 105000
}
```

**Validation Rules:** Nonempty items, positive quantities, menu availability, hub acceptance/capacity, delivery eligibility, voucher validity, and server-side price calculation. Persist order, order items, and initial status history atomically.

### 5.4 `GET /api/orders/{id}`

**Response 200:** Order detail shape (§4.2) including `status_history`. Returns `404` if not found.

### 5.5 `GET /api/customers/{id}/orders`

**Response 200:** Array of order summaries (§4.1), newest first, with optional `status` filter.

---

## 6. TV2 — Kitchen APIs (UC03 & UC04)

### 6.1 `GET /api/kitchen/orders?hub_id=1&status=PENDING`

Required query: `hub_id`. Optional query: `status` (defaults to kitchen-relevant states `PENDING`, `CONFIRMED`, `PREPARING`, `READY`).

**Response 200:** Array of order summaries (§4.1).

### 6.2 `PATCH /api/kitchen/orders/{id}/decision`

**Request (Confirm):**

```json
{"decision": "CONFIRM"}
```

**Request (Reject):**

```json
{"decision": "REJECT", "reason": "An ingredient is unavailable"}
```

**Response 200:**

```json
{"id": 101, "previous_status": "PENDING", "status": "CONFIRMED", "rejection_reason": null}
```

**Rules:** Only `PENDING` orders can be confirmed/rejected; rejection requires a nonblank reason; invalid/duplicate transitions return `409`; missing order returns `404`.

### 6.3 `PATCH /api/kitchen/orders/{id}/status`

**Request (Start Preparation / Mark Ready):**

```json
{"status": "PREPARING"}
```

```json
{"status": "READY"}
```

**Response 200:**

```json
{"id": 101, "previous_status": "CONFIRMED", "status": "PREPARING"}
```

**Rules:** Only `CONFIRMED → PREPARING` and `PREPARING → READY` transitions are allowed; invalid transitions return `409`.

### 6.4 State Transition Matrix

| Current | Action | Next | UC |
|---|---|---|---|
| `PENDING` | Confirm | `CONFIRMED` | UC03 |
| `PENDING` | Reject + reason | `REJECTED` | UC03 |
| `CONFIRMED` | Start preparing | `PREPARING` | UC04 |
| `PREPARING` | Mark ready | `READY` | UC04 |
| `READY` | Delivered / Failed | `DELIVERED` / `FAILED` | Supporting/demo flow |
| `PENDING` | Cancel | `CANCELLED` | Supporting flow |

---

## 7. TV3 — Admin Voucher APIs (UC05 — Implemented)

Requires an authenticated `ADMIN` session (`401` if unauthenticated, `403` for non-admin roles). Soft-archiving updates status to `ARCHIVED` to preserve historical order references.

### 7.1 `GET /api/vouchers`

**Optional query parameters:**
- `status`: `ALL` (default), `ACTIVE`, `EXPIRED`, or `ARCHIVED`
- `search`: case-insensitive substring match against `code` or `hub`

**Response 200:**

```json
[
  {
    "id": 1,
    "code": "BITEWELCOME",
    "hub": "All hubs",
    "discount": "20%",
    "min_order": "150,000 VND",
    "valid_from": "01 Nov 2026 –",
    "valid_to": "31 Dec 2026",
    "status": "ACTIVE"
  }
]
```

### 7.2 `POST /api/vouchers`

**Request:**

```json
{
  "code": "SAIGON25",
  "hub": "All hubs",
  "discount": "20%",
  "min_order": 150000,
  "start_date": "2026-11-17",
  "end_date": "2026-12-31"
}
```

**Response 201:** Created voucher object (`status` defaults to `"ACTIVE"`).  
**Errors:** `400` if `code` is blank or `end_date < start_date`; `409` if `code` already exists; `422` if payload validation fails.

### 7.3 `PATCH /api/vouchers/{id}/archive`

**Request:** Empty body.  
**Response 200:** Updated voucher object with `"status": "ARCHIVED"`.  
**Errors:** `404` if voucher ID is not found; `400` if voucher status is not `ACTIVE` (e.g., already `EXPIRED` or `ARCHIVED`).

---

## 8. TV3 — Management Reports APIs (UC06 — Implemented)

Requires an authenticated `MANAGER` session (`401` if unauthenticated, `403` for non-manager roles). All three endpoints accept inclusive `start_date=YYYY-MM-DD` and `end_date=YYYY-MM-DD` query parameters (defaulting to `2026-11-01` through `2026-11-15`) and return `400` when `end_date < start_date`.

### 8.1 `GET /api/reports/sales?start_date=2026-11-01&end_date=2026-11-15`

**Response 200:**

```json
{
  "kpis": [
    {"label": "Total Revenue", "value": "428,500,000 VND"},
    {"label": "Total Orders", "value": "3,420"},
    {"label": "Avg. Delivery Time", "value": "24 mins"}
  ],
  "totalSummary": "Total: 428,500,000 VND · 3,420 orders",
  "rows": [
    {
      "label": "01",
      "date": "01 Nov 2026",
      "orders": 192,
      "revenue": 24000000,
      "chartVal": 24.0,
      "delivery": "24 mins"
    }
  ]
}
```

### 8.2 `GET /api/reports/hub-workload?start_date=2026-11-01&end_date=2026-11-15`

**Response 200:**

```json
{
  "kpis": [
    {"label": "Total Hub Orders", "value": "3,420"},
    {"label": "Completed Orders", "value": "3,318"},
    {"label": "Avg. Prep Time", "value": "11 mins"}
  ],
  "totalSummary": "Total: 3,420 orders · 97.0% completion rate",
  "rows": [
    {
      "label": "D1",
      "col1": "District 1 Central Hub",
      "col2": "1,120",
      "col3": "1,092",
      "col4": "28",
      "chartVal": 1120
    }
  ]
}
```

### 8.3 `GET /api/reports/delivery?start_date=2026-11-01&end_date=2026-11-15`

**Response 200:**

```json
{
  "kpis": [
    {"label": "Total Deliveries", "value": "3,318"},
    {"label": "On-Time Rate", "value": "94.6%"},
    {"label": "Avg. Delivery Time", "value": "24 mins"}
  ],
  "totalSummary": "Total: 3,318 deliveries · 94.6% on-time",
  "rows": [
    {
      "label": "01",
      "col1": "01 Nov 2026",
      "col2": "188",
      "col3": "179 (95.2%)",
      "col4": "24 mins",
      "chartVal": 95.2
    }
  ]
}
```

---

## 9. Optional Supporting Endpoints, DB Rules & Checklist

### 9.1 Optional Supporting Endpoints (Require Team Approval)

| Method | Endpoint | Purpose | Proposed Owner |
|---|---|---|---|
| GET | `/api/orders/{id}/history` | Standalone status timeline if not included in order detail | TV1 |
| GET | `/api/vouchers/{id}` | Single voucher details if list data is insufficient | TV3 |
| GET | `/api/health` | Local backend health check | TV2 (foundation) |

### 9.2 Database Dependencies & Integration Rules

- **TV3 Database:** `orders`, `order_items`, `order_status_history`, `menu_items`, `hubs`, `vouchers`, `deliveries`, and supporting tables defined in `database/schema.sql`.
- **Cross-Module Persistence:** Orders created by TV1 (`PENDING`) must appear in TV2 (`GET /api/kitchen/orders`) with the same ID; status updates by TV2 must reflect in TV1 (`GET /api/orders/{id}`). Vouchers and reports managed by TV3 are now directly bound to the shared MySQL 8 database (`SaigonBiteDB`) via SQLAlchemy ORM (replacing `_VOUCHERS_STORE` and static report fixtures), while `mock_orders.py` remains active until TV1/TV2 database repositories are merged.
- **Transaction Boundary:** Every status transition must atomically persist both order status and `order_status_history` within a single transaction.

### 9.3 Team Approval Checklist

- [x] **TV3:** Implemented Admin Voucher APIs (`/api/vouchers`) and Manager Report APIs (`/api/reports/*`) with role-protected routes and Figma-aligned portals.
- [x] **TV3:** Bound voucher and report endpoints to MySQL 8 SQLAlchemy ORM models (`schema.sql` / `seed.sql`).
- [ ] **TV1:** Confirm `POST /api/orders` request/response, hub/menu fields, and UC02 history shape.
- [ ] **TV2:** Confirm kitchen `decision`/`status` bodies and allowed transitions.
- [ ] **All:** Confirm IDs, timestamps, VND representation, error format, and access-control policy before freezing v1.0.