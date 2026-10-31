import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
client.post('/api/auth/demo')


def test_list_filter_and_frontend():
    pending = client.get('/api/kitchen/orders?hub_id=1&status=PENDING')
    assert pending.status_code == 200 and len(pending.json()) == 2
    assert client.get('/api/kitchen/orders?hub_id=2').json()[0]['id'] == 106
    assert client.get('/api/kitchen/orders?hub_id=1&status=READY').json()[0]['status'] == 'READY'
    page = client.get('/')
    assert page.status_code == 200 and 'SaigonBite' in page.text
    assert client.get('/app.js').status_code == 200


def test_decision_and_history():
    result = client.patch('/api/kitchen/orders/101/decision', json={'decision':'CONFIRM'})
    assert result.status_code == 200 and result.json()['status'] == 'CONFIRMED'
    detail = client.get('/api/orders/101').json()
    assert [entry['status'] for entry in detail['status_history']] == ['PENDING','CONFIRMED']
    assert client.patch('/api/kitchen/orders/101/decision', json={'decision':'CONFIRM'}).status_code == 409


def test_reject_validation_and_recording():
    assert client.patch('/api/kitchen/orders/102/decision', json={'decision':'REJECT'}).status_code == 400
    response = client.patch('/api/kitchen/orders/102/decision', json={'decision':'REJECT','reason':'Ingredient unavailable'})
    assert response.status_code == 200 and response.json()['rejection_reason'] == 'Ingredient unavailable'
    history = client.get('/api/orders/102').json()['status_history']
    assert history[-1]['status'] == 'REJECTED' and history[-1]['note'] == 'Ingredient unavailable'


def test_preparation_transitions_and_conflicts():
    assert client.patch('/api/kitchen/orders/103/status', json={'status':'READY'}).status_code == 409
    assert client.patch('/api/kitchen/orders/103/status', json={'status':'PREPARING'}).status_code == 200
    assert client.patch('/api/kitchen/orders/103/status', json={'status':'READY'}).json()['status'] == 'READY'
    assert client.get('/api/orders/103').json()['status_history'][-1]['status'] == 'READY'
    assert client.patch('/api/kitchen/orders/103/status', json={'status':'CONFIRMED'}).status_code == 409


def test_unknown_order():
    assert client.get('/api/orders/99999').status_code == 404
    assert client.patch('/api/kitchen/orders/99999/decision', json={'decision':'CONFIRM'}).status_code == 404
