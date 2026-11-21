from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Delivery, Hub, Order, OrderStatusHistory


def get_orders_in_range(db: Session, start_dt: datetime, end_dt: datetime) -> list[Order]:
    return db.query(Order).filter(Order.created_at.between(start_dt, end_dt)).all()


def get_all_hubs(db: Session) -> list[Hub]:
    return db.query(Hub).order_by(Hub.hub_id).all()


def get_hub_orders_in_range(db: Session, hub_id: int, start_dt: datetime, end_dt: datetime) -> list[Order]:
    return (db.query(Order)
            .filter(Order.hub_id == hub_id, Order.created_at.between(start_dt, end_dt))
            .all())


def get_deliveries_by_order_range(db: Session, start_dt: datetime, end_dt: datetime) -> list[Delivery]:
    return (db.query(Delivery).join(Order)
            .filter(Order.created_at.between(start_dt, end_dt))
            .all())


def get_status_history_in_range(
    db: Session, start_dt: datetime, end_dt: datetime
) -> list[OrderStatusHistory]:
    return (db.query(OrderStatusHistory).join(Order)
            .filter(Order.created_at.between(start_dt, end_dt))
            .order_by(OrderStatusHistory.changed_at, OrderStatusHistory.history_id)
            .all())


def average_delivery_minutes(deliveries: list[Delivery]) -> float | None:
    durations = [
        (row.delivered_at - row.pickup_at).total_seconds() / 60
        for row in deliveries
        if row.pickup_at is not None
        and row.delivered_at is not None
        and row.delivered_at >= row.pickup_at
    ]
    return sum(durations) / len(durations) if durations else None
