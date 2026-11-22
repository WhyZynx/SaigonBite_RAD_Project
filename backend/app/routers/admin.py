
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Delivery, Order, OrderStatusHistory, utc_now

router = APIRouter(prefix="/api/admin", tags=["Admin Orders"])


@router.get("/orders/ready")
def list_ready_orders(db: Session = Depends(get_db)):
    """List orders that Kitchen has finished preparing."""
    orders = db.scalars(
        select(Order)
        .options(
            joinedload(Order.customer),
            joinedload(Order.hub),
        )
        .where(Order.status == "READY")
        .order_by(Order.created_at.asc(), Order.order_id.asc())
    ).all()

    return [
        {
            "id": order.order_id,
            "customer_name": order.customer.name if order.customer else "Unknown",
            "customer_phone": order.customer.phone if order.customer else "",
            "hub_name": order.hub.name if order.hub else "Unknown",
            "delivery_address": order.delivery_address,
            "total": order.total,
            "created_at": order.created_at,
            "status": order.status,
        }
        for order in orders
    ]


@router.patch("/orders/{order_id}/deliver")
def mark_order_as_delivered(
    order_id: int,
    db: Session = Depends(get_db),
):
    """Admin simulates the delivery completion after Kitchen marks READY."""
    try:
        order = db.scalar(
            select(Order)
            .where(Order.order_id == order_id)
            .with_for_update()
        )

        if order is None:
            raise HTTPException(status_code=404, detail="Order not found.")

        if order.status != "READY":
            raise HTTPException(
                status_code=409,
                detail=f"Only READY orders can be delivered. Current status: {order.status}",
            )

        now = utc_now()

        # Conditional update protects against concurrent status changes.
        result = db.execute(
            update(Order)
            .where(
                Order.order_id == order_id,
                Order.status == "READY",
            )
            .values(status="DELIVERED")
            .execution_options(synchronize_session=False)
        )

        if result.rowcount != 1:
            raise HTTPException(
                status_code=409,
                detail="Order status changed. Please refresh and try again.",
            )

        db.add(
            OrderStatusHistory(
                order_id=order_id,
                old_status="READY",
                new_status="DELIVERED",
                reason="Marked as delivered by Admin (simulation).",
                changed_at=now,
            )
        )

        delivery = db.scalar(
            select(Delivery).where(Delivery.order_id == order_id)
        )

        if delivery is None:
            delivery = Delivery(
                order_id=order_id,
                delivered_at=now,
                outcome="DELIVERED",
            )
            db.add(delivery)
        else:
            delivery.delivered_at = now
            delivery.outcome = "DELIVERED"

        db.commit()

        return {
            "id": order_id,
            "previous_status": "READY",
            "status": "DELIVERED",
            "delivered_at": now,
            "message": "Order marked as delivered successfully.",
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
