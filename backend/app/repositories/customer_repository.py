from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session, joinedload

from app.models import Customer, Hub, MenuItem, Order, OrderItem, OrderStatusHistory, Voucher
from app.schemas import CreateOrderRequest
from app.voucher_rules import calculate_voucher_discount


def get_hubs(db: Session) -> list[Hub]:
    return db.query(Hub).order_by(Hub.hub_id).all()


def get_menu_items(db: Session, hub_id: int) -> list[MenuItem]:
    return (db.query(MenuItem).filter(MenuItem.hub_id == hub_id)
            .order_by(MenuItem.menu_item_id).all())


def customer_has_used_voucher(db: Session, customer_id: int, voucher_id: int) -> bool:
    return (db.query(Order.order_id)
            .filter(Order.customer_id == customer_id, Order.voucher_id == voucher_id)
            .with_for_update().first() is not None)


def create_order(
    db: Session,
    payload: CreateOrderRequest,
    *,
    customer_id: int,
    delivery_distance_km: float,
    delivery_fee: int,
    surcharge: int = 0,
) -> Order:
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

        hub = (db.query(Hub).filter(Hub.hub_id == payload.hub_id)
               .with_for_update().first())
        if hub is None:
            raise HTTPException(status_code=404, detail="Hub not found")
        if hub.status != "OPEN":
            raise HTTPException(status_code=400, detail="This hub is not accepting orders")

        requested_ids = {line.menu_item_id for line in payload.items}
        menu_items = (db.query(MenuItem)
                      .filter(MenuItem.hub_id == payload.hub_id,
                              MenuItem.menu_item_id.in_(requested_ids)).all())
        menu_by_id = {item.menu_item_id: item for item in menu_items}
        if len(menu_by_id) != len(requested_ids) or any(not item.is_available for item in menu_items):
            raise HTTPException(status_code=400, detail="A menu item is unavailable")

        subtotal = sum(menu_by_id[line.menu_item_id].price * line.quantity for line in payload.items)
        voucher = None
        discount = 0
        if payload.voucher_code:
            voucher = db.query(Voucher).filter(
                Voucher.code == payload.voucher_code.strip().upper()
            ).with_for_update().first()
            discount = calculate_voucher_discount(voucher, subtotal)
            if customer_has_used_voucher(db, customer_id, voucher.voucher_id):
                raise HTTPException(status_code=400, detail="You have already used this voucher on a previous order")

        order = Order(
            customer_id=customer_id,
            hub_id=payload.hub_id,
            voucher_id=voucher.voucher_id if voucher else None,
            status="PENDING",
            delivery_address=payload.delivery_address,
            delivery_distance_km=delivery_distance_km,
            payment_method=payload.payment_method,
            payment_status="UNPAID",
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            surcharge=surcharge,
            discount=discount,
            total=subtotal + delivery_fee + surcharge - discount,
        )
        for line in payload.items:
            item = menu_by_id[line.menu_item_id]
            order.order_items.append(OrderItem(
                menu_item_id=item.menu_item_id,
                quantity=line.quantity,
                unit_price=item.price,
            ))
        order.status_history.append(
            OrderStatusHistory(old_status=None, new_status="PENDING", reason=None)
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def get_customer_orders(db: Session, customer_id: int, status: str | None = None) -> list[Order]:
    query = db.query(Order).filter(Order.customer_id == customer_id)
    if status:
        query = query.filter(Order.status == status.upper())
    return query.order_by(Order.created_at.desc(), Order.order_id.desc()).all()


def get_order_detail(db: Session, order_id: int) -> Order | None:
    return (db.query(Order)
            .options(joinedload(Order.order_items).joinedload(OrderItem.menu_item),
                     joinedload(Order.status_history), joinedload(Order.voucher))
            .filter(Order.order_id == order_id).first())


def cancel_pending_order(db: Session, order_id: int, customer_id: int) -> dict:
    try:
        order = (db.query(Order)
                 .filter(Order.order_id == order_id, Order.customer_id == customer_id)
                 .with_for_update().first())
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status != "PENDING":
            raise HTTPException(status_code=409, detail="Only pending orders can be cancelled")

        result = db.execute(
            update(Order)
            .where(Order.order_id == order_id, Order.customer_id == customer_id,
                   Order.status == "PENDING")
            .values(status="CANCELLED")
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            raise HTTPException(status_code=409, detail="Order status changed; refresh and try again")

        db.add(OrderStatusHistory(
            order_id=order_id,
            old_status="PENDING",
            new_status="CANCELLED",
            reason="Cancelled by customer",
        ))
        db.commit()
        return {"id": order_id, "previous_status": "PENDING", "status": "CANCELLED"}
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise
