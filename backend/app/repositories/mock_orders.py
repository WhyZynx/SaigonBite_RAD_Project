"""Temporary process-local order repository. Replace this adapter with MySQL later."""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from threading import RLock

from fastapi import HTTPException

from app.schemas import OrderStatus

TZ = timezone(timedelta(hours=7))


def now():
    return datetime.now(TZ)


def sample_order(order_id, customer_id, status, name, quantity, price, minutes, hub_id=1):
    created = now() - timedelta(minutes=minutes)
    return {
        "id": order_id, "customer_id": customer_id, "hub_id": hub_id,
        "status": status, "total": quantity * price + 15000,
        "created_at": created, "items": [{"menu_item_id": order_id, "name": name,
        "quantity": quantity, "unit_price": price, "line_total": quantity * price}],
        "delivery_address": "District 1, Ho Chi Minh City", "delivery_distance_km": 3.2,
        "voucher_code": None, "payment_method": "COD", "payment_status": "UNPAID",
        "subtotal": quantity * price, "delivery_fee": 15000, "surcharge": 0,
        "discount": 0, "rejection_reason": None,
        "status_history": [{"status": status, "changed_at": created, "note": None}],
    }


class MockOrderRepository:
    def __init__(self):
        self._lock = RLock()
        self._orders = {
            101: sample_order(101, 1, OrderStatus.PENDING, "Cơm gà xối mỡ", 2, 55000, 4),
            102: sample_order(102, 2, OrderStatus.PENDING, "Bánh mì thịt nướng", 3, 35000, 8),
            103: sample_order(103, 3, OrderStatus.CONFIRMED, "Phở bò đặc biệt", 1, 75000, 13),
            104: sample_order(104, 4, OrderStatus.PREPARING, "Bún thịt nướng", 2, 50000, 18),
            105: sample_order(105, 5, OrderStatus.READY, "Gỏi cuốn tôm", 2, 45000, 25),
            106: sample_order(106, 6, OrderStatus.PENDING, "Cơm tấm sườn", 1, 60000, 7, 2),
        }

    def list_orders(self, hub_id, status=None):
        with self._lock:
            relevant = {OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY}
            return [deepcopy(o) for o in sorted(self._orders.values(), key=lambda x: x["created_at"], reverse=True)
                    if o["hub_id"] == hub_id and o["status"] in (relevant if status is None else {status})]

    def get(self, order_id):
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                raise HTTPException(status_code=404, detail="Order not found")
            return deepcopy(order)

    def decide(self, order_id, decision, reason=None):
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                raise HTTPException(status_code=404, detail="Order not found")
            if order["status"] != OrderStatus.PENDING:
                raise HTTPException(status_code=409, detail="Only PENDING orders can be decided")
            if decision == "REJECT" and (reason is None or not reason.strip()):
                raise HTTPException(status_code=400, detail="A rejection reason is required")
            previous = order["status"]
            next_status = OrderStatus.CONFIRMED if decision == "CONFIRM" else OrderStatus.REJECTED
            order["status"] = next_status
            order["rejection_reason"] = reason.strip() if decision == "REJECT" else None
            order["status_history"].append({"status": next_status, "changed_at": now(), "note": order["rejection_reason"]})
            return {"id": order_id, "previous_status": previous, "status": next_status, "rejection_reason": order["rejection_reason"]}

    def change_status(self, order_id, next_status):
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                raise HTTPException(status_code=404, detail="Order not found")
            allowed = {OrderStatus.CONFIRMED: OrderStatus.PREPARING, OrderStatus.PREPARING: OrderStatus.READY}
            if allowed.get(order["status"]) != next_status:
                raise HTTPException(status_code=409, detail=f"Transition from {order['status']} to {next_status} is not allowed")
            previous = order["status"]
            order["status"] = next_status
            order["status_history"].append({"status": next_status, "changed_at": now(), "note": None})
            return {"id": order_id, "previous_status": previous, "status": next_status}


orders = MockOrderRepository()
