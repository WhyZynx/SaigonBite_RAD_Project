from pathlib import Path
import sys
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth import SESSION_COOKIE, clear_session, create_session
from app.database import Base, get_db
from app.main import app
from app.models import Customer, Hub, Notification, Order
from app.repositories.notification import NotificationRepository


@pytest.fixture
def notification_clients():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with testing_session() as db:
        db.add_all(
            [
                Customer(customer_id=1, customer_type="LOCAL", name="Alice", email="alice@example.invalid"),
                Customer(customer_id=2, customer_type="LOCAL", name="Bob", email="bob@example.invalid"),
                Hub(hub_id=1, name="Test Hub", address="Test address"),
            ]
        )
        db.flush()
        db.add_all(
            [
                Order(order_id=501, customer_id=1, hub_id=1, delivery_address="Alice address", delivery_distance_km=1.0, subtotal=10000, total=10000),
                Order(order_id=502, customer_id=2, hub_id=1, delivery_address="Bob address", delivery_distance_km=1.0, subtotal=10000, total=10000),
            ]
        )
        db.commit()

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    tokens = {
        "alice": create_session("alice@example.invalid", "CUSTOMER", demo=True),
        "bob": create_session("bob@example.invalid", "CUSTOMER", demo=True),
        "kitchen": create_session("kitchen-test@example.invalid", "KITCHEN_STAFF", demo=True),
    }
    clients = {role: TestClient(app) for role in tokens}
    for role, client in clients.items():
        client.cookies.set(SESSION_COOKIE, tokens[role])
    try:
        yield {"clients": clients, "session_factory": testing_session}
    finally:
        for client in clients.values():
            client.close()
        for token in tokens.values():
            clear_session(token)
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_rejection_creates_persistent_notification_for_order_owner(notification_clients):
    clients = notification_clients["clients"]
    response = clients["kitchen"].patch(
        "/api/kitchen/orders/501/decision",
        json={"decision": "REJECT", "reason": "Unavailable ingredients"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"

    alice_list = clients["alice"].get("/api/customer/notifications?customer_id=2")
    assert alice_list.status_code == 200
    assert len(alice_list.json()) == 1
    notification = alice_list.json()[0]
    assert notification["order_id"] == 501
    assert notification["is_read"] is False
    assert "Unavailable ingredients" in notification["message"]
    assert clients["alice"].get("/api/customer/notifications/unread-count").json() == {"unread_count": 1}
    assert clients["bob"].get("/api/customer/notifications").json() == []
    assert clients["bob"].get("/api/customer/notifications/unread-count").json() == {"unread_count": 0}
    with notification_clients["session_factory"]() as db:
        assert db.query(Notification).filter_by(order_id=501).count() == 1


def test_notification_read_state_and_cross_customer_access(notification_clients):
    clients = notification_clients["clients"]
    rejected = clients["kitchen"].patch(
        "/api/kitchen/orders/501/decision",
        json={"decision": "REJECT", "reason": "Closed for maintenance"},
    )
    assert rejected.status_code == 200
    notification_id = clients["alice"].get("/api/customer/notifications").json()[0]["id"]

    assert clients["bob"].patch(f"/api/customer/notifications/{notification_id}/read").status_code == 404
    assert clients["alice"].get("/api/customer/notifications/unread-count").json() == {"unread_count": 1}
    marked = clients["alice"].patch(f"/api/customer/notifications/{notification_id}/read")
    assert marked.status_code == 200 and marked.json() == {"id": notification_id, "is_read": True}
    assert clients["alice"].get("/api/customer/notifications/unread-count").json() == {"unread_count": 0}
    with notification_clients["session_factory"]() as db:
        assert db.query(Notification).filter_by(notification_id=notification_id).one().is_read is True


def test_notification_timestamp_is_returned_as_utc(notification_clients):
    clients = notification_clients["clients"]
    rejected = clients["kitchen"].patch(
        "/api/kitchen/orders/501/decision",
        json={"decision": "REJECT", "reason": "Unavailable"},
    )
    assert rejected.status_code == 200
    timestamp = clients["alice"].get("/api/customer/notifications").json()[0]["created_at"]
    parsed = datetime.fromisoformat(timestamp)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() == timedelta(0)
    assert parsed.tzinfo == timezone.utc


def test_duplicate_notification_insert_returns_existing_row(notification_clients):
    with notification_clients["session_factory"]() as db:
        repository = NotificationRepository(db)
        original = repository.create_order_rejected(501, "Unavailable")
        duplicate = repository.create_order_rejected(501, "Different retry reason")
        assert duplicate["id"] == original["id"]
        assert duplicate["message"] == original["message"]
        assert db.query(Notification).filter_by(order_id=501).count() == 1


def test_invalid_or_retried_rejection_does_not_duplicate_notification(notification_clients):
    kitchen = notification_clients["clients"]["kitchen"]
    invalid = kitchen.patch(
        "/api/kitchen/orders/501/decision",
        json={"decision": "REJECT", "reason": "   "},
    )
    assert invalid.status_code == 400
    assert kitchen.get("/api/customer/notifications").status_code == 403
    with notification_clients["session_factory"]() as db:
        assert db.query(Notification).count() == 0

    first = kitchen.patch(
        "/api/kitchen/orders/501/decision",
        json={"decision": "REJECT", "reason": "Unavailable"},
    )
    retry = kitchen.patch(
        "/api/kitchen/orders/501/decision",
        json={"decision": "REJECT", "reason": "Unavailable"},
    )
    assert first.status_code == 200
    assert retry.status_code == 409
    with notification_clients["session_factory"]() as db:
        assert db.query(Notification).filter_by(order_id=501).count() == 1


def test_notification_storage_failure_does_not_reverse_successful_rejection(notification_clients, monkeypatch):
    def fail_notification_insert(self, order_id, reason):
        raise OperationalError("INSERT INTO notifications", {}, RuntimeError("database unavailable"))

    monkeypatch.setattr(NotificationRepository, "create_order_rejected", fail_notification_insert)
    response = notification_clients["clients"]["kitchen"].patch(
        "/api/kitchen/orders/501/decision",
        json={"decision": "REJECT", "reason": "Unavailable"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"
    with notification_clients["session_factory"]() as db:
        order = db.query(Order).filter_by(order_id=501).one()
        assert order.status == "REJECTED"
        assert db.query(Notification).filter_by(order_id=501).count() == 0


def test_notification_endpoints_require_customer_session(notification_clients):
    unauthenticated = TestClient(app)
    try:
        assert unauthenticated.get("/api/customer/notifications").status_code == 401
        assert unauthenticated.get("/api/customer/notifications/unread-count").status_code == 401
        assert unauthenticated.patch("/api/customer/notifications/1/read").status_code == 401
    finally:
        unauthenticated.close()
