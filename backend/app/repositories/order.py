from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Hub, Order, OrderItem, OrderStatusHistory
from app.schemas import OrderStatus


class OrderRepository:
    """SQLAlchemy persistence operations used by the Kitchen endpoints."""

    KITCHEN_STATUSES = {
        OrderStatus.PENDING.value,
        OrderStatus.CONFIRMED.value,
        OrderStatus.PREPARING.value,
        OrderStatus.READY.value,
    }
    TRANSITIONS = {
        OrderStatus.PENDING.value: {OrderStatus.CONFIRMED.value, OrderStatus.REJECTED.value},
        OrderStatus.CONFIRMED.value: {OrderStatus.PREPARING.value},
        OrderStatus.PREPARING.value: {OrderStatus.READY.value},
    }

    def __init__(self, db: Session):
        self.db = db

    def list_hubs(self):
        return self.db.scalars(select(Hub).order_by(Hub.hub_id)).all()

    def list_orders(self, hub_id: int, status: OrderStatus | None = None):
        statement = select(Order).where(Order.hub_id == hub_id)
        if status is None:
            statement = statement.where(Order.status.in_(self.KITCHEN_STATUSES))
        else:
            statement = statement.where(Order.status == status.value)
        statement = statement.order_by(Order.created_at.desc(), Order.order_id.desc())
        return self.db.scalars(statement).all()

    def get_order(self, order_id: int) -> Order:
        order = self.db.scalar(
            select(Order)
            .options(
                selectinload(Order.order_items).joinedload(OrderItem.menu_item),
                selectinload(Order.status_history),
                joinedload(Order.voucher),
                joinedload(Order.customer),
            )
            .where(Order.order_id == order_id)
        )
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def decide(self, order_id: int, decision: str, reason: str | None = None):
        if decision not in {"CONFIRM", "REJECT"}:
            raise HTTPException(status_code=400, detail="Invalid decision")
        if decision == "REJECT" and not (reason or "").strip():
            raise HTTPException(status_code=400, detail="A rejection reason is required")
        next_status = OrderStatus.CONFIRMED.value if decision == "CONFIRM" else OrderStatus.REJECTED.value
        normalized_reason = (reason or "").strip() or None
        return self._transition(order_id, next_status, normalized_reason)

    def change_status(self, order_id: int, next_status: OrderStatus):
        return self._transition(order_id, next_status.value, None)

    def _transition(self, order_id: int, next_status: str, reason: str | None):
        try:
            order = self.db.scalar(
                select(Order).where(Order.order_id == order_id).with_for_update()
            )
            if order is None:
                raise HTTPException(status_code=404, detail="Order not found")

            previous_status = getattr(order, "status", None)
            if not isinstance(previous_status, str):
                raise RuntimeError("Loaded order status must be a string")
            if next_status not in self.TRANSITIONS.get(previous_status, set()):
                raise HTTPException(
                    status_code=409,
                    detail=f"Transition from {previous_status} to {next_status} is not allowed",
                )

            # The conditional UPDATE also protects databases without row-level FOR UPDATE
            # semantics (notably SQLite test fixtures) from racing transitions.
            result = self.db.execute(
                update(Order)
                .where(Order.order_id == order_id, Order.status == previous_status)
                .values(status=next_status)
                .execution_options(synchronize_session=False)
            )
            if not isinstance(result, CursorResult):
                raise RuntimeError("Order status update did not return a cursor result")
            if result.rowcount != 1:
                self.db.rollback()
                raise HTTPException(status_code=409, detail="Order status changed concurrently")

            self.db.add(
                OrderStatusHistory(
                    order_id=order_id,
                    old_status=previous_status,
                    new_status=next_status,
                    reason=reason,
                )
            )
            self.db.commit()
            return {
                "id": order_id,
                "previous_status": previous_status,
                "status": next_status,
                **({"rejection_reason": reason} if next_status == OrderStatus.REJECTED.value else {}),
            }
        except HTTPException:
            if self.db.in_transaction():
                self.db.rollback()
            raise
        except Exception:
            self.db.rollback()
            raise
