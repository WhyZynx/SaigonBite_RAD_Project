"""Temporary process-local order repository. Replace this adapter with MySQL later."""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from threading import RLock

from fastapi import HTTPException

from app.schemas import OrderStatus

TZ = timezone(timedelta(hours=7))


def now():
    return datetime.now(TZ)


class MockOrderRepository:
    def __init__(self):
        self._lock = RLock()
        # Start with a clean demo dataset. Only orders created in this session appear.
        self._orders = {}
        self._next_id = 1

    def create(self, *, customer_id, hub_id, items, delivery_address, payment_method):
        with self._lock:
            hub = HUBS_BY_ID.get(hub_id)
            if not hub or not hub["accepting_orders"]:
                raise HTTPException(status_code=400, detail="This hub is not accepting orders")
            item_by_id = {item["id"]: item for item in MENU_ITEMS if item["hub_id"] == hub_id}
            if not items:
                raise HTTPException(status_code=400, detail="At least one menu item is required")
            order_items = []
            for requested in items:
                menu_item = item_by_id.get(requested.menu_item_id)
                if not menu_item or not menu_item["is_available"]:
                    raise HTTPException(status_code=400, detail="A menu item is unavailable")
                order_items.append({"menu_item_id": menu_item["id"], "name": menu_item["name"],
                                    "quantity": requested.quantity, "unit_price": menu_item["price"],
                                    "line_total": menu_item["price"] * requested.quantity})
            subtotal = sum(item["line_total"] for item in order_items)
            order_id = self._next_id
            self._next_id += 1
            created = now()
            order = {"id": order_id, "customer_id": customer_id, "hub_id": hub_id,
                     "status": OrderStatus.PENDING, "total": subtotal + DELIVERY_FEE,
                     "created_at": created, "items": order_items,
                     "delivery_address": delivery_address, "delivery_distance_km": 0.0,
                     "voucher_code": None, "payment_method": payment_method,
                     "payment_status": "UNPAID", "subtotal": subtotal,
                     "delivery_fee": DELIVERY_FEE, "surcharge": 0, "discount": 0,
                     "rejection_reason": None,
                     "status_history": [{"status": OrderStatus.PENDING, "changed_at": created, "note": None}]}
            self._orders[order_id] = order
            return deepcopy(order)

    def list_orders(self, hub_id, status=None):
        with self._lock:
            relevant = {OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY}
            return [deepcopy(o) for o in sorted(self._orders.values(), key=lambda x: x["created_at"], reverse=True)
                    if o["hub_id"] == hub_id and o["status"] in (relevant if status is None else {status})]

    def list_customer_orders(self, customer_id):
        with self._lock:
            return [deepcopy({key: order[key] for key in ("id", "customer_id", "hub_id", "status", "total", "created_at")})
                    for order in sorted(self._orders.values(), key=lambda item: item["created_at"], reverse=True)
                    if order["customer_id"] == customer_id]

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

HUBS = [
    {"id": 1, "name": "Anrakutei", "address": "315 Nguyễn Hữu Thọ, Tân Phong, Quận 7", "accepting_orders": True,
     "description": "Japanese barbecue", "description_vi": "Nhà hàng thịt nướng Nhật Bản", "icon": "grill", "location_label": "Nguyễn Hữu Thọ", "cuisine": "Japanese BBQ"},
    {"id": 2, "name": "Wrap & Roll · SC VivoCity", "address": "Tầng 4, SC VivoCity, 1058 Nguyễn Văn Linh", "accepting_orders": True,
     "description": "Vietnamese rolls & home-style dishes", "description_vi": "Món cuốn và món Việt", "icon": "rolls", "location_label": "SC VivoCity · Tầng 4", "cuisine": "Vietnamese"},
    {"id": 3, "name": "Cô Thanh Noodles · SC VivoCity", "address": "Tầng 4, SC VivoCity, 1058 Nguyễn Văn Linh", "accepting_orders": True,
     "description": "Vietnamese noodles", "description_vi": "Các món mì và phở Việt", "icon": "noodles", "location_label": "SC VivoCity · Tầng 4", "cuisine": "Noodles"},
    {"id": 4, "name": "Cơm Tấm Cali 15 · SC VivoCity", "address": "Tầng 4, SC VivoCity, 1058 Nguyễn Văn Linh", "accepting_orders": True,
     "description": "Southern Vietnamese broken rice", "description_vi": "Cơm tấm kiểu miền Nam", "icon": "rice", "location_label": "SC VivoCity · Tầng 4", "cuisine": "Vietnamese rice"},
    {"id": 5, "name": "Hoàng Yến Cuisine", "address": "Sunrise City, 23 Nguyễn Hữu Thọ, Quận 7", "accepting_orders": True,
     "description": "Vietnamese cuisine", "description_vi": "Ẩm thực Việt Nam", "icon": "restaurant", "location_label": "Sunrise City", "cuisine": "Vietnamese"},
]
HUBS_BY_ID = {hub["id"]: hub for hub in HUBS}
# The delivery pricing rule is not defined in the shared API contract yet.
DELIVERY_FEE = 0
MENU_ITEMS = [
    {"id": 1, "hub_id": 1, "name": "Mì gà", "description": "Mì nóng với thịt gà và rau", "price": 45000, "category": "Món chính", "is_available": True, "emoji": "🍜"},
    {"id": 2, "hub_id": 1, "name": "Cơm chiên", "description": "Cơm chiên trứng và rau củ", "price": 40000, "category": "Món chính", "is_available": True, "emoji": "🍛"},
    {"id": 3, "hub_id": 1, "name": "Trà sữa", "description": "Trà sữa dùng lạnh", "price": 30000, "category": "Thức uống", "is_available": True, "emoji": "🧋"},
    {"id": 4, "hub_id": 1, "name": "Cơm sườn nướng", "description": "Sườn nướng ăn kèm cơm", "price": 50000, "category": "Món chính", "is_available": True, "emoji": "🍱"},
    {"id": 5, "hub_id": 1, "name": "Mì Ý", "description": "Mì Ý sốt cà chua", "price": 45000, "category": "Món chính", "is_available": True, "emoji": "🍝"},
    {"id": 6, "hub_id": 1, "name": "Trà chanh", "description": "Trà chanh mát lạnh", "price": 20000, "category": "Thức uống", "is_available": True, "emoji": "🍋"},
    {"id": 7, "hub_id": 2, "name": "Cơm gà", "description": "Cơm gà cho bữa trưa", "price": 40000, "category": "Món chính", "is_available": True, "emoji": "🍗"},
    {"id": 8, "hub_id": 2, "name": "Gỏi cuốn", "description": "Rau tươi cuốn bánh tráng", "price": 25000, "category": "Món phụ", "is_available": True, "emoji": "🥬"},
    {"id": 9, "hub_id": 3, "name": "Cơm rau củ", "description": "Cơm ăn kèm rau củ tươi", "price": 40000, "category": "Món chính", "is_available": True, "emoji": "🥗"},
    {"id": 10, "hub_id": 4, "name": "Cơm sườn nướng", "description": "Cơm tấm sườn nướng", "price": 50000, "category": "Món chính", "is_available": True, "emoji": "🍱"},
    {"id": 11, "hub_id": 5, "name": "Cơm gà", "description": "Cơm gà dùng kèm rau", "price": 45000, "category": "Món chính", "is_available": True, "emoji": "🍗"},
]
