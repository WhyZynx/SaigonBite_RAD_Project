import os
from pathlib import Path

from fastapi import FastAPI, Request, Response, Depends
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
from app.models import Order
from app.routers.kitchen import router as kitchen_router
from app.routers.customer import router as customer_router
from app.routers.reports import router as reports_router
from app.routers.vouchers import router as vouchers_router
from app.schemas import LoginRequest, OrderDetail

app = FastAPI(title="SaigonBite Kitchen API", version="0.1.0")
app.include_router(kitchen_router)
app.include_router(customer_router)
app.include_router(reports_router)
app.include_router(vouchers_router)

project_dir = Path(__file__).resolve().parents[2]

frontend_dir = project_dir / "frontend" / "kitchen"
customer_frontend_dir = project_dir / "frontend" / "customer"
admin_frontend_dir = project_dir / "frontend" / "admin"
manager_frontend_dir = project_dir / "frontend" / "manager"
cookie_secure = os.getenv("SAIGONBITE_COOKIE_SECURE", "0") == "1"


@app.middleware("http")
async def protect_kitchen(request: Request, call_next):
    path = request.url.path
    role_for_path = None
    if path in {"/kitchen", "/style.css", "/app.js"} or path.startswith("/kitchen/") or path == "/api/kitchen" or path.startswith("/api/kitchen/"):
        role_for_path = "KITCHEN_STAFF"
    elif path.rstrip("/") == "/customer":
        role_for_path = "CUSTOMER"
    elif path.rstrip("/") == "/admin" or path.startswith("/admin/") or path == "/api/vouchers" or path.startswith("/api/vouchers/"):
        role_for_path = "ADMIN"
    elif (
        path.rstrip("/") == "/manager"
        or path.startswith("/manager/")
        or path == "/api/reports"
        or path.startswith("/api/reports/")
    ):
        role_for_path = "MANAGER"
    protected = role_for_path is not None or path == "/api/auth/me"
    session = get_session(request.cookies.get(SESSION_COOKIE)) if protected else None
    if protected and not session:
        if role_for_path and not path.startswith("/api/"):
            return RedirectResponse(url="/", status_code=303)
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})
    if role_for_path and session["role"] != role_for_path:
        if not path.startswith("/api/"):
            return RedirectResponse(url=role_home(session["role"]), status_code=303)
        return JSONResponse(status_code=403, content={"detail": "This account role cannot access this resource"})
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
def root_page(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if session:
        return RedirectResponse(url=role_home(session["role"]), status_code=303)
    return FileResponse(frontend_dir / "login.html")


@app.get("/login", include_in_schema=False)
def login_page():
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
    return {"email": session["email"], "role": session["role"], "demo": session["demo"], "redirect_url": role_home(session["role"])}


@app.post("/api/auth/logout", tags=["SaigonBite Authentication"])
def logout(request: Request, response: Response):
    clear_session(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(key=SESSION_COOKIE, path="/", httponly=True, samesite="lax", secure=cookie_secure)
    return {"message": "Logged out"}


@app.get("/customer/", include_in_schema=False)
@app.get("/customer", include_in_schema=False)
def customer_placeholder(request: Request):
    return FileResponse(customer_frontend_dir / "index.html")


@app.get("/customer/style.css", include_in_schema=False)
def customer_css():
    return FileResponse(customer_frontend_dir / "style.css", media_type="text/css")


@app.get("/customer/app.js", include_in_schema=False)
def customer_javascript():
    return FileResponse(customer_frontend_dir / "app.js", media_type="text/javascript")


@app.get("/admin/", include_in_schema=False)
@app.get("/admin", include_in_schema=False)
def admin_page():
    return FileResponse(admin_frontend_dir / "index.html")


@app.get("/admin/style.css", include_in_schema=False)
def admin_css():
    return FileResponse(
        admin_frontend_dir / "style.css",
        media_type="text/css"
    )


@app.get("/admin/app.js", include_in_schema=False)
def admin_javascript():
    return FileResponse(
        admin_frontend_dir / "app.js",
        media_type="text/javascript"
    )


@app.get("/manager/", include_in_schema=False)
@app.get("/manager", include_in_schema=False)
def manager_page():
    return FileResponse(manager_frontend_dir / "index.html")


@app.get("/manager/style.css", include_in_schema=False)
def manager_css():
    return FileResponse(
        manager_frontend_dir / "style.css",
        media_type="text/css"
    )


@app.get("/manager/app.js", include_in_schema=False)
def manager_javascript():
    return FileResponse(
        manager_frontend_dir / "app.js",
        media_type="text/javascript"
    )


@app.get("/api/orders/{order_id}", tags=["Orders"])
def get_order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if not session:
        return JSONResponse(status_code=401, content={"detail": "Authentication required"})
    if session["role"] not in {"CUSTOMER", "KITCHEN_STAFF", "MANAGER", "ADMIN"}:
        return JSONResponse(status_code=403, content={"detail": "This account role cannot access this resource"})
    
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        return JSONResponse(status_code=404, content={"detail": "Order not found"})
    
    if session["role"] == "CUSTOMER" and order.customer_id != 1: # Hoặc logic phân quyền customer ID thực tế
        return JSONResponse(status_code=404, content={"detail": "Order not found"})
        
    # Map dữ liệu từ ORM Model sang dạng trả về tương thích với schema
    items = [
        {
            "menu_item_id": item.menu_item_id,
            "name": item.menu_item.name if item.menu_item else "Item",
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "line_total": item.quantity * item.unit_price
        }
        for item in order.order_items
    ]
    
    history = [
        {
            "status": h.new_status,
            "changed_at": h.changed_at,
            "note": h.reason
        }
        for h in order.status_history
    ]

    return {
        "id": order.order_id,
        "customer_id": order.customer_id,
        "hub_id": order.hub_id,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at,
        "items": items,
        "delivery_address": order.delivery_address,
        "delivery_distance_km": order.delivery_distance_km,
        "voucher_code": order.voucher.code if order.voucher else None,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "surcharge": order.surcharge,
        "discount": order.discount,
        "rejection_reason": next((h.reason for h in order.status_history if h.new_status == "REJECTED"), None),
        "status_history": history
    }


app.mount("/kitchen", StaticFiles(directory=frontend_dir.resolve(), html=True), name="kitchen-ui")