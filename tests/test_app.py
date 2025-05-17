import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
import pytest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success(client):
    response = client.post('/login', json={'username': 'user1', 'password': 'pass123'})
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_login_fail(client):
    response = client.post('/login', json={'username': 'user1', 'password': 'wrongpass'})
    assert response.status_code == 401

def test_get_balance_authorized(client):
    login_res = client.post('/login', json={'username': 'user1', 'password': 'pass123'})
    token = login_res.get_json()['token']
    response = client.get('/balance', headers={'Authorization': token})
    assert response.status_code == 200
    assert 'balance' in response.get_json()

def test_get_balance_unauthorized(client):
    response = client.get('/balance')
    assert response.status_code == 401

def test_transaction_deposit(client):
    login_res = client.post('/login', json={'username': 'user1', 'password': 'pass123'})
    token = login_res.get_json()['token']
    response = client.post('/transaction', json={'amount': 100}, headers={'Authorization': token})
    assert response.status_code == 200
    assert response.get_json()['balance'] >= 1000

def test_transaction_withdraw_success(client):
    login_res = client.post('/login', json={'username': 'user1', 'password': 'pass123'})
    token = login_res.get_json()['token']
    response = client.post('/transaction', json={'amount': -200}, headers={'Authorization': token})
    assert response.status_code == 200

def test_transaction_overdraft_fail(client):
    login_res = client.post('/login', json={'username': 'user1', 'password': 'pass123'})
    token = login_res.get_json()['token']
    response = client.post('/transaction', json={'amount': -10000}, headers={'Authorization': token})
    assert response.status_code == 400
    assert response.get_json()['error'] == "Overdraft not allowed"
