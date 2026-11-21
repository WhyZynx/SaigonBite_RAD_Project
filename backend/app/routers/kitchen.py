import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.order import OrderRepository
from app.notification_service import NotificationService
from app.schemas import (
    DecisionRequest,
    DecisionResponse,
    OrderStatus,
    OrderSummary,
    StatusRequest,
    StatusResponse,
)

router = APIRouter(prefix="/api/kitchen", tags=["Kitchen"])
logger = logging.getLogger(__name__)


@router.get("/hubs")
def list_kitchen_hubs(db: Session = Depends(get_db)):
    return [
        {"id": hub.hub_id, "name": hub.name, "status": hub.status}
        for hub in OrderRepository(db).list_hubs()
    ]


@router.get("/orders", response_model=list[OrderSummary])
def list_kitchen_orders(
    hub_id: int = Query(gt=0),
    status: OrderStatus | None = None,
    db: Session = Depends(get_db),
):
    return [
        {
            "id": order.order_id,
            "customer_id": order.customer_id,
            "hub_id": order.hub_id,
            "status": order.status,
            "total": order.total,
            "created_at": order.created_at,
        }
        for order in OrderRepository(db).list_orders(hub_id, status)
    ]


@router.patch("/orders/{order_id}/decision", response_model=DecisionResponse)
def decide_order(order_id: int, request: DecisionRequest, db: Session = Depends(get_db)):
    result = OrderRepository(db).decide(order_id, request.decision.value, request.reason)
    if request.decision.value == "REJECT":
        try:
            NotificationService(db).notify_order_rejected(order_id, result["rejection_reason"])
        except Exception:
            db.rollback()
            logger.exception("Failed to create customer notification for rejected order %s", order_id)
    return result


@router.patch("/orders/{order_id}/status", response_model=StatusResponse)
def update_order_status(order_id: int, request: StatusRequest, db: Session = Depends(get_db)):
    return OrderRepository(db).change_status(order_id, request.status)
