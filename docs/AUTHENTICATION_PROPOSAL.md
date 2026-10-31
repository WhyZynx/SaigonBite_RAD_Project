# SaigonBite Authentication Proposal (Temporary Mock)

**Status:** Implementation proposal for team review. This file is separate from `API_CONTRACT.md`; the existing order API contract is unchanged.

## Mock roles and routing

The backend currently maps configured mock credentials to one of `CUSTOMER`, `KITCHEN_STAFF`, or `ADMIN`. The submitted login request contains only `email` and `password`; any client-supplied role is ignored. The server returns the authenticated role and its fixed destination:

| Role | Destination |
|---|---|
| `CUSTOMER` | `/customer/` |
| `KITCHEN_STAFF` | `/kitchen/` |
| `ADMIN` | `/admin/` |

Customer and Admin destinations currently return explicit temporary placeholders because their interface files are empty. They do not modify TV1/TV3 code.

## Proposed authentication endpoints

These routes are implemented for the local demo and need team approval before being treated as a shared contract.

### `POST /api/auth/login`

Request:

```json
{"email":"kitchen@saigonbite.local","password":"KitchenDemo2026!"}
```

Success response:

```json
{"email":"kitchen@saigonbite.local","role":"KITCHEN_STAFF","demo":false,"redirect_url":"/kitchen/"}
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
- Kitchen UI assets, Kitchen APIs, and the shared order detail route require a `KITCHEN_STAFF` session. Missing sessions return HTTP 401 for APIs; a different role receives HTTP 403 for APIs. A wrong-role page request redirects to that user's own role destination.
- Customer/Admin placeholder routes require their matching session role.
- `SAIGONBITE_COOKIE_SECURE=1` enables the Secure cookie flag for HTTPS.

## Replacement before production

Replace the mock credential mapping and process-local session dictionary with the team's approved user store, password verification, session lifecycle/store, role policy, and deployment security controls. Agree final field names, response shape, error behavior, and whether role-based redirects belong in this API before adding these proposals to the shared API contract. No permanent database schema is introduced by this mock.
