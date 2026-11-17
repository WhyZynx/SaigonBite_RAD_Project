from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    PREPARING = "PREPARING"
    READY = "READY"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class Decision(str, Enum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"


class DecisionRequest(BaseModel):
    decision: Decision
    reason: str | None = None


class StatusRequest(BaseModel):
    status: OrderStatus


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class StatusHistoryEntry(BaseModel):
    status: OrderStatus
    changed_at: datetime
    note: str | None = None


class OrderItem(BaseModel):
    menu_item_id: int
    name: str
    quantity: int
    unit_price: int
    line_total: int


class OrderSummary(BaseModel):
    id: int
    customer_id: int
    hub_id: int
    status: OrderStatus
    total: int
    created_at: datetime


class OrderDetail(OrderSummary):
    customer_name: str | None = None
    customer_phone: str | None = None
    items: list[OrderItem]
    delivery_address: str
    delivery_distance_km: float
    voucher_code: str | None = None
    payment_method: str
    payment_status: str
    subtotal: int
    delivery_fee: int
    surcharge: int
    discount: int
    rejection_reason: str | None = None
    status_history: list[StatusHistoryEntry]


class DecisionResponse(BaseModel):
    id: int
    previous_status: OrderStatus
    status: OrderStatus
    rejection_reason: str | None = None


class StatusResponse(BaseModel):
    id: int
    previous_status: OrderStatus
    status: OrderStatus
