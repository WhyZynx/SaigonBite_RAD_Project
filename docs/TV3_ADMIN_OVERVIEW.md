# TV3 — Admin Module Overview

## 1. Introduction

This document describes the Admin module implemented by TV3 in the SaigonBite RAD Project.

The Admin module currently focuses on two main functions:

1. Voucher Management
2. Mark as Delivered (Demo)

The Admin portal is available at:

```text
http://localhost:8000/admin/
```

Admin users must sign in through the shared login page. The backend checks the authenticated role and restricts access to the Admin portal and its protected APIs.

## 2. Admin Portal Structure

The current Admin interface contains the following navigation items:

| Navigation | Description |
|---|---|
| Vouchers | Manage promotional vouchers |
| Mark as Delivered | View Kitchen-ready orders and simulate delivery completion |
| Log out | End the current session |

The Admin module does not currently include separate Dashboard, User Management, Hub Management, or Menu Management pages.

## 3. Voucher Management

### 3.1 View Vouchers

Admin can view the voucher list and see the following information:

- Voucher code
- Discount value
- Minimum order value
- Validity period
- Voucher status
- Available actions

The voucher list supports filtering by status and searching by voucher code.

Supported statuses:

| Status | Meaning |
|---|---|
| `ACTIVE` | Voucher is currently active |
| `EXPIRED` | Voucher has passed its end date |
| `ARCHIVED` | Voucher has been archived |

The backend checks voucher expiration when retrieving voucher records. An `ACTIVE` voucher whose end date has passed is changed to `EXPIRED`.

### 3.2 Create Voucher

Admin can create a voucher by entering:

| Field | Description |
|---|---|
| Voucher Code | Unique voucher code |
| Discount Value | Percentage discount or fixed VND discount |
| Minimum Order | Minimum order value required |
| Valid From | Voucher start date |
| Valid Until | Voucher end date |

The backend validates the submitted information:

- Voucher code must contain at least 2 characters and cannot exceed 32 characters.
- Discount percentage must be between 1% and 100%.
- Fixed discount must be a positive amount.
- Minimum order must be zero or greater.
- End date cannot be earlier than start date.
- Duplicate voucher codes are rejected.

New vouchers are created with the `ACTIVE` status.

### 3.3 Edit Voucher

Admin can edit an existing voucher using the update action.

The editable information includes:

- Voucher code
- Discount value
- Minimum order
- Start date
- End date

The backend prevents editing archived vouchers. It also checks for duplicate voucher codes.

### 3.4 Archive Voucher

Admin can archive a voucher that is currently `ACTIVE` or `EXPIRED`.

Archiving changes the voucher status to:

```text
ARCHIVED
```

The system uses soft archiving instead of deleting the voucher record. This preserves historical references to vouchers used by orders.

An already archived voucher cannot be archived again.

### 3.5 Voucher API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/vouchers` | Retrieve vouchers |
| POST | `/api/vouchers` | Create a voucher |
| PUT | `/api/vouchers/{voucher_id}` | Update a voucher |
| PATCH | `/api/vouchers/{voucher_id}/archive` | Archive a voucher |

Optional query parameters for the list endpoint:

| Parameter | Description |
|---|---|
| `status` | Filter by `ALL`, `ACTIVE`, `EXPIRED`, or `ARCHIVED` |
| `search` | Search by voucher code |

Example:

```text
GET /api/vouchers?status=ACTIVE&search=SAIGON
```

### 3.6 Voucher Business Rules and Limitations

- Voucher codes are unique.
- New vouchers are created as `ACTIVE`.
- Expired vouchers are automatically changed to `EXPIRED` when voucher records are retrieved.
- Only `ACTIVE` and `EXPIRED` vouchers can be archived.
- Archived vouchers cannot be edited.
- The current shared database schema does not associate vouchers with individual hubs.
- The `hub` field displayed in the Admin interface is currently a display-only value (`All hubs`). It is not persisted as a hub relationship or used to restrict voucher applicability.

## 4. Mark as Delivered (Demo)

### 4.1 Purpose

The Mark as Delivered page allows Admin to view orders that have completed preparation in the Kitchen and simulate the completion of delivery.

Kitchen Staff handles the order preparation process and updates the order status to `READY`.

Admin can then use the delivery action to change an eligible order to `DELIVERED`.

This is a supporting demonstration function, not a complete real-world delivery-management system.

### 4.2 View Ready Orders

The page retrieves orders whose current status is:

```text
READY
```

The table displays:

- Order ID
- Customer name
- Customer phone
- Hub name
- Delivery address
- Order total
- Current status
- Available action

Orders are retrieved from the shared database. The list can be refreshed to load the latest eligible orders.

### 4.3 Mark Order as Delivered

When Admin confirms the action, the backend:

