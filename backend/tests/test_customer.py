from datetime import datetime, timedelta
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
from app import delivery_fee_service
from app.main import app
from app.models import Brand, Customer, Hub, MenuItem, Voucher
from app.schemas import CreateOrderRequest


@pytest.fixture
def customer_client(monkeypatch):
    monkeypatch.setattr(delivery_fee_service, "_geocode", lambda address: (10.0, 20.0))
    monkeypatch.setattr(delivery_fee_service, "_geocode_params", lambda params: (10.0, 20.0))
    monkeypatch.setattr(delivery_fee_service, "_route_distance_meters", lambda *coords: 1_000.0)
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
                    email="customer-test@example.invalid",
                    phone="0900000001",
                ),
                Customer(
                    customer_id=2,
                    customer_type="TOURIST",
                    name="Second Customer",
                    email="second-customer@example.invalid",
                    phone="0900000002",
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
        "hub_id": 1,
        "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": "A" * 255,
        "payment_method": "COD",
    }

    assert CreateOrderRequest(**payload).delivery_address == "A" * 255

    with pytest.raises(ValidationError):
        CreateOrderRequest(**{**payload, "delivery_address": "A" * 256})


def test_delivery_contact_string_round_trips_to_order_detail(customer_client):
    delivery_address = (
        "Test street 12\n"
        "Recipient: Customer Test12334\n"
        "Phone: 0903243240\n"
        "Note: 1111111"
    )
    response = customer_client.post(
        "/api/orders",
        json={
            "hub_id": 1,
            "destination_address": "18 Nguyen Hue Street, District 1",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "delivery_address": delivery_address,
            "payment_method": "COD",
        },
    )

    assert response.status_code == 201
    order_id = response.json()["id"]
    detail_response = customer_client.get(f"/api/orders/{order_id}")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["delivery_address"] == "18 Nguyen Hue Street, District 1\n" + delivery_address
    assert detail["customer_name"] == "Customer Test12334"
    assert detail["customer_phone"] == "0900000001"
    assert detail["delivery_distance_km"] == 1.0
    assert detail["payment_method"] == "COD"
    assert detail["status"] == "PENDING"
    assert [entry["status"] for entry in detail["status_history"]] == ["PENDING"]


def test_customer_can_list_order_and_view_chronological_status_history(customer_client):
    created = customer_client.post("/api/orders", json={
        "hub_id": 1,
        "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": "House 12\nRecipient: Customer Test12334\nPhone: 0900000001",
        "payment_method": "COD",
    })
    assert created.status_code == 201
    order_id = created.json()["id"]

    order_list = customer_client.get("/api/customer/orders")
    assert order_list.status_code == 200
    listed_order = next(order for order in order_list.json() if order["id"] == order_id)
    assert listed_order["customer_id"] == 1
    assert listed_order["hub_id"] == 1
    assert listed_order["status"] == "PENDING"
    assert listed_order["total"] == created.json()["total"]

    initial_detail = customer_client.get(f"/api/orders/{order_id}")
    assert initial_detail.status_code == 200
    detail = initial_detail.json()
    assert detail["id"] == order_id
    assert detail["hub_id"] == 1
    assert detail["payment_method"] == "COD"
    assert detail["items"] == [{
        "menu_item_id": 1,
        "name": "Test item",
        "quantity": 1,
        "unit_price": 50000,
        "line_total": 50000,
    }]
    assert detail["status"] == "PENDING"
    assert [entry["status"] for entry in detail["status_history"]] == ["PENDING"]

    cancelled = customer_client.post(f"/api/customer/orders/{order_id}/cancel")
    assert cancelled.status_code == 200

    updated_detail = customer_client.get(f"/api/orders/{order_id}")
    assert updated_detail.status_code == 200
    updated_order = updated_detail.json()
    assert updated_order["status"] == "CANCELLED"
    assert [entry["status"] for entry in updated_order["status_history"]] == ["PENDING", "CANCELLED"]
    timestamps = [entry["changed_at"] for entry in updated_order["status_history"]]
    assert timestamps == sorted(timestamps)


def test_customer_can_validate_and_apply_voucher(customer_client):
    # The fixture's database is reached through the overridden session factory; seed
    # through the same dependency so the endpoint sees this voucher.
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        now = datetime.now()
        db.add(Voucher(code="SAVE10", discount_type="PERCENT", discount_value=10,
                       min_order=80000, start_date=now - timedelta(days=1),
                       end_date=now + timedelta(days=1), status="ACTIVE"))
        db.commit()
    finally:
        db.close()
        db_generator.close()

    preview = customer_client.post("/api/customer/vouchers/validate", json={
        "code": "save10", "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 2}],
    })
    assert preview.status_code == 200
    assert preview.json() == {
        "code": "SAVE10", "subtotal": 100000, "discount": 10000,
        "delivery_fee": 13000, "delivery_distance_km": 1.0, "surcharge": 0, "total": 103000,
    }

    rejected = customer_client.post("/api/customer/vouchers/validate", json={
        "code": "SAVE10", "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
    })
    assert rejected.status_code == 400
    assert rejected.json()["detail"] == (
        "Minimum order for this voucher is 80,000 VND. Add 30,000 VND more to apply it."
    )

    order = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 2}],
        "delivery_address": "Test street 12\nRecipient: Customer Test12334\nPhone: 0900000001",
        "voucher_code": "SAVE10", "payment_method": "COD",
    })
    assert order.status_code == 201
    assert order.json()["discount"] == 10000
    assert order.json()["total"] == 103000

    reuse_preview = customer_client.post("/api/customer/vouchers/validate", json={
        "code": "SAVE10", "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 2}],
    })
    assert reuse_preview.status_code == 400
    assert reuse_preview.json()["detail"] == "You have already used this voucher on a previous order"


def test_demo_delivery_survives_map_failure_for_quote_voucher_and_order(customer_client, monkeypatch):
    def map_unavailable(*_args, **_kwargs):
        raise delivery_fee_service.ProviderRequestError("Could not connect to Nominatim")

    monkeypatch.setattr(delivery_fee_service, "_hub_coordinates", map_unavailable)
    quote = customer_client.post("/api/delivery-quote", json={
        "hub_id": 1, "delivery_address": "19 Nguyen Huu Tho, District 7",
    })
    assert quote.status_code == 502

    demo_quote = customer_client.post("/api/delivery-quote", json={
        "hub_id": 1, "delivery_address": "19 Nguyen Huu Tho, District 7",
        "demo_delivery": True,
    })
    assert demo_quote.status_code == 200
    assert demo_quote.json() == {
        "delivery_distance_km": delivery_fee_service.DEMO_DELIVERY_DISTANCE_KM,
        "delivery_fee": delivery_fee_service.DEMO_DELIVERY_FEE_VND,
        "surcharge": delivery_fee_service.DEMO_DELIVERY_SURCHARGE_VND,
        "is_demo": True,
    }

    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        now = datetime.now()
        db.add(Voucher(code="DEMO10", discount_type="PERCENT", discount_value=10,
                       min_order=80000, start_date=now - timedelta(days=1),
                       end_date=now + timedelta(days=1), status="ACTIVE"))
        db.commit()
    finally:
        db.close()
        db_generator.close()

    voucher = customer_client.post("/api/customer/vouchers/validate", json={
        "code": "DEMO10", "hub_id": 1,
        "destination_address": "19 Nguyen Huu Tho, District 7",
        "demo_delivery": True,
        "items": [{"menu_item_id": 1, "quantity": 2}],
    })
    assert voucher.status_code == 200
    assert voucher.json()["is_demo"] is True
    assert voucher.json()["delivery_distance_km"] == delivery_fee_service.DEMO_DELIVERY_DISTANCE_KM
    assert voucher.json()["delivery_fee"] == delivery_fee_service.DEMO_DELIVERY_FEE_VND

    order = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "19 Nguyen Huu Tho, District 7",
        "items": [{"menu_item_id": 1, "quantity": 2}],
        "delivery_address": "Recipient: Customer Test12334\nPhone: 0900000001",
        "voucher_code": "DEMO10", "demo_delivery": True,
    })
    assert order.status_code == 201
    assert order.json()["delivery_distance_km"] == delivery_fee_service.DEMO_DELIVERY_DISTANCE_KM
    assert order.json()["delivery_fee"] == delivery_fee_service.DEMO_DELIVERY_FEE_VND
    assert order.json()["total"] == (
        100_000 + delivery_fee_service.DEMO_DELIVERY_FEE_VND
        + delivery_fee_service.DEMO_DELIVERY_SURCHARGE_VND - 10_000
    )


def test_demo_delivery_can_be_chosen_when_nominatim_does_not_find_address(customer_client, monkeypatch):
    def no_address(*_args, **_kwargs):
        raise delivery_fee_service.NoGeocodingResult("no matching address")

    monkeypatch.setattr(delivery_fee_service, "_geocode_customer_address", no_address)
    actual_quote = customer_client.post("/api/delivery-quote", json={
        "hub_id": 1, "delivery_address": "20/15/1 Me Coc",
    })
    assert actual_quote.status_code == 400

    demo_quote = customer_client.post("/api/delivery-quote", json={
        "hub_id": 1, "delivery_address": "20/15/1 Me Coc", "demo_delivery": True,
    })
    assert demo_quote.status_code == 200
    assert demo_quote.json()["is_demo"] is True


@pytest.mark.parametrize(("details", "message"), [
    ("Phone: 0900000001", "Recipient name is required"),
    ("Recipient: Customer Test12334", "Delivery phone number is required"),
])
def test_order_rejects_missing_recipient_or_phone_before_quote(customer_client, monkeypatch, details, message):
    def quote_must_not_run(*_args, **_kwargs):
        pytest.fail("delivery quote must not run for invalid contact details")

    monkeypatch.setattr(delivery_fee_service.DeliveryFeeService, "calculate", quote_must_not_run)
    response = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": details,
    })
    assert response.status_code == 422
    assert response.json()["detail"] == message


def test_order_rejects_combined_address_over_255_before_quote(customer_client, monkeypatch):
    def quote_must_not_run(*_args, **_kwargs):
        pytest.fail("delivery quote must not run for an overlong combined address")

    monkeypatch.setattr(delivery_fee_service.DeliveryFeeService, "calculate", quote_must_not_run)
    response = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "A" * 230,
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": "Recipient: Customer Test12334\nPhone: 0900000001",
    })
    assert response.status_code == 422
    assert "maximum 255 characters" in response.json()["detail"]


@pytest.mark.parametrize("phone", ["1234567890123456", "090abc1234"])
def test_order_rejects_overlong_or_malformed_phone_before_quote(customer_client, monkeypatch, phone):
    def quote_must_not_run(*_args, **_kwargs):
        pytest.fail("delivery quote must not run for an invalid phone number")

    monkeypatch.setattr(delivery_fee_service.DeliveryFeeService, "calculate", quote_must_not_run)
    response = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": f"Recipient: Customer Test12334\nPhone: {phone}",
    })
    assert response.status_code == 422
    assert response.json()["detail"] == "Enter a valid delivery phone number with 9 to 15 digits"


def test_customer_voucher_page_lists_only_currently_available_codes(customer_client):
    db_generator = app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        now = datetime.now()
        db.add_all([
            Voucher(code="SAVE10", discount_type="PERCENT", discount_value=10,
                    min_order=80000, start_date=now - timedelta(days=1),
                    end_date=now + timedelta(days=10), status="ACTIVE"),
            Voucher(code="ARCHIVED", discount_type="FIXED", discount_value=5000,
                    min_order=0, start_date=now - timedelta(days=1),
                    end_date=now + timedelta(days=10), status="ARCHIVED"),
        ])
        db.commit()
    finally:
        db.close()
        db_generator.close()

    response = customer_client.get("/api/customer/vouchers")
    assert response.status_code == 200
    assert [voucher["code"] for voucher in response.json()] == ["SAVE10"]
    assert response.json()[0]["min_order"] == 80000

    order = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 2}],
        "delivery_address": "House 12\nRecipient: Customer Test12334\nPhone: 0900000001",
        "voucher_code": "SAVE10", "payment_method": "COD",
    })
    assert order.status_code == 201
    response_after_use = customer_client.get("/api/customer/vouchers")
    assert response_after_use.status_code == 200
    assert response_after_use.json() == []


def test_customer_can_cancel_only_own_pending_order(customer_client):
    order = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": "House 12\nRecipient: Customer Test12334\nPhone: 0900000001",
        "payment_method": "COD",
    })
    assert order.status_code == 201
    order_id = order.json()["id"]

    cancelled = customer_client.post(f"/api/customer/orders/{order_id}/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json() == {"id": order_id, "previous_status": "PENDING", "status": "CANCELLED"}

    detail = customer_client.get(f"/api/orders/{order_id}").json()
    assert detail["status"] == "CANCELLED"
    assert [entry["status"] for entry in detail["status_history"]] == ["PENDING", "CANCELLED"]
    history_timestamps = [entry["changed_at"] for entry in detail["status_history"]]
    assert history_timestamps == sorted(history_timestamps)
    assert detail["status_history"][-1]["status"] == "CANCELLED"
    assert detail["status_history"][-1]["note"] == "Cancelled by customer"

    repeated_cancel = customer_client.post(f"/api/customer/orders/{order_id}/cancel")
    assert repeated_cancel.status_code == 409

    other_token = create_session("second-customer@example.invalid", "CUSTOMER", demo=False)
    customer_client.cookies.set(SESSION_COOKIE, other_token)
    try:
        other_cancel = customer_client.post(f"/api/customer/orders/{order_id}/cancel")
        assert other_cancel.status_code == 404
    finally:
        customer_client.cookies.delete(SESSION_COOKIE)
        clear_session(other_token)


def test_customer_identity_maps_from_session_email(customer_client):
    first_profile = customer_client.get("/api/customer/profile")
    assert first_profile.status_code == 200
    assert first_profile.json()["id"] == 1
    assert first_profile.json()["customer_type"] == "LOCAL"

    first_order = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": "First customer address\nRecipient: Customer Test12334\nPhone: 0900000001",
        "payment_method": "COD",
    })
    assert first_order.status_code == 201

    second_token = create_session("second-customer@example.invalid", "CUSTOMER", demo=False)
    customer_client.cookies.set(SESSION_COOKIE, second_token)
    try:
        second_profile = customer_client.get("/api/customer/profile")
        assert second_profile.status_code == 200
        assert second_profile.json()["id"] == 2
        assert second_profile.json()["name"] == "Second Customer"
        assert second_profile.json()["customer_type"] == "TOURIST"
        assert customer_client.get("/api/customer/orders").json() == []
        assert customer_client.get(f"/api/orders/{first_order.json()['id']}").status_code == 404
        missing_order = customer_client.get("/api/orders/999999")
        assert missing_order.status_code == 404
        assert missing_order.json()["detail"] == "Order not found"

        second_order = customer_client.post("/api/orders", json={
            "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
            "items": [{"menu_item_id": 1, "quantity": 1}],
            "delivery_address": "Second customer address\nRecipient: Second Customer\nPhone: 0900000002",
            "payment_method": "COD",
        })
        assert second_order.status_code == 201
        assert customer_client.get("/api/customer/orders").json()[0]["customer_id"] == 2
    finally:
        customer_client.cookies.delete(SESSION_COOKIE)
        clear_session(second_token)


def test_customer_account_without_matching_profile_is_rejected(customer_client):
    unknown_token = create_session("unknown@example.invalid", "CUSTOMER", demo=False)
    customer_client.cookies.set(SESSION_COOKIE, unknown_token)
    try:
        response = customer_client.get("/api/customer/profile")
        assert response.status_code == 403
    finally:
        customer_client.cookies.delete(SESSION_COOKIE)
        clear_session(unknown_token)


def test_customer_order_requires_delivery_phone(customer_client):
    missing_phone = customer_client.post("/api/orders", json={
        "hub_id": 1, "destination_address": "18 Nguyen Hue Street, District 1",
        "items": [{"menu_item_id": 1, "quantity": 1}],
        "delivery_address": "Address details\nRecipient: Customer Test12334\nPhone:   ",
        "payment_method": "COD",
    })
    assert missing_phone.status_code == 422
    assert missing_phone.json()["detail"] == "Delivery phone number is required"
