# SaigonBite — REST API Contract

**Version:** 1.0 Draft | **Backend:** Python + FastAPI | **Database:** MySQL 8 | **Architecture:** MVC-inspired Layered Monolith + Repository Pattern

> **Status:** DRAFT FOR TEAM REVIEW. This contract is derived from the SaigonBite RAD report, six use cases, and the project's existing REST API planning table. The 15 endpoints in section 2 are retained from the planning table. Additional payload fields, filters, error codes, and support endpoints are implementation proposals unless explicitly identified as already specified. TV1/TV2/TV3 should approve them before parallel implementation.

## 1. Conventions

- Base URL (local): `http://localhost:8000` (proposed development setting).
- All JSON requests use `Content-Type: application/json`; response JSON uses `snake_case` keys.
- Identifiers are positive integers; timestamps use ISO 8601 strings; monetary amounts are nonnegative VND integers. These are **implementation conventions**, not stated in the case study.
- Response errors (proposed common format): `{"detail": "Human-readable error message"}`.
- HTTP status: `200` GET/PATCH/PUT success; `201` POST created; `204` DELETE/archive success; `400` invalid business input; `404` missing resource; `409` illegal state transition/conflict; `422` invalid request format; `500` unexpected server failure. Auth-related `401/403` only when the team implements authentication/authorization.
- Authentication scheme is **not specified** in the report; do not claim JWT/session is already agreed. In a local demo, role separation must be documented; production authorization is out of scope until agreed.
- Data examples are illustrative, not official fees, voucher discounts, or business thresholds.
- `PENDING`, `CONFIRMED`, `REJECTED`, `PREPARING`, `READY`, `DELIVERED`, `FAILED`, `CANCELLED` are the normalized API/DB codes from the project's order-status planning table. UI may display “Ready for Pickup” for `READY`.

## 2. Baseline API inventory — from existing project REST API planning table

| UC | Method | Endpoint | Owner | Purpose |
|---|---|---|---|---|
| UC01 | GET | `/api/hubs` | TV1 | List hubs |
| UC01 | GET | `/api/menu-items?hub_id={id}` | TV1 | List menu items for a hub |
| UC01 | POST | `/api/orders` | TV1 | Place order |
| UC02 | GET | `/api/orders/{id}` | TV1 | Get order detail and current status |
| UC02 | GET | `/api/customers/{id}/orders` | TV1 | List customer orders |
| UC03/04 | GET | `/api/kitchen/orders?hub_id={id}` | TV2 | Kitchen order queue |
| UC03 | PATCH | `/api/kitchen/orders/{id}/decision` | TV2 | Confirm/reject incoming order |
| UC04 | PATCH | `/api/kitchen/orders/{id}/status` | TV2 | Start preparation / mark ready |
| UC05 | GET | `/api/admin/vouchers` | TV3 | List vouchers |
| UC05 | POST | `/api/admin/vouchers` | TV3 | Create voucher |
| UC05 | PUT | `/api/admin/vouchers/{id}` | TV3 | Update voucher |
| UC05 | DELETE | `/api/admin/vouchers/{id}` | TV3 | Archive voucher (soft delete) |
| UC06 | GET | `/api/reports/sales` | TV3 | Sales report |
| UC06 | GET | `/api/reports/hub-workload` | TV3 | Hub workload report |
| UC06 | GET | `/api/reports/delivery` | TV3 | Delivery report |

**Important:** The report/planning table identifies endpoint names and responsibilities, but it does **not** completely specify the JSON bodies and responses below. Those are proposed contracts designed to implement the documented use cases.

## 3. Shared data shapes (proposed)

### 3.1 Order summary

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

### 3.2 Order detail

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

`payment_status` and other payment-related values must be reconciled with the actual DB schema. The examples do not imply a live payment gateway.

## 4. TV1 — Customer APIs (UC01 and UC02)

### 4.1 `GET /api/hubs`

**Response 200 (proposed):**

```json
[
  {"id": 1, "name": "Hub A", "address": "District 1, HCMC", "accepting_orders": true}
]
```

**Business rule:** Hub availability/capacity must be validated when placing orders. Exact capacity threshold is an unresolved assumption in the report.

### 4.2 `GET /api/menu-items?hub_id=1`

Required query: `hub_id`.

**Response 200 (proposed):**

```json
[
  {"id": 1, "hub_id": 1, "name": "Chicken Rice", "price": 50000, "is_available": true}
]
```

### 4.3 `POST /api/orders`

**Request (from existing planning example):**

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

`voucher_code` is optional (proposed); maximum **one** voucher per order is grounded in the project requirements.

**Response 201 (from planning example):**

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

**Validate:** Nonempty items, positive quantities, menu availability, hub acceptance/capacity, delivery eligibility, voucher validity, price calculated on server. Distance fee formula, maximum distance, hub capacity threshold and voucher limits remain pending clarification. Save order, order items, and initial status history in one transaction.

