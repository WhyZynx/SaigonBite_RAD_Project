from datetime import date, datetime, timedelta
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
from app.models import Voucher


@pytest.fixture
def admin_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    previous = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    token = create_session("admin-test@example.invalid", "ADMIN", demo=True)
    client = TestClient(app)
    client.cookies.set(SESSION_COOKIE, token)
    try:
        yield client, factory
    finally:
        client.close()
        clear_session(token)
        if previous is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def voucher_payload(code="RAD20"):
    return {
        "code": code,
        "discount": "20%",
        "min_order": 50000,
        "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=7)).isoformat(),
    }


def test_uc05_create_update_and_archive(admin_client):
    client, factory = admin_client
    created = client.post("/api/vouchers", json=voucher_payload())
    assert created.status_code == 201
    voucher_id = created.json()["id"]
    assert created.json()["status"] == "ACTIVE"

    updated_payload = {**voucher_payload("RAD25"), "discount": "25%"}
    updated = client.put(f"/api/vouchers/{voucher_id}", json=updated_payload)
    assert updated.status_code == 200
    assert updated.json()["code"] == "RAD25"
    assert updated.json()["discount"] == "25%"

    archived = client.patch(f"/api/vouchers/{voucher_id}/archive")
    assert archived.status_code == 200
    assert archived.json()["status"] == "ARCHIVED"
    assert client.put(f"/api/vouchers/{voucher_id}", json=updated_payload).status_code == 409


def test_uc05_expire_and_archive_expired_voucher(admin_client):
    client, factory = admin_client
    with factory() as db:
        voucher = Voucher(
            code="OLD20", discount_type="PERCENT", discount_value=20,
            min_order=0, start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now() - timedelta(days=1), status="ACTIVE",
        )
        db.add(voucher)
        db.commit()
        voucher_id = voucher.voucher_id

    rows = client.get("/api/vouchers").json()
    expired = next(row for row in rows if row["id"] == voucher_id)
    assert expired["status"] == "EXPIRED"
    archived = client.patch(f"/api/vouchers/{voucher_id}/archive")
    assert archived.status_code == 200
    assert archived.json()["status"] == "ARCHIVED"
