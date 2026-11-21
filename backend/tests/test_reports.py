
from datetime import date, datetime, time, timedelta
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth import SESSION_COOKIE, clear_session, create_session
from app.database import Base, get_db
from app.main import app
from app.models import (
    Customer,
    Delivery,
    Hub,
    Order,
    OrderStatusHistory,
)


@pytest.fixture
def api_environment():
    """
    All API tests use isolated in-memory SQLite.
    No connection is made to the team's MySQL database.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    testing_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    clients = []
    tokens = []

    def make_client(role: str):
        token = create_session(
            f"{role.lower()}-test@example.invalid",
            role,
            demo=True,
        )
        client = TestClient(app)
        client.cookies.set(SESSION_COOKIE, token)

        clients.append(client)
        tokens.append(token)

        return client

    try:
        yield make_client, testing_session
    finally:
        for client in clients:
            client.close()

        for token in tokens:
            clear_session(token)

        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override

        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def seed_base_data(db):
    customer = Customer(
        customer_id=1,
        customer_type="LOCAL",
        name="Report Test Customer",
        email="report-customer@example.invalid",
        phone="0900000001",
    )

    hub1 = Hub(
        hub_id=1,
        name="Central Hub",
        address="District 1, HCMC",
    )

    hub2 = Hub(
        hub_id=2,
        name="East Hub",
        address="Thu Duc, HCMC",
    )

    db.add_all([customer, hub1, hub2])
    db.commit()


def add_order(
    db,
    order_id: int,
    hub_id: int,
    status: str,
    created_at: datetime,
):
    order = Order(
        order_id=order_id,
        customer_id=1,
        hub_id=hub_id,
        status=status,
        delivery_address="Test delivery address",
        delivery_distance_km=2.0,
        payment_method="COD",
        payment_status="UNPAID",
        subtotal=100000,
        delivery_fee=0,
        surcharge=0,
        discount=0,
        total=100000,
        created_at=created_at,
    )

    db.add(order)
    db.commit()

    return order


def report_url(report_type: str, report_day: date):
    day = report_day.isoformat()
    return (
        f"/api/reports/{report_type}"
        f"?start_date={day}&end_date={day}"
    )


def test_admin_delivered_is_counted_without_shipper_pickup(api_environment):
    make_client, factory = api_environment
    report_day = date.today()
    created_at = datetime.combine(report_day, time(9, 0))

    with factory() as db:
        seed_base_data(db)

        add_order(
            db,
            order_id=501,
            hub_id=1,
            status="READY",
            created_at=created_at,
        )

    admin = make_client("ADMIN")

    delivered = admin.patch("/api/admin/orders/501/deliver")

    assert delivered.status_code == 200
    assert delivered.json()["previous_status"] == "READY"
    assert delivered.json()["status"] == "DELIVERED"

    # A second delivery attempt must be rejected.
    repeated = admin.patch("/api/admin/orders/501/deliver")
    assert repeated.status_code == 409

    with factory() as db:
        order = db.get(Order, 501)
        delivery = db.query(Delivery).filter_by(order_id=501).one()

        history = (
            db.query(OrderStatusHistory)
            .filter_by(order_id=501)
            .all()
        )

        assert order.status == "DELIVERED"
        assert delivery.outcome == "DELIVERED"
        assert delivery.delivered_at is not None

        # No real shipper/pickup workflow is implemented.
        assert delivery.pickup_at is None

        delivered_history = [
            row for row in history
            if row.old_status == "READY"
            and row.new_status == "DELIVERED"
        ]
        assert len(delivered_history) == 1

    manager = make_client("MANAGER")
    response = manager.get(report_url("delivery", report_day))

    assert response.status_code == 200

    data = response.json()

    assert data["kpis"][0] == {
        "label": "Total Deliveries",
        "value": "1",
    }
    assert data["kpis"][1] == {
        "label": "Completed Deliveries",
        "value": "1",
    }

    # Completion is known, but delivery duration cannot be measured
    # because there is no pickup_at timestamp.
    assert data["kpis"][2] == {
        "label": "Avg. Delivery Time",
        "value": "—",
    }

    assert data["rows"][0]["col2"] == "1"
    assert data["rows"][0]["col3"] == "—"
    assert data["rows"][0]["chartVal"] == 1


def test_delivery_report_separates_total_completed_and_duration(api_environment):
    make_client, factory = api_environment
    report_day = date.today()
    created_at = datetime.combine(report_day, time(9, 0))

    with factory() as db:
        seed_base_data(db)

        # Completed, but no pickup timestamp (Admin demo).
        add_order(db, 601, 1, "DELIVERED", created_at)
        db.add(
            Delivery(
                order_id=601,
                outcome="DELIVERED",
                pickup_at=None,
                delivered_at=created_at + timedelta(minutes=40),
            )
        )

        # Completed with both timestamps: duration is measurable.
        add_order(db, 602, 1, "DELIVERED", created_at)
        db.add(
            Delivery(
                order_id=602,
                outcome="DELIVERED",
                pickup_at=created_at + timedelta(minutes=10),
                delivered_at=created_at + timedelta(minutes=40),
            )
        )

        # Not completed.
        add_order(db, 603, 2, "PREPARING", created_at)
        db.add(
            Delivery(
                order_id=603,
                outcome="IN_TRANSIT",
                pickup_at=created_at,
                delivered_at=None,
            )
        )

        # Invalid negative duration: completed outcome is still counted,
        # but this record must not affect average delivery time.
        add_order(db, 604, 2, "DELIVERED", created_at)
        db.add(
            Delivery(
                order_id=604,
                outcome="DELIVERED",
                pickup_at=created_at + timedelta(minutes=50),
                delivered_at=created_at + timedelta(minutes=40),
            )
        )

        db.commit()

    manager = make_client("MANAGER")
    response = manager.get(report_url("delivery", report_day))

    assert response.status_code == 200

    data = response.json()

    assert data["kpis"][0]["value"] == "4"
    assert data["kpis"][1]["value"] == "3"

    # Only the valid 30-minute interval contributes to the average.
    assert data["kpis"][2]["value"] == "30 mins"

    assert len(data["rows"]) == 1
    assert data["rows"][0]["col2"] == "4"
    assert data["rows"][0]["col3"] == "30 mins"
    assert data["rows"][0]["chartVal"] == 3


def test_hub_workload_counts_orders_by_hub_and_status(api_environment):
    make_client, factory = api_environment
    report_day = date.today()
    created_at = datetime.combine(report_day, time(9, 0))

    with factory() as db:
        seed_base_data(db)

        add_order(db, 701, 1, "DELIVERED", created_at)
        add_order(db, 702, 1, "READY", created_at)
        add_order(db, 703, 2, "PREPARING", created_at)

        db.add_all([
            OrderStatusHistory(
                order_id=701,
                old_status="READY",
                new_status="DELIVERED",
                reason="Test history",
                changed_at=created_at + timedelta(minutes=20),
            ),
            OrderStatusHistory(
                order_id=702,
                old_status="PREPARING",
                new_status="READY",
                reason="Test history",
                changed_at=created_at + timedelta(minutes=15),
            ),
        ])
        db.commit()

    manager = make_client("MANAGER")
    response = manager.get(report_url("hub-workload", report_day))

    assert response.status_code == 200

    data = response.json()

    assert data["kpis"] == [
        {"label": "Total Hub Orders", "value": "3"},
        {"label": "Completed Orders", "value": "1"},
        {"label": "Hubs with Orders", "value": "2"},
    ]

    rows_by_hub = {
        row["col1"]: row
        for row in data["rows"]
    }

    assert rows_by_hub["Central Hub"]["col2"] == "2"
    assert rows_by_hub["Central Hub"]["col3"] == "1"
    assert rows_by_hub["Central Hub"]["col4"] == "1"

    assert rows_by_hub["East Hub"]["col2"] == "1"
    assert rows_by_hub["East Hub"]["col3"] == "0"
    assert rows_by_hub["East Hub"]["col4"] == "1"

    assert data["statusHistoryRecords"] == 2


def test_manager_reports_reject_invalid_date_range(api_environment):
    make_client, _ = api_environment
    manager = make_client("MANAGER")

    response = manager.get(
        "/api/reports/delivery"
        "?start_date=2026-11-22&end_date=2026-11-21"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid time range"


def test_admin_and_manager_roles_are_enforced(api_environment):
    make_client, _ = api_environment

    admin = make_client("ADMIN")
    manager = make_client("MANAGER")

    # Admin cannot access Manager reports.
    assert admin.get(
        "/api/reports/delivery"
        "?start_date=2026-11-21&end_date=2026-11-21"
    ).status_code == 403

    # Manager cannot execute Admin delivery actions.
    assert manager.patch(
        "/api/admin/orders/501/deliver"
    ).status_code == 403
