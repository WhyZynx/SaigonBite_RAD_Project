import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.auth import DEMO_EMAIL, DEMO_PASSWORD, SESSION_COOKIE
from app.database import Base, get_db
from app.main import app
from app.models import Brand, Customer, Hub, MenuItem, Order, OrderItem


@pytest.fixture
def client():
    """Use isolated SQLite for every auth test that may reach database endpoints."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with testing_session() as db:
        db.add_all([
            Customer(customer_id=1, customer_type="LOCAL", name="Auth Test Customer"),
            Hub(hub_id=1, name="Auth Test Hub", address="HCMC"),
            Brand(brand_id=1, name="Auth Test Brand"),
        ])
        db.flush()
        db.add(MenuItem(menu_item_id=1, hub_id=1, brand_id=1, name="Test item", price=1000))
        db.flush()
        db.add(Order(
            order_id=101,
            customer_id=1,
            hub_id=1,
            status="PENDING",
            delivery_address="HCMC",
            delivery_distance_km=1,
            payment_method="COD",
            subtotal=1000,
            total=1000,
        ))
        db.flush()
        db.add(OrderItem(order_id=101, menu_item_id=1, quantity=1, unit_price=1000))
        db.commit()

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_login_success_sets_httponly_session_cookie(client):
    response = client.post('/api/auth/login', json={'email': DEMO_EMAIL, 'password': DEMO_PASSWORD})
    assert response.status_code == 200
    assert response.json()['email'] == DEMO_EMAIL
    assert response.json()['role'] == 'KITCHEN_STAFF'
    assert response.json()['redirect_url'] == '/kitchen/'
    assert response.json()['demo'] is False
    assert SESSION_COOKIE in response.cookies
    assert 'httponly' in response.headers['set-cookie'].lower()
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 200


def test_login_failure_does_not_create_session(client):
    response = client.post('/api/auth/login', json={'email': DEMO_EMAIL, 'password': 'incorrect'})
    assert response.status_code == 401
    assert SESSION_COOKIE not in client.cookies
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 401


def test_demo_preview_and_logout(client):
    demo = client.post('/api/auth/demo')
    assert demo.status_code == 200 and demo.json()['demo'] is True
    assert demo.json()['role'] == 'KITCHEN_STAFF'
    assert client.get('/api/auth/me').json()['demo'] is True
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 200
    logout = client.post('/api/auth/logout')
    assert logout.status_code == 200
    assert client.get('/api/auth/me').status_code == 401
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 401


def test_unauthenticated_ui_and_order_apis_are_protected(client):
    assert 'Sign In' in client.get('/').text
    assert client.get('/kitchen/', follow_redirects=False).status_code == 303
    assert client.get('/app.js', follow_redirects=False).status_code == 303
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 401
    assert client.patch('/api/kitchen/orders/101/decision', json={'decision':'CONFIRM'}).status_code == 401
    assert client.patch('/api/kitchen/orders/101/status', json={'status':'PREPARING'}).status_code == 401
    assert client.get('/api/orders/101').status_code == 401


def test_mock_role_routing_is_server_determined(client):
    from app.auth import MOCK_ACCOUNTS

    for account in MOCK_ACCOUNTS:
        response = client.post('/api/auth/login', json={
            'email': account['email'],
            'password': account['password'],
            'role': 'ADMIN' if account['role'] != 'ADMIN' else 'CUSTOMER',
        })
        assert response.status_code == 200
        assert response.json()['role'] == account['role']
        assert response.json()['redirect_url'] == {
            'CUSTOMER': '/customer/',
            'KITCHEN_STAFF': '/kitchen/',
            'ADMIN': '/admin/',
            'MANAGER': '/manager/',
        }[account['role']]
        assert client.get('/').status_code == 200
        if account['role'] in {'CUSTOMER', 'ADMIN'}:
            destination = response.json()['redirect_url']
            portal = client.get(destination)
            assert portal.status_code == 200
            if account['role'] == 'CUSTOMER':
                assert '<title>Order Food | SaigonBite</title>' in portal.text
                assert client.get('/customer/app.js').status_code == 200
            else:
                assert 'ADMIN PORTAL' in portal.text
            assert client.get('/api/kitchen/orders?hub_id=1').status_code == 403


def test_local_development_demo_credentials_sign_in_with_expected_roles(client):
    expected_roles = {
        'kitchen@saigonbite.com': 'KITCHEN_STAFF',
        'admin@saigonbite.com': 'ADMIN',
        'customer@saigonbite.com': 'CUSTOMER',
    }
    for email, role in expected_roles.items():
        response = client.post('/api/auth/login', json={'email': email, 'password': 'password123'})
        assert response.status_code == 200
        assert response.json()['role'] == role
