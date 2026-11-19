from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth import SESSION_COOKIE, clear_session, create_session
from app.database import Base, get_db
from app.main import app
from app.models import Brand, Customer, Hub, MenuItem
from app.schemas import CreateOrderRequest


@pytest.fixture
def customer_client():
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
                Customer(
                    customer_id=1,
                    customer_type="LOCAL",
                    name="Customer Test12334",
                    phone="0900000001",
                ),
                Hub(hub_id=1, name="Test Hub", address="Test address"),
                Brand(brand_id=1, name="Test Brand"),
            ]
        )
        db.flush()
        db.add(MenuItem(menu_item_id=1, hub_id=1, brand_id=1, name="Test item", price=50000))
        db.commit()

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    token = create_session("customer-test@example.invalid", "CUSTOMER", demo=True)
    client = TestClient(app)
    client.cookies.set(SESSION_COOKIE, token)
    try:
        yield client
    finally:
        client.close()
        clear_session(token)
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_delivery_address_limit_matches_database_column():
    payload = {
        "customer_id": 1,
        "hub_id": 1,
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": "A" * 255,
        "delivery_distance_km": 3.5,
        "payment_method": "COD",
    }

    assert CreateOrderRequest(**payload).delivery_address == "A" * 255

    with pytest.raises(ValidationError):
        CreateOrderRequest(**{**payload, "delivery_address": "A" * 256})


def test_delivery_contact_string_round_trips_to_order_detail(customer_client):
    delivery_address = (
        "Test street 12\n"
        "Recipient: Customer Test12334\n"
        "Phone: 324324\n"
        "Note: 1111111"
    )
    response = customer_client.post(
        "/api/orders",
        json={
            "customer_id": 1,
            "hub_id": 1,
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "delivery_address": delivery_address,
            "delivery_distance_km": 8.25,
            "payment_method": "COD",
        },
    )

    assert response.status_code == 201
    order_id = response.json()["id"]
    detail_response = customer_client.get(f"/api/orders/{order_id}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["delivery_address"] == delivery_address
    assert detail["customer_name"] == "Customer Test12334"
    assert detail["customer_phone"] == "0900000001"
    # The current API intentionally stores the demo distance configured by the router.
    assert detail["delivery_distance_km"] == 3.5
