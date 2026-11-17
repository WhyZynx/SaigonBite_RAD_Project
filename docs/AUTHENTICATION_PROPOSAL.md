# SaigonBite Authentication Proposal (Temporary Mock)

**Status:** Implementation proposal for team review. This file documents the active 4-role local authentication and route protection layer (`CUSTOMER`, `KITCHEN_STAFF`, `ADMIN`, `MANAGER`) and is separate from `API_CONTRACT.md`.

## Mock roles and routing

The backend currently maps configured mock credentials to one of `CUSTOMER`, `KITCHEN_STAFF`, `ADMIN`, or `MANAGER`. The submitted login request contains only `email` and `password`; any client-supplied role is ignored. The server returns the authenticated role and its fixed destination:

| Role | Destination | Interface Status |
|---|---|---|
| `CUSTOMER` | `/customer/` | Temporary Customer placeholder |
| `KITCHEN_STAFF` | `/kitchen/` | Kitchen Portal |
| `ADMIN` | `/admin/` | Admin Portal (Manage Vouchers) |
| `MANAGER` | `/manager/` | Manager Portal (Management Reports) |

## Proposed authentication endpoints

These routes are implemented for the local demo and need team approval before being treated as a shared contract.

### `POST /api/auth/login`

Request:

```json
{"email":"admin@saigonbite.com","password":"password123"}
```

Success response:

```json
{"email":"admin@saigonbite.com","role":"ADMIN","demo":false,"redirect_url":"/admin/"}
```

Invalid credentials return HTTP 401. The server chooses the role from its account mapping; a `role` property sent by the browser has no effect.

### `POST /api/auth/demo`

Creates a `KITCHEN_STAFF` demo session and returns the same identity fields with `demo: true`. This supports the shared page's Demo Preview action.

### `GET /api/auth/me`

Returns the current session's `email`, `role`, `demo`, and server-selected `redirect_url`. An unauthenticated request returns HTTP 401.

### `POST /api/auth/logout`

Invalidates the server-side session and expires the session cookie.

## Session and access behavior

- A random session ID is stored in the browser's `HttpOnly`, `SameSite=Lax` cookie named `saigonbite_session`.
- Session records are held in process memory for up to eight hours and are lost on restart.
- Protected routes enforce strict role separation:
  - `KITCHEN_STAFF`: `/kitchen`, `/kitchen/`, `/style.css`, `/app.js`, and `/api/kitchen/*`
  - `CUSTOMER`: `/customer` and `/customer/`
  - `ADMIN`: `/admin`, `/admin/`, and `/api/vouchers/*`
  - `MANAGER`: `/manager`, `/manager/`, and `/api/reports/*`
- Missing sessions return HTTP 401 for APIs (or `303` redirect to `/` for UI pages); a different role receives HTTP 403 for APIs (or `303` redirect to that user's own role destination for UI pages).
- `SAIGONBITE_COOKIE_SECURE=1` enables the Secure cookie flag for HTTPS.

## Replacement before production

Replace the mock credential mapping and process-local session dictionary with the team's approved user store, password verification, session lifecycle/store, role policy, and deployment security controls. Agree final field names, response shape, error behavior, and whether role-based redirects belong in this API before adding these proposals to the shared API contract. No permanent database schema is introduced by this mock.