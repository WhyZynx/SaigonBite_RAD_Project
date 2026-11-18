from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_type = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    passport_number = Column(String(30), nullable=True)

    orders = relationship("Order", back_populates="customer")


class Hub(Base):
    __tablename__ = "hubs"

    hub_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    capacity = Column(Integer, default=20, nullable=False)
    status = Column(String(20), default="OPEN", nullable=False)

    menu_items = relationship("MenuItem", back_populates="hub")
    orders = relationship("Order", back_populates="hub")


class Brand(Base):
    __tablename__ = "brands"

    brand_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)

    menu_items = relationship("MenuItem", back_populates="brand")


class MenuItem(Base):
    __tablename__ = "menu_items"

    menu_item_id = Column(Integer, primary_key=True, autoincrement=True)
    hub_id = Column(
        Integer,
        ForeignKey("hubs.hub_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    brand_id = Column(
        Integer,
        ForeignKey("brands.brand_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    hub = relationship("Hub", back_populates="menu_items")
    brand = relationship("Brand", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")


class Voucher(Base):
    __tablename__ = "vouchers"

    voucher_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(String(20), nullable=False)
    discount_value = Column(Integer, nullable=False)
    min_order = Column(Integer, default=0, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False)

    orders = relationship("Order", back_populates="voucher")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(
        Integer,
        ForeignKey("customers.customer_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    hub_id = Column(
        Integer,
        ForeignKey("hubs.hub_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    voucher_id = Column(
        Integer,
        ForeignKey("vouchers.voucher_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    status = Column(String(30), default="PENDING", nullable=False)
    delivery_address = Column(String(255), nullable=False)
    delivery_distance_km = Column(Float, nullable=False)
    payment_method = Column(String(20), default="COD", nullable=False)
    payment_status = Column(String(20), default="UNPAID", nullable=False)
    subtotal = Column(Integer, nullable=False)
    delivery_fee = Column(Integer, default=0, nullable=False)
    surcharge = Column(Integer, default=0, nullable=False)
    discount = Column(Integer, default=0, nullable=False)
    total = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    hub = relationship("Hub", back_populates="orders")
    voucher = relationship("Voucher", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    delivery = relationship("Delivery", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    menu_item_id = Column(
        Integer,
        ForeignKey("menu_items.menu_item_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    old_status = Column(String(30), nullable=True)
    new_status = Column(String(30), nullable=False)
    reason = Column(String(255), nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="status_history")


class Delivery(Base):
    __tablename__ = "deliveries"

    delivery_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.order_id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )
    pickup_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    outcome = Column(String(30), default="IN_TRANSIT", nullable=False)

    order = relationship("Order", back_populates="delivery")
