from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Delivery, Hub, Order


def get_orders_in_range(db: Session, start_dt: datetime, end_dt: datetime) -> list[Order]:
    return db.query(Order).filter(Order.created_at.between(start_dt, end_dt)).all()


def get_completed_deliveries_in_range(
    db: Session, start_dt: datetime, end_dt: datetime
) -> list[Delivery]:
    return (
        db.query(Delivery)
        .join(Order)
        .filter(
            Order.created_at.between(start_dt, end_dt),
            Delivery.delivered_at.isnot(None),
            Delivery.pickup_at.isnot(None),
        )
        .all()
    )


def get_all_hubs(db: Session) -> list[Hub]:
    return db.query(Hub).all()


def get_hub_orders_in_range(
    db: Session, hub_id: int, start_dt: datetime, end_dt: datetime
) -> list[Order]:
    return (
        db.query(Order)
        .filter(
            Order.hub_id == hub_id,
            Order.created_at.between(start_dt, end_dt),
        )
        .all()
    )


def get_deliveries_by_order_range(
    db: Session, start_dt: datetime, end_dt: datetime
) -> list[Delivery]:
    return (
        db.query(Delivery)
        .join(Order)
        .filter(Order.created_at.between(start_dt, end_dt))
        .all()
    )