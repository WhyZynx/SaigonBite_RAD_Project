import os
from html import escape
from pathlib import Path

from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.auth import (
    DEMO_EMAIL,
    SESSION_COOKIE,
    SESSION_TTL_SECONDS,
    authenticate_credentials,
    clear_session,
    create_session,
    get_session,
    role_home,
)
from app.database import get_db
from app.repositories.order import OrderRepository
from app.routers.kitchen import router as kitchen_router
from app.schemas import LoginRequest, OrderDetail

app = FastAPI(title="SaigonBite Kitchen API", version="0.1.0")
app.include_router(kitchen_router)

project_dir = Path(__file__).resolve().parents[2]
frontend_dir = project_dir / "frontend" / "kitchen"
cookie_secure = os.getenv("SAIGONBITE_COOKIE_SECURE", "0") == "1"


@app.middleware("http")
async def protect_kitchen(request: Request, call_next):
    path = request.url.path
    role_for_path = None
    if path in {"/kitchen", "/style.css", "/app.js"} or path.startswith("/kitchen/") or path == "/api/kitchen" or path.startswith("/api/kitchen/") or path.startswith("/api/orders/"):
        role_for_path = "KITCHEN_STAFF"
    elif path.rstrip("/") == "/customer":
        role_for_path = "CUSTOMER"
    elif path.rstrip("/") == "/admin":
        role_for_path = "ADMIN"
    protected = role_for_path is not None or path == "/api/auth/me"
    session = get_session(request.cookies.get(SESSION_COOKIE)) if protected else None
    if role_for_path is not None:
        if session is None:
            if not path.startswith("/api/"):
                return RedirectResponse(url="/", status_code=303)
            return JSONResponse(status_code=401, content={"detail": "Authentication required"})
        if session["role"] != role_for_path:
            if not path.startswith("/api/"):
                return RedirectResponse(url=role_home(session["role"]), status_code=303)
            return JSONResponse(status_code=403, content={"detail": "This account role cannot access this resource"})
    elif path == "/api/auth/me" and session is None:
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})
    return await call_next(request)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=cookie_secure,
        samesite="lax",
        path="/",
    )


@app.get("/", include_in_schema=False)
@app.get("/login", include_in_schema=False)
def login_page(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if session:
        return RedirectResponse(url=role_home(session["role"]), status_code=303)
    return FileResponse(frontend_dir / "login.html")


@app.get("/login.css", include_in_schema=False)
def login_css():
    return FileResponse(frontend_dir / "login.css", media_type="text/css")


@app.get("/login.js", include_in_schema=False)
def login_javascript():
    return FileResponse(frontend_dir / "login.js", media_type="text/javascript")


@app.get("/style.css", include_in_schema=False)
def kitchen_css():
    return FileResponse(frontend_dir / "style.css", media_type="text/css")


@app.get("/app.js", include_in_schema=False)
def kitchen_javascript():
    return FileResponse(frontend_dir / "app.js", media_type="text/javascript")


@app.post("/api/auth/login", tags=["SaigonBite Authentication"])
def login(payload: LoginRequest, response: Response):
    account = authenticate_credentials(payload.email, payload.password)
    if not account:
        return JSONResponse(status_code=401, content={"detail": "Invalid email or password"})
    role = account["role"]
    token = create_session(account["email"], role, demo=False)
    set_session_cookie(response, token)
    return {"email": account["email"], "role": role, "demo": False, "redirect_url": role_home(role)}


@app.post("/api/auth/demo", tags=["SaigonBite Authentication"])
def demo_preview(response: Response):
    role = "KITCHEN_STAFF"
    token = create_session(DEMO_EMAIL, role, demo=True)
    set_session_cookie(response, token)
    return {"email": DEMO_EMAIL, "role": role, "demo": True, "redirect_url": role_home(role)}


@app.get("/api/auth/me", tags=["SaigonBite Authentication"])
def current_user(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if session is None:
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})
    return {"email": session["email"], "role": session["role"], "demo": session["demo"], "redirect_url": role_home(session["role"])}


@app.post("/api/auth/logout", tags=["SaigonBite Authentication"])
def logout(request: Request, response: Response):
    clear_session(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(key=SESSION_COOKIE, path="/", httponly=True, samesite="lax", secure=cookie_secure)
    return {"message": "Logged out"}


@app.get("/customer/", include_in_schema=False)
@app.get("/customer", include_in_schema=False)
def customer_placeholder(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if session is None:
        return RedirectResponse(url="/", status_code=303)
    email = escape(session["email"])
    return HTMLResponse(temporary_role_placeholder_content("CUSTOMER", email))


@app.get("/admin/", include_in_schema=False)
@app.get("/admin", include_in_schema=False)
def admin_placeholder(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if session is None:
        return RedirectResponse(url="/", status_code=303)
    email = escape(session["email"])
    return HTMLResponse(temporary_role_placeholder_content("ADMIN", email))


def temporary_role_placeholder_content(role: str, email: str) -> str:
    title = "Customer interface" if role == "CUSTOMER" else "Admin interface"
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} | SaigonBite</title><style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#fbf8f0;color:#263b31;font:16px Arial,sans-serif}}main{{max-width:520px;margin:24px;padding:38px;background:#fff;border:1px solid #e5ebe3;border-radius:12px;box-shadow:0 8px 30px #173d3212}}.brand{{color:#173d32;font-size:22px;font-weight:700}}.brand small{{display:block;margin-top:5px;color:#7c8b7f;font-size:10px;letter-spacing:1px}}h1{{margin:34px 0 10px;font-size:24px}}p{{color:#768379;line-height:1.6}}strong{{color:#405447}}button{{margin-top:16px;padding:12px 20px;border:0;border-radius:6px;background:#173d32;color:#fff;font-weight:700;cursor:pointer}}</style><main><div class="brand">SaigonBite<small>MANAGEMENT SYSTEM</small></div><h1>{title} is not integrated yet</h1><p>This temporary placeholder confirms that <strong>{email}</strong> signed in as <strong>{role}</strong>. The role-specific interface will appear here when its team module is integrated.</p><button id="logout">Sign Out</button></main><script>document.getElementById('logout').onclick=async()=>{{await fetch('/api/auth/logout',{{method:'POST'}});location.assign('/')}};</script></html>"""


@app.get("/api/orders/{order_id}", response_model=OrderDetail, tags=["Orders"])
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    """Shared order detail read used by Kitchen and other order workflows."""
    order = OrderRepository(db).get_order(order_id)
    history = sorted(order.status_history, key=lambda entry: (entry.changed_at, entry.history_id))
    rejection = next(
        (entry.reason for entry in reversed(history)
         if entry.new_status == "REJECTED" and entry.reason),
        None,
    )
    return {
        "id": order.order_id,
        "customer_id": order.customer_id,
        "hub_id": order.hub_id,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at,
        "customer_name": order.customer.name,
        "customer_phone": order.customer.phone,
        "items": [
            {
                "menu_item_id": item.menu_item_id,
                "name": item.menu_item.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_total": item.quantity * item.unit_price,
            }
            for item in order.order_items
        ],
        "delivery_address": order.delivery_address,
        "delivery_distance_km": order.delivery_distance_km,
        "voucher_code": order.voucher.code if order.voucher else None,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "surcharge": order.surcharge,
        "discount": order.discount,
        "rejection_reason": rejection,
        "status_history": [
            {
                "status": entry.new_status,
                "changed_at": entry.changed_at,
                "note": entry.reason,
            }
            for entry in history
        ],
    }


app.mount("/kitchen", StaticFiles(directory=frontend_dir.resolve(), html=True), name="kitchen-ui")
