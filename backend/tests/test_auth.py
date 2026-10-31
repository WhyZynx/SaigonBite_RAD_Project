import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.auth import DEMO_EMAIL, DEMO_PASSWORD, SESSION_COOKIE
from app.main import app


def test_login_success_sets_httponly_session_cookie():
    client = TestClient(app)
    response = client.post('/api/auth/login', json={'email': DEMO_EMAIL, 'password': DEMO_PASSWORD})
    assert response.status_code == 200
    assert response.json()['email'] == DEMO_EMAIL
    assert response.json()['role'] == 'KITCHEN_STAFF'
    assert response.json()['redirect_url'] == '/kitchen/'
    assert response.json()['demo'] is False
    assert SESSION_COOKIE in response.cookies
    assert 'httponly' in response.headers['set-cookie'].lower()
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 200


def test_login_failure_does_not_create_session():
    client = TestClient(app)
    response = client.post('/api/auth/login', json={'email': DEMO_EMAIL, 'password': 'incorrect'})
    assert response.status_code == 401
    assert SESSION_COOKIE not in client.cookies
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 401


def test_demo_preview_and_logout():
    client = TestClient(app)
    demo = client.post('/api/auth/demo')
    assert demo.status_code == 200 and demo.json()['demo'] is True
    assert demo.json()['role'] == 'KITCHEN_STAFF'
    assert client.get('/api/auth/me').json()['demo'] is True
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 200
    logout = client.post('/api/auth/logout')
    assert logout.status_code == 200
    assert client.get('/api/auth/me').status_code == 401
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 401


def test_unauthenticated_ui_and_order_apis_are_protected():
    client = TestClient(app)
    assert 'Sign In' in client.get('/').text
    assert client.get('/kitchen/', follow_redirects=False).status_code == 303
    assert client.get('/app.js', follow_redirects=False).status_code == 303
    assert client.get('/api/kitchen/orders?hub_id=1').status_code == 401
    assert client.patch('/api/kitchen/orders/101/decision', json={'decision':'CONFIRM'}).status_code == 401
    assert client.patch('/api/kitchen/orders/101/status', json={'status':'PREPARING'}).status_code == 401
    assert client.get('/api/orders/101').status_code == 401


def test_mock_role_routing_is_server_determined():
    from app.auth import MOCK_ACCOUNTS

    for account in MOCK_ACCOUNTS:
        client = TestClient(app)
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
        }[account['role']]
        assert client.get('/').status_code == 200
        if account['role'] in {'CUSTOMER', 'ADMIN'}:
            destination = response.json()['redirect_url']
            placeholder = client.get(destination)
            assert placeholder.status_code == 200
            assert 'not integrated yet' in placeholder.text
            assert client.get('/api/kitchen/orders?hub_id=1').status_code == 403


def test_local_development_demo_credentials_sign_in_with_expected_roles():
    client = TestClient(app)
    expected_roles = {
        'kitchen@saigonbite.com': 'KITCHEN_STAFF',
        'admin@saigonbite.com': 'ADMIN',
        'customer@saigonbite.com': 'CUSTOMER',
    }
    for email, role in expected_roles.items():
        response = client.post('/api/auth/login', json={'email': email, 'password': 'password123'})
        assert response.status_code == 200
        assert response.json()['role'] == role