### 4.4 `GET /api/orders/{id}`

**Response 200:** Order detail shape in §3.2, including `status_history` (proposed shape; UC02 requires tracking/history). **404:** Order not found. Enforce customer ownership if authentication is implemented.

### 4.5 `GET /api/customers/{id}/orders`

**Response 200 (proposed):** Array of order summaries in §3.1, newest first. Optional `status` query filter is proposed, not part of the baseline.

## 5. TV2 — Kitchen APIs (UC03 and UC04)

### 5.1 `GET /api/kitchen/orders?hub_id=1&status=PENDING`

`hub_id` is the baseline query parameter. `status` is a **proposed optional filter**; when omitted, return orders belonging to the hub in the kitchen-relevant states (`PENDING`, `CONFIRMED`, `PREPARING`, `READY`) or agree a different default with the team.

**Response 200 (proposed):** Array of order summaries in §3.1. The Kitchen UI can fetch detail via `GET /api/orders/{id}` (shared TV1 endpoint); do not create a duplicate kitchen detail API unless needed for authorization.

### 5.2 `PATCH /api/kitchen/orders/{id}/decision`

**Request for confirm (proposed):**

```json
{"decision": "CONFIRM"}
```

**Request for reject (proposed):**

```json
{"decision": "REJECT", "reason": "An ingredient is unavailable"}
```

**Response 200 (proposed):**

```json
{"id": 101, "previous_status": "PENDING", "status": "CONFIRMED", "rejection_reason": null}
```

**Rules:** Only `PENDING` can be confirmed/rejected; rejection requires a nonblank reason; duplicate/invalid decision returns `409`; nonexistent order returns `404`. Persist status and `OrderStatusHistory` in the same transaction. Rejection payment/refund effects are **not settled** by the report.

### 5.3 `PATCH /api/kitchen/orders/{id}/status`

**Request to start preparation (proposed):**

```json
{"status": "PREPARING"}
```

**Request to mark ready (proposed):**

```json
{"status": "READY"}
```

**Response 200 (proposed):**

```json
{"id": 101, "previous_status": "CONFIRMED", "status": "PREPARING"}
```

**Rules:** Only `CONFIRMED → PREPARING` and `PREPARING → READY` allowed through this endpoint. Return `409` for skipped/reversed/duplicate transitions. Save status and history atomically. If concurrent updates occur, guard with a transaction and row lock or an equivalent conditional update to prevent conflicting transitions.

### 5.4 State transition matrix

| Current | Action | Next | UC |
|---|---|---|---|
| `PENDING` | Confirm | `CONFIRMED` | UC03 |
| `PENDING` | Reject + reason | `REJECTED` | UC03 |
| `CONFIRMED` | Start preparing | `PREPARING` | UC04 |
| `PREPARING` | Mark ready | `READY` | UC04 |
| `READY` | Delivered / Failed | `DELIVERED` / `FAILED` | Supporting/demo flow, **not** a TV2 endpoint in the baseline |
| `PENDING` | Cancel | `CANCELLED` | Supporting flow; cutoff/actor require confirmation |

All other transitions are rejected unless later approved by the team. `READY` is displayed as “Ready for Pickup” in the UI.

## 6. TV3 — Admin Voucher APIs (UC05)

The report requires creating, viewing/searching, editing and **archiving** vouchers; DELETE must be implemented as soft archive, not a destructive row deletion.

### 6.1 `GET /api/admin/vouchers`

**Proposed optional query:** `search`, `status` (`ACTIVE`, `INACTIVE`, `ARCHIVED`).

**Response 200 (proposed):**

```json
[
  {
    "id": 1,
    "code": "WELCOME10",
    "discount_type": "PERCENT",
    "discount_value": 10,
    "start_at": "2026-11-01T00:00:00+07:00",
    "end_at": "2026-12-01T00:00:00+07:00",
    "is_archived": false
  }
]
```

### 6.2 `POST /api/admin/vouchers`

**Request (proposed):**

```json
{
  "code": "WELCOME10",
  "discount_type": "PERCENT",
  "discount_value": 10,
  "start_at": "2026-11-01T00:00:00+07:00",
  "end_at": "2026-12-01T00:00:00+07:00"
}
```

**Response 201:** Created voucher object with generated `id`.

### 6.3 `PUT /api/admin/vouchers/{id}`

**Request:** Same editable fields as create (full replacement of editable voucher properties). **Response 200:** Updated voucher object. **404:** Not found; **409:** duplicate voucher code. If the DB has different voucher fields, update this contract before coding.

### 6.4 `DELETE /api/admin/vouchers/{id}`

**Response 204:** No body. **Effect:** Set `is_archived = true` or equivalent persisted status; preserve historical voucher usage and order references. **404:** Not found.

