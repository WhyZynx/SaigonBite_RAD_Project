from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.auth import SESSION_COOKIE, get_session
from app.database import get_db
from app.repositories import customer_repository
from app.schemas import CreateOrderRequest, CreateOrderResponse

router = APIRouter(tags=["Customer"])
DELIVERY_BASE_FEE = 15_000
MAX_DELIVERY_DISTANCE_KM = 10
MOCK_DELIVERY_DISTANCE_KM = 3.5


def customer_session(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if not session or session["role"] != "CUSTOMER":
        raise HTTPException(status_code=401 if not session else 403, detail="Customer access required")
    return session


def _hub_payload(hub):
    return {"id": hub.hub_id, "name": hub.name, "address": hub.address,
            "accepting_orders": hub.status == "OPEN"}


@router.get("/api/hubs")
def list_hubs(request: Request, db: Session = Depends(get_db)):
    customer_session(request)
    return [_hub_payload(hub) for hub in customer_repository.get_hubs(db)]


@router.get("/api/menu-items")
def list_menu_items(request: Request, hub_id: int = Query(gt=0), db: Session = Depends(get_db)):
    customer_session(request)
    items = customer_repository.get_menu_items(db, hub_id)
    return [{"id": item.menu_item_id, "hub_id": item.hub_id, "name": item.name,
             "price": item.price, "is_available": item.is_available} for item in items]


@router.post("/api/orders", response_model=CreateOrderResponse, status_code=201)
def create_order(payload: CreateOrderRequest, request: Request, db: Session = Depends(get_db)):
    customer_session(request)
    if payload.customer_id != 1:
        raise HTTPException(status_code=403, detail="Customer does not match the signed-in demo account")

    if MOCK_DELIVERY_DISTANCE_KM > MAX_DELIVERY_DISTANCE_KM:
        raise HTTPException(
            status_code=400,
            detail=f"Delivery distance exceeds the {MAX_DELIVERY_DISTANCE_KM} km limit",
        )
    order = customer_repository.create_order(
        db,
        payload,
        delivery_distance_km=MOCK_DELIVERY_DISTANCE_KM,
        delivery_fee=DELIVERY_BASE_FEE,
    )
    return {"id": order.order_id, "status": order.status, "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee, "surcharge": order.surcharge,
            "discount": order.discount, "total": order.total}


@router.get("/api/customers/{customer_id}/orders")
def list_customer_orders(customer_id: int, request: Request, status: str | None = None,
                         db: Session = Depends(get_db)):
    customer_session(request)
    if customer_id != 1:
        raise HTTPException(status_code=403, detail="Customer does not match the signed-in demo account")
    rows = customer_repository.get_customer_orders(db, customer_id, status)
    return [{"id": order.order_id, "customer_id": order.customer_id, "hub_id": order.hub_id,
             "status": order.status, "total": order.total, "created_at": order.created_at}
            for order in rows]


@router.get("/api/orders/{order_id}")
def get_order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] not in {"CUSTOMER", "KITCHEN_STAFF", "MANAGER", "ADMIN"}:
        raise HTTPException(status_code=403, detail="This account role cannot access this resource")
    order = customer_repository.get_order_detail(db, order_id)
    if order is None or (session["role"] == "CUSTOMER" and order.customer_id != 1):
        raise HTTPException(status_code=404, detail="Order not found")
    history = sorted(order.status_history, key=lambda entry: (entry.changed_at, entry.history_id))
    return {
        "id": order.order_id, "customer_id": order.customer_id, "hub_id": order.hub_id,
        "status": order.status, "total": order.total, "created_at": order.created_at,
        "items": [{"menu_item_id": item.menu_item_id,
                   "name": item.menu_item.name if item.menu_item else "Item",
                   "quantity": item.quantity, "unit_price": item.unit_price,
                   "line_total": item.quantity * item.unit_price} for item in order.order_items],
        "delivery_address": order.delivery_address,
        "delivery_distance_km": order.delivery_distance_km,
        "voucher_code": order.voucher.code if order.voucher else None,
        "payment_method": order.payment_method, "payment_status": order.payment_status,
        "subtotal": order.subtotal, "delivery_fee": order.delivery_fee,
        "surcharge": order.surcharge, "discount": order.discount,
        "rejection_reason": next((entry.reason for entry in history if entry.new_status == "REJECTED"), None),
        "status_history": [{"status": entry.new_status, "changed_at": entry.changed_at,
                            "note": entry.reason} for entry in history],
    }
