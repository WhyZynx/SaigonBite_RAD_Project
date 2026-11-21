
# TV3 — Manager Module Overview

## 1. Introduction

This document describes the Manager module in the SaigonBite RAD Project.

The Manager portal is available at:

```text
http://localhost:8000/manager/
```

Manager users sign in through the shared login page. The backend checks the authenticated role before granting access to the Manager portal and its protected report APIs.

## 2. Manager Portal Structure

The Manager sidebar contains the following navigation items:

| Navigation | Current Status | Description |
|---|---|---|
| Dashboard | Coming Soon | Future overview of business performance and key statistics |
| Hub Operations | Coming Soon | Future monitoring and management of hub operations |
| Order History | Coming Soon | Future search and review of historical orders |
| Reports | Implemented | Generate sales, hub workload and delivery performance reports |
| Log out | Implemented | End the current session |

### 2.1 Future Development Pages

Dashboard, Hub Operations and Order History are currently placeholder pages.

Selecting one of these items displays a Coming Soon message.

These placeholder pages:

- Do not call backend APIs.
- Do not modify database records.
- Do not perform actual business operations.
- Are reserved for future development.

### 2.2 Implemented Page

The Reports page is currently functional. It allows Managers to select a report type and date range, generate report data, and review KPIs, charts and detail tables.

## 3. Management Reports

The Reports page currently supports three report types.

### 3.1 Sales Report

Provides sales-related information for the selected date range.

The report includes:

- Total revenue.
- Total orders.
- Average delivery time.
- Daily sales revenue chart.
- Daily sales breakdown table.

Revenue is calculated from orders with the `DELIVERED` status.

### 3.2 Hub Workload Report

Provides an overview of order workload across hubs.

The report includes:

- Hub workload information.
- Total orders.
- Completed orders.
- Orders not delivered.
- Hub workload chart and breakdown table.

The current report includes hubs that have associated orders in the reporting data.

### 3.3 Delivery Performance Report

Provides delivery completion information for the selected date range.

The report includes:

- Completed deliveries.
- Average delivery time.
- Daily delivery performance chart.
- Delivery performance breakdown table.

Some values may be unavailable when the required delivery timestamps are missing.

## 4. Report Filters and Display

Managers must select:

- Start Date
- End Date
- Report Type

The start date cannot be later than the end date.

The Reports page retrieves data from the backend using the selected report type and date range.

The page displays:

- KPI cards.
- A chart.
- A detailed data table.
- A Show All / Show Less option when the table contains more than four rows.

There is no assumption that every report contains data. Empty results are displayed using a No Data Available message.

## 5. API Endpoints

The Manager frontend uses the following report API routes:

| Report Type | Endpoint |
|---|---|
| Sales Report | `GET /api/reports/sales` |
| Hub Workload Report | `GET /api/reports/hub-workload` |
| Delivery Performance Report | `GET /api/reports/delivery` |

The report requests use the query parameters:

| Parameter | Description |
|---|---|
| `start_date` | Beginning of the reporting period |
| `end_date` | End of the reporting period |

Example:

```text
GET /api/reports/sales?start_date=2026-11-01&end_date=2026-11-20
```

The actual report values are retrieved from the shared project database.

## 6. Backend and Frontend Structure

Main Manager frontend files:

| File | Responsibility |
|---|---|
| `frontend/manager/index.html` | Manager page structure |
| `frontend/manager/style.css` | Manager interface styling |
| `frontend/manager/app.js` | Navigation, report requests, charts and tables |

The Manager portal uses the shared FastAPI backend and database. It does not introduce a separate Manager database.

## 7. Relationship with Other Modules

### 7.1 Manager and Admin

Admin can simulate delivery completion for orders with the `READY` status by changing them to `DELIVERED`.

Manager reports read shared order and delivery data. Therefore, delivery records and timestamps created by the Admin demo action can contribute to delivery reporting.

### 7.2 Manager and Kitchen

Kitchen Staff handles order confirmation and preparation, including the transition to `READY`.

Manager can review aggregated operational and delivery information through the available reports.

### 7.3 Manager and Customer

Customer creates orders through the Customer portal. The shared order data can be used by Manager reports according to the report's calculation rules.

## 8. Current Scope and Limitations

| Feature | Current Status |
|---|---|
| Sales Report | Implemented |
| Hub Workload Report | Implemented |
| Delivery Performance Report | Implemented |
| Report date filters | Implemented |
| KPI cards | Implemented |
| Charts | Implemented |
| Detail tables | Implemented |
| Dashboard | Coming Soon |
| Hub Operations | Coming Soon |
| Order History | Coming Soon |
| Real-time hub monitoring | Not implemented |
| Historical order search page | Not implemented |

### 8.1 Future Development Notes

Dashboard, Hub Operations and Order History are currently interface placeholders only.

Their appearance in the sidebar does not mean that the corresponding business functionality or backend APIs have been implemented.

Additional API endpoints, business logic, database operations and testing will be required when these features are developed.

## 9. Summary

The TV3 Manager module currently provides three implemented reports:

1. Sales Report.
2. Hub Workload Report.
3. Delivery Performance Report.

The Manager sidebar also displays three planned pages:

- Dashboard.
- Hub Operations.
- Order History.

These pages currently display Coming Soon messages and are reserved for future development.

The implemented reports use the project's shared FastAPI backend and database.