**Important unresolved voucher rules:** precise eligibility, usage limits, expiration processing and discount caps must be agreed with TV3 and reconciled to the database design.

## 7. TV3 — Management Reports (UC06)

Report types **sales**, **hub workload**, and **delivery** are grounded in the report. Detailed metrics, aggregation and date filters are **proposed**, because report assumption A-05 leaves them unspecified.

All three endpoints propose optional `from_date=YYYY-MM-DD`, `to_date=YYYY-MM-DD`, and `hub_id` filters. Dates are inclusive, and the team must agree which timestamps and statuses count.

### 7.1 `GET /api/reports/sales?from_date=2026-11-01&to_date=2026-11-30`

**Response 200 (proposed):**

```json
{
  "from_date": "2026-11-01",
  "to_date": "2026-11-30",
  "order_count": 25,
  "gross_sales": 2500000,
  "discount_total": 100000,
  "net_sales": 2400000
}
```

### 7.2 `GET /api/reports/hub-workload?from_date=2026-11-01&to_date=2026-11-30`

**Response 200 (proposed):**

```json
{
  "hubs": [
    {"hub_id": 1, "hub_name": "Hub A", "total_orders": 18, "pending_orders": 2, "preparing_orders": 3, "ready_orders": 1}
  ]
}
```

### 7.3 `GET /api/reports/delivery?from_date=2026-11-01&to_date=2026-11-30`

**Response 200 (proposed):**

```json
{
  "total_deliveries": 20,
  "delivered_count": 18,
  "failed_count": 2,
  "success_rate_percent": 90.0
}
```

Delivery outcomes should be calculated from actual `delivered_at`/`delivery_outcome` (or mapped equivalents) where available; do not fabricate completed deliveries by treating `READY` as `DELIVERED`.

## 8. Optional supporting endpoints — NOT in baseline, require approval

These are only needed if the UI/test/demo cannot use existing routes:

| Method | Endpoint | Purpose | Proposed owner |
|---|---|---|---|
| GET | `/api/orders/{id}/history` | Standalone status timeline if not included in order detail | TV1 |
| GET | `/api/admin/vouchers/{id}` | Single voucher details if list data is insufficient | TV3 |
| GET | `/api/health` | Local backend health check | TV2 (foundation) |

Do not add separate `/confirm`, `/reject`, `/start-preparing`, `/mark-ready` routes **in addition** to the two baseline kitchen PATCH endpoints. Choose one consistent design; this contract retains the original `/decision` and `/status` routes.

## 9. Database dependencies and integration rules

- **TV3 database:** `orders`, `order_items`, `order_status_history`, `menu_items`, `hubs`, `vouchers`, and other report/customer tables as defined in the final ERD/SQL. Actual table and column names must be mapped from the team's SQL; these names are conceptual until verified.
- **TV1:** Creating an order (`PENDING`) must make it visible to TV2 through `GET /api/kitchen/orders` using the **same order ID**.
- **TV2:** Confirm/reject/prepare/ready must update the same persisted order; UC02 must display the new status and history.
- **TV3:** Voucher data used by UC01 and report data generated from actual orders must come from the same MySQL database.
- **Transaction boundary:** On every status transition, write order status and history together; roll back both on error.
- **Demo sequence:** Create voucher (UC05) → place order (UC01) → confirm (UC03) → prepare/ready (UC04) → track (UC02) → view reports (UC06). Delivery report requires separate real/demo delivery-outcome records, not just ready orders.

## 10. Team approval checklist

- [ ] **TV3:** Confirm exact SQL table/column names, foreign keys, voucher columns and seed data.
- [ ] **TV1:** Confirm `POST /api/orders` request/response, hub/menu fields, and UC02 history shape.
- [ ] **TV2:** Confirm kitchen `decision`/`status` bodies and allowed transitions.
- [ ] **TV3:** Confirm voucher `PUT`/archive semantics and report metrics/filters.
- [ ] **All:** Confirm IDs, timestamps, VND representation, error format and access-control approach.
- [ ] **All:** Resolve/report open assumptions for capacity, distance/fees, voucher eligibility, cancellation, payment/refund, and report calculations; do not invent business rules.
- [ ] **All:** Freeze this contract as v1.0 before implementing frontend `fetch()` and FastAPI Pydantic schemas.

## 11. Source alignment

- **RAD SaigonBite report:** UC01–UC06, actors, requirements, order process, class/sequence diagrams, UI design, assumption log and implementation sections.
- **RAD project planning document, §3.4 and §3.5:** order-status codes/transitions and the 15 baseline REST endpoints, plus the `POST /api/orders` sample.
- **Implementation proposals in this document:** complete JSON examples for all other endpoints, response shapes, query filters, standard HTTP error codes, and optional supporting endpoints. These are NOT claims that the report already fixed these details.
