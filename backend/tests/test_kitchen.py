import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import Base, get_db
from app.main import app
from app.models import Brand, Customer, Hub, MenuItem, Order, OrderItem, OrderStatusHistory


@pytest.fixture
def client():
    # An in-memory database shared by TestClient's request threads; it never connects
    # to or changes the configured team MySQL database.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add_all(
        [
            Customer(customer_id=1, customer_type="LOCAL", name="Test Customer", phone="0900000001"),
            Hub(hub_id=1, name="Central", address="HCMC"),
            Hub(hub_id=2, name="East", address="HCMC"),
            MenuItem(menu_item_id=1, hub_id=1, brand_id=1, name="Pho", price=50000),
        ]
    )
    # Satisfy menu_items.brand_id with a real shared model row.
    db.add(Brand(brand_id=1, name="SaigonBite"))
    db.flush()
    for order_id, hub_id, status in [
        (106, 1, "PENDING"),
        (107, 1, "CONFIRMED"),
        (108, 1, "PREPARING"),
        (109, 2, "READY"),
        (105, 1, "REJECTED"),
    ]:
        db.add(
            Order(
                order_id=order_id,
                customer_id=1,
                hub_id=hub_id,
                status=status,
                delivery_address="District 1",
                delivery_distance_km=2.0,
                payment_method="COD",
                subtotal=50000,
                total=65000,
            )
        )
    db.flush()
    for order_id in (106, 107, 108, 109, 105):
        db.add(OrderItem(order_id=order_id, menu_item_id=1, quantity=1, unit_price=50000))
        db.add(
            OrderStatusHistory(
                order_id=order_id,
                old_status=None,
                new_status="PENDING",
            )
        )
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    test_client.post("/api/auth/demo")
    test_client._kitchen_test_session_factory = TestingSession
    try:
        yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_list_filters_orders_by_hub_and_status(client):
    expected_by_status = {
        "PENDING": [106],
        "CONFIRMED": [107],
        "PREPARING": [108],
        "READY": [],
        "REJECTED": [105],
    }
    for status, expected_ids in expected_by_status.items():
        response = client.get(f"/api/kitchen/orders?hub_id=1&status={status}")
        assert response.status_code == 200
        assert [order["id"] for order in response.json()] == expected_ids
    all_kitchen = client.get("/api/kitchen/orders?hub_id=1")
    assert {order["status"] for order in all_kitchen.json()} == {"PENDING", "CONFIRMED", "PREPARING"}
    assert client.get("/api/kitchen/orders?hub_id=2").json()[0]["id"] == 109


def test_home_and_kitchen_frontend_assets_after_login(client):
    home = client.get("/", follow_redirects=True)
    kitchen = client.get("/kitchen/")
    javascript = client.get("/app.js")
    assert home.status_code == 200 and "SaigonBite" in home.text
    assert kitchen.status_code == 200 and "Kitchen" in kitchen.text
    assert javascript.status_code == 200 and "refreshOrders" in javascript.text


def test_confirm_order_creates_history(client):
    response = client.patch("/api/kitchen/orders/106/decision", json={"decision": "CONFIRM"})
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"
    # Query the isolated database to prove both status and matching history were persisted.
    response = client.get("/api/kitchen/orders?hub_id=1&status=CONFIRMED")
    assert response.status_code == 200
    assert any(order["id"] == 106 for order in response.json())
    with client._kitchen_test_session_factory() as db:
        history = db.query(OrderStatusHistory).filter_by(order_id=106).order_by(OrderStatusHistory.history_id).all()
        assert [(entry.old_status, entry.new_status, entry.reason) for entry in history][-1] == (
            "PENDING", "CONFIRMED", None
        )
    detail = client.get("/api/orders/106")
    assert detail.status_code == 200
    order = detail.json()
    assert order["status"] == "CONFIRMED"
    assert order["customer_name"] == "Test Customer"
    assert order["customer_phone"] == "0900000001"
    assert order["delivery_address"] == "District 1"
    assert order["delivery_distance_km"] == 2.0
    assert order["items"][0] == {
        "menu_item_id": 1,
        "name": "Pho",
        "quantity": 1,
        "unit_price": 50000,
        "line_total": 50000,
    }
    assert order["subtotal"] == 50000
    assert order["delivery_fee"] == 0
    assert order["surcharge"] == 0
    assert order["discount"] == 0
    assert order["total"] == 65000
    assert order["payment_method"] == "COD"
    assert order["payment_status"] == "UNPAID"
    assert [entry["status"] for entry in order["status_history"]][-1] == "CONFIRMED"
    assert order["rejection_reason"] is None
    assert "customer_note" not in order
    assert "options" not in order["items"][0]


def test_reject_with_reason_and_history(client):
    response = client.patch(
        "/api/kitchen/orders/106/decision",
        json={"decision": "REJECT", "reason": "  Ingredient unavailable  "},
    )
    assert response.status_code == 200
    assert response.json()["rejection_reason"] == "Ingredient unavailable"
    with client._kitchen_test_session_factory() as db:
        history = db.query(OrderStatusHistory).filter_by(order_id=106).order_by(OrderStatusHistory.history_id).all()
        assert (history[-1].old_status, history[-1].new_status, history[-1].reason) == (
            "PENDING", "REJECTED", "Ingredient unavailable"
        )
    detail = client.get("/api/orders/106")
    assert detail.status_code == 200
    assert detail.json()["rejection_reason"] == "Ingredient unavailable"


def test_reject_without_reason(client):
    response = client.patch("/api/kitchen/orders/106/decision", json={"decision": "REJECT", "reason": "  "})
    assert response.status_code == 400


def test_preparation_transitions_and_history(client):
    preparing = client.patch("/api/kitchen/orders/107/status", json={"status": "PREPARING"})
    ready = client.patch("/api/kitchen/orders/108/status", json={"status": "READY"})
    assert preparing.status_code == 200 and preparing.json()["status"] == "PREPARING"
    assert ready.status_code == 200 and ready.json()["status"] == "READY"
    assert client.get("/api/orders/107").json()["status"] == "PREPARING"
    assert client.get("/api/orders/108").json()["status"] == "READY"
    with client._kitchen_test_session_factory() as db:
        preparing_history = db.query(OrderStatusHistory).filter_by(order_id=107).order_by(OrderStatusHistory.history_id).all()
        ready_history = db.query(OrderStatusHistory).filter_by(order_id=108).order_by(OrderStatusHistory.history_id).all()
        assert (preparing_history[-1].old_status, preparing_history[-1].new_status) == ("CONFIRMED", "PREPARING")
        assert (ready_history[-1].old_status, ready_history[-1].new_status) == ("PREPARING", "READY")


def test_invalid_transition_and_missing_order(client):
    assert client.patch("/api/kitchen/orders/107/status", json={"status": "READY"}).status_code == 409
    assert client.patch("/api/kitchen/orders/99999/decision", json={"decision": "CONFIRM"}).status_code == 404
    assert client.patch("/api/kitchen/orders/99999/status", json={"status": "PREPARING"}).status_code == 404
