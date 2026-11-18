from fastapi import APIRouter, HTTPException, Query, Request

from app.auth import SESSION_COOKIE, get_session
from app.repositories.mock_orders import HUBS, MENU_ITEMS, orders
from app.schemas import CreateOrderRequest, CreateOrderResponse

router = APIRouter(tags=["Customer"])


def customer_session(request: Request):
    session = get_session(request.cookies.get(SESSION_COOKIE))
    if not session or session["role"] != "CUSTOMER":
        raise HTTPException(status_code=401 if not session else 403, detail="Customer access required")
    return session


@router.get("/api/hubs")
def list_hubs(request: Request):
    customer_session(request)
    return HUBS


@router.get("/api/menu-items")
def list_menu_items(request: Request, hub_id: int = Query(gt=0)):
    customer_session(request)
    return [item for item in MENU_ITEMS if item["hub_id"] == hub_id]


@router.post("/api/orders", response_model=CreateOrderResponse, status_code=201)
def create_order(payload: CreateOrderRequest, request: Request):
    customer_session(request)
    if payload.customer_id != 1:
        raise HTTPException(status_code=403, detail="Customer does not match the signed-in demo account")
    order = orders.create(customer_id=1, hub_id=payload.hub_id, items=payload.items,
                          delivery_address=payload.delivery_address, payment_method=payload.payment_method)
    return {key: order[key] for key in ("id", "status", "subtotal", "delivery_fee", "surcharge", "discount", "total")}


@router.get("/api/customers/{customer_id}/orders")
def list_customer_orders(customer_id: int, request: Request):
    customer_session(request)
    # The temporary auth mock maps every customer session to demo customer 1.
    if customer_id != 1:
        raise HTTPException(status_code=403, detail="Customer does not match the signed-in demo account")
    return orders.list_customer_orders(customer_id)