1. Finds the selected order.
2. Checks that the order exists.
3. Checks that its current status is `READY`.
4. Updates the order status to `DELIVERED`.
5. Adds a record to `order_status_history`.
6. Creates or updates the corresponding Delivery record.
7. Saves the changes to the database.

The Delivery record is updated with:

- `delivered_at`: the time the order is marked as delivered.
- `outcome`: `DELIVERED`.

The operation uses a database transaction and a conditional status update to prevent an order from being delivered twice through competing requests.

### 4.4 Order Status Transition

```text
Kitchen Staff
     |
     v
   READY
     |
     | Admin demo action
     v
 DELIVERED
```

Only orders with the `READY` status can be marked as delivered.

If the order does not exist, the API returns `404`.

If the order is not in `READY` status, the API returns `409`.

### 4.5 Admin Delivery API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/admin/orders/ready` | Retrieve orders with `READY` status |
| PATCH | `/api/admin/orders/{order_id}/deliver` | Mark a READY order as DELIVERED |

Example:

```text
GET /api/admin/orders/ready
```

```text
PATCH /api/admin/orders/101/deliver
```

Successful response example:

```json
{
  "id": 101,
  "previous_status": "READY",
  "status": "DELIVERED",
  "delivered_at": "2026-11-20T10:30:00",
  "message": "Order marked as delivered successfully."
}
```

The timestamp above is an illustrative example, not a fixed value.

## 5. Backend Implementation

The Admin module uses the existing layered backend structure.

```text
Admin Frontend
      |
      v
FastAPI Routers
      |
      v
SQLAlchemy ORM
      |
      v
Shared Database
```

Main implementation files:

| File | Responsibility |
|---|---|
| `frontend/admin/index.html` | Admin page structure |
| `frontend/admin/style.css` | Admin interface styling |
| `frontend/admin/app.js` | Voucher and delivery page interactions |
| `backend/app/routers/vouchers.py` | Voucher API endpoints and validation |
| `backend/app/routers/admin.py` | Ready-order list and delivery simulation |
| `backend/app/repositories/voucher_repository.py` | Voucher database operations |
| `backend/app/models.py` | Shared database models |
| `backend/app/auth.py` | Temporary role-based authentication and sessions |
| `backend/app/main.py` | Application setup and router registration |

## 6. Database Tables Used

The Admin module interacts with the shared project database.

| Table | Usage |
|---|---|
| `vouchers` | Store voucher information and status |
| `orders` | Read READY orders and update order status |
| `order_status_history` | Record the READY-to-DELIVERED transition |
| `customers` | Retrieve customer information for ready orders |
| `hubs` | Retrieve hub information for ready orders |
| `deliveries` | Create or update delivery completion information |

The module uses the shared database models and does not introduce a separate Admin database.

## 7. Relationship with Other Modules

### 7.1 Admin and Kitchen

Kitchen Staff is responsible for preparing orders.

The Kitchen status flow ends at:

```text
PREPARING → READY
```

The Admin demo action can continue the order flow:

```text
READY → DELIVERED
```

Admin does not replace Kitchen's order confirmation or preparation responsibilities.

### 7.2 Admin and Customer

Customer ordering and voucher validation are handled by the Customer module and shared backend.

Admin manages voucher information, while Customer ordering uses the shared voucher data.

The current Customer UI does not submit a voucher code, so the complete voucher application flow is not currently exposed through that UI.

### 7.3 Admin and Manager

The Admin delivery action updates the order status and Delivery record.

Manager Reports read shared database information, including order and delivery data.

The delivery completion action can therefore provide delivery timestamps and outcomes for Manager reporting.

## 8. Current Scope and Limitations

The following items describe the current implementation rather than proposed future features.

| Item | Current Status |
|---|---|
| View vouchers | Implemented |
| Search vouchers | Implemented |
| Filter vouchers by status | Implemented |
| Create vouchers | Implemented |
| Edit vouchers | Implemented |
| Archive vouchers | Implemented |
| Automatic expiration check | Implemented when voucher records are retrieved |
| View Kitchen-ready orders | Implemented |
| Mark READY orders as DELIVERED | Implemented as a demo action |
| Persist delivery completion timestamp | Implemented |
| Real shipper assignment and tracking | Not implemented |
| Hub-specific voucher association | Not supported by the current shared schema |
| Admin user management | Not implemented |
| Hub and menu management | Not implemented |
| Admin dashboard | Not implemented |

## 9. Summary

The TV3 Admin module currently provides two main functions:

1. **Voucher Management:** Admin can view, search, filter, create, edit, and archive vouchers.
2. **Mark as Delivered:** Admin can view orders completed by Kitchen and simulate delivery completion for orders in the `READY` state.

Both functions use the project's shared FastAPI backend and database.

The delivery action is intended for project demonstration and does not represent a complete real-world delivery workflow. The current implementation should be evaluated according to the project's agreed RAD scope.