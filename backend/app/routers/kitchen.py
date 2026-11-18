from fastapi import APIRouter, Query

from app.repositories.mock_orders import orders
from app.schemas import DecisionRequest, DecisionResponse, OrderDetail, OrderStatus, OrderSummary, StatusRequest, StatusResponse

router = APIRouter(prefix="/api/kitchen", tags=["Kitchen"])


@router.get("/orders", response_model=list[OrderSummary])
def list_kitchen_orders(hub_id: int = Query(gt=0), status: OrderStatus | None = None):
    return orders.list_orders(hub_id, status)


@router.patch("/orders/{order_id}/decision", response_model=DecisionResponse)
def decide_order(order_id: int, request: DecisionRequest):
    return orders.decide(order_id, request.decision.value, request.reason)


@router.patch("/orders/{order_id}/status", response_model=StatusResponse)
def update_order_status(order_id: int, request: StatusRequest):
    return orders.change_status(order_id, request.status)
