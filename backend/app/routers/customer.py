from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import SESSION_COOKIE, get_session
from app.delivery_fee_service import DeliveryFeeService
from app.database import get_db
from app.repositories import customer_repository
from app.repositories.notification import NotificationRepository
from app.schemas import CreateOrderItem, CreateOrderRequest, CreateOrderResponse
from app.models import Customer, Hub, MenuItem, Order, Voucher
from app.voucher_rules import calculate_voucher_discount

router = APIRouter(tags=["Customer"])


class VoucherPreviewRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    hub_id: int = Field(gt=0)
    destination_address: str = Field(min_length=5, max_length=255)
    items: list[CreateOrderItem] = Field(min_length=1)


def customer_session(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if not session or session["role"] != "CUSTOMER":
        raise HTTPException(status_code=401 if not session else 403, detail="Customer access required")
    return session


def current_customer(request: Request, db: Session) -> Customer:
    session = customer_session(request)
    matches = (db.query(Customer)
               .filter(func.lower(Customer.email) == session["email"].strip().lower())
               .all())
    if len(matches) != 1:
        raise HTTPException(
            status_code=403,
            detail="The signed-in customer account must match exactly one customer profile",
        )
    return matches[0]


def _hub_payload(hub):
    return {"id": hub.hub_id, "name": hub.name, "address": hub.address,
            "accepting_orders": hub.status == "OPEN"}


def _has_nonblank_contact_line(address: str, label: str) -> bool:
    for line in address.splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip().casefold() == label.casefold() and value.strip():
            return True
    return False


def _utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _order_completed_at(order: Order) -> str | None:
    if order.delivery and order.delivery.delivered_at:
        return _utc_timestamp(order.delivery.delivered_at)
    delivered = [entry.changed_at for entry in order.status_history if entry.new_status == "DELIVERED"]
    return _utc_timestamp(max(delivered)) if delivered else None


@router.post("/api/customer/vouchers/validate")
def validate_voucher(payload: VoucherPreviewRequest, request: Request, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    route = DeliveryFeeService(db).calculate(payload.hub_id, payload.destination_address)
    hub = db.query(Hub).filter(Hub.hub_id == payload.hub_id).first()
    if hub is None or hub.status != "OPEN":
        raise HTTPException(status_code=400, detail="This hub is not accepting orders")
    quantities = {}
    for item in payload.items:
        quantities[item.menu_item_id] = quantities.get(item.menu_item_id, 0) + item.quantity
    menu_items = (db.query(MenuItem).filter(MenuItem.hub_id == payload.hub_id,
                                            MenuItem.menu_item_id.in_(quantities)).all())
    menu_by_id = {item.menu_item_id: item for item in menu_items}
    if len(menu_by_id) != len(quantities) or any(not item.is_available for item in menu_items):
        raise HTTPException(status_code=400, detail="A menu item is unavailable")
    subtotal = sum(menu_by_id[item_id].price * quantity for item_id, quantity in quantities.items())
    voucher = db.query(Voucher).filter(Voucher.code == payload.code.strip().upper()).first()
    discount = calculate_voucher_discount(voucher, subtotal)
    if customer_repository.customer_has_used_voucher(db, customer.customer_id, voucher.voucher_id):
        raise HTTPException(status_code=400, detail="You have already used this voucher on a previous order")
    return {"code": voucher.code, "subtotal": subtotal,
            "discount": discount, **route,
            "total": subtotal + route["delivery_fee"] + route["surcharge"] - discount}


@router.get("/api/customer/vouchers")
def list_available_vouchers(request: Request, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    now = datetime.now()
    vouchers = (db.query(Voucher)
                .filter(Voucher.status == "ACTIVE", Voucher.start_date <= now, Voucher.end_date >= now)
                .filter(~Voucher.voucher_id.in_(
                    db.query(Order.voucher_id)
                    .filter(Order.customer_id == customer.customer_id, Order.voucher_id.isnot(None))
                ))
                .order_by(Voucher.end_date.asc(), Voucher.code.asc()).all())
    return [{"code": voucher.code, "discount_type": voucher.discount_type,
             "discount_value": voucher.discount_value, "min_order": voucher.min_order,
             "valid_from": voucher.start_date, "valid_until": voucher.end_date}
            for voucher in vouchers]


@router.get("/api/hubs")
def list_hubs(request: Request, db: Session = Depends(get_db)):
    current_customer(request, db)
    return [_hub_payload(hub) for hub in customer_repository.get_hubs(db)]


@router.get("/api/menu-items")
def list_menu_items(request: Request, hub_id: int = Query(gt=0), db: Session = Depends(get_db)):
    current_customer(request, db)
    items = customer_repository.get_menu_items(db, hub_id)
    return [{"id": item.menu_item_id, "hub_id": item.hub_id, "name": item.name,
             "price": item.price, "is_available": item.is_available} for item in items]


@router.get("/api/delivery-options")
def delivery_options(request: Request, hub_id: int = Query(gt=0), db: Session = Depends(get_db)):
    current_customer(request, db)
    hub = db.query(Hub).filter(Hub.hub_id == hub_id).first()
    if hub is None:
        raise HTTPException(status_code=404, detail="Hub not found")
    if hub.status != "OPEN":
        raise HTTPException(status_code=400, detail="This hub is not accepting orders")
    return {"hub_id": hub.hub_id, "hub_name": hub.name, "hub_address": hub.address}


class DeliveryQuoteRequest(BaseModel):
    hub_id: int = Field(gt=0)
    delivery_address: str = Field(min_length=5, max_length=255)


@router.post("/api/delivery-quote")
def delivery_quote(payload: DeliveryQuoteRequest, request: Request, db: Session = Depends(get_db)):
    current_customer(request, db)
    return DeliveryFeeService(db).calculate(payload.hub_id, payload.delivery_address)


@router.post("/api/orders", response_model=CreateOrderResponse, status_code=201)
def create_order(payload: CreateOrderRequest, request: Request, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    if not _has_nonblank_contact_line(payload.delivery_address, "Recipient"):
        raise HTTPException(status_code=422, detail="Recipient name is required")
    if not _has_nonblank_contact_line(payload.delivery_address, "Phone"):
        raise HTTPException(status_code=422, detail="Delivery phone number is required")
    route = DeliveryFeeService(db).calculate(payload.hub_id, payload.destination_address)
    address = f"{payload.destination_address}\n{payload.delivery_address}"
    if len(address) > 255:
        raise HTTPException(status_code=422, detail="Delivery address details are too long")
    payload.delivery_address = address
    order = customer_repository.create_order(
        db,
        payload,
        customer_id=customer.customer_id,
        delivery_distance_km=route["delivery_distance_km"],
        delivery_fee=route["delivery_fee"],
        surcharge=route["surcharge"],
    )
    return {"id": order.order_id, "status": order.status, "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee, "delivery_distance_km": order.delivery_distance_km,
            "surcharge": order.surcharge,
            "discount": order.discount, "total": order.total}


@router.get("/api/customer/profile")
def get_customer_profile(request: Request, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    return {"id": customer.customer_id, "name": customer.name,
            "email": customer.email, "phone": customer.phone,
            "customer_type": customer.customer_type}


@router.get("/api/customer/notifications")
def list_customer_notifications(request: Request, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    return NotificationRepository(db).list_for_customer(customer.customer_id)


@router.get("/api/customer/notifications/unread-count")
def get_customer_notification_unread_count(request: Request, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    return {"unread_count": NotificationRepository(db).unread_count(customer.customer_id)}


@router.patch("/api/customer/notifications/{notification_id}/read")
def mark_customer_notification_read(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    customer = current_customer(request, db)
    return NotificationRepository(db).mark_read(customer.customer_id, notification_id)


@router.get("/api/customer/orders")
def list_customer_orders(request: Request, status: str | None = None, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    rows = customer_repository.get_customer_orders(db, customer.customer_id, status)
    return [{"id": order.order_id, "customer_id": order.customer_id, "hub_id": order.hub_id,
             "status": order.status, "total": order.total, "created_at": _utc_timestamp(order.created_at),
             "completed_at": _order_completed_at(order)}
            for order in rows]


@router.post("/api/customer/orders/{order_id}/cancel")
def cancel_customer_order(order_id: int, request: Request, db: Session = Depends(get_db)):
    customer = current_customer(request, db)
    return customer_repository.cancel_pending_order(db, order_id, customer.customer_id)


@router.get("/api/orders/{order_id}")
def get_order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")
    if session["role"] not in {"CUSTOMER", "KITCHEN_STAFF", "MANAGER", "ADMIN"}:
        raise HTTPException(status_code=403, detail="This account role cannot access this resource")
    customer = current_customer(request, db) if session["role"] == "CUSTOMER" else None
    order = customer_repository.get_order_detail(db, order_id)
    if order is None or (customer is not None and order.customer_id != customer.customer_id):
        raise HTTPException(status_code=404, detail="Order not found")
    history = sorted(order.status_history, key=lambda entry: (entry.changed_at, entry.history_id))
    return {
        "id": order.order_id, "customer_id": order.customer_id, "hub_id": order.hub_id,
        "status": order.status, "total": order.total, "created_at": _utc_timestamp(order.created_at),
        "completed_at": _order_completed_at(order),
        "customer_name": order.customer.name if order.customer else None,
        "customer_phone": order.customer.phone if order.customer else None,
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
        "status_history": [{"status": entry.new_status, "changed_at": _utc_timestamp(entry.changed_at),
                            "note": entry.reason} for entry in history],
    }
