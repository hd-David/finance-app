import pytest
from app import app
from model import Base, dbconnect, User
from werkzeug.security import generate_password_hash, check_password_hash

# ======================================================
# FIXTURES (Setup and Teardown)
# ======================================================
from unittest.mock import patch
import pytest

@pytest.fixture(autouse=True)
def mock_lookup():
    """This stops the tests from calling the real internet"""
    with patch("app.lookup") as mocked:
        def side_effect(symbol):
            if symbol.upper() == "AAPL":
                return {"symbol": "AAPL", "price": 150.0, "name": "Apple Inc"}
            if symbol.upper() == "BRK.A":
                return {"symbol": "BRK.A", "price": 500000.0, "name": "Berkshire"}
            return None
        mocked.side_effect = side_effect
        yield mocked
        
        
@pytest.fixture
def client():
    """Configures the app for testing and provides a test client."""
    app.config['TESTING'] = True
    # Use a separate test database file so we don't wipe your real data
    app.config['DATABASE_URL'] = 'sqlite:///test_finance.db'
    
    with app.test_client() as client:
        with app.app_context():
            db = dbconnect()
            Base.metadata.drop_all(bind=db.get_bind()) # Clear old test data
            Base.metadata.create_all(bind=db.get_bind()) # Create fresh tables
            yield client
            db.close()

from flask_jwt_extended import create_access_token

@pytest.fixture
def auth_headers(client):
    """Helper fixture to register/login and return JWT headers."""
    with app.app_context():
        db = dbconnect()
        user = User(
            username="tester",
            email="test@example.com",
            full_names="Test User",
            # Manually set the hash to bypass the setter issue
            password_hash=generate_password_hash("Password123!"),
            cash=10000.0
        )
        db.add(user)
        db.commit()
        db.commit()
        db.refresh(user) # Get the generated ID
        
        # 2. Generate a token for this specific user ID
        # Adjust identity=str(user.id) or identity=user.username based on your app.py
        token = create_access_token(identity=str(user.id))
        db.close()
        
    return {"Authorization": f"Bearer {token}"}

# ======================================================
# TEST CASES
# ======================================================

def test_register_success(client):
    """Test that a new user can register."""
    payload = {
        "username": "newguy",
        "email": "new@guy.com",
        "password": "SecurePassword1!",
        "full_names": "New Guy"
    }
    response = client.post('/api/register', json=payload)
    assert response.status_code == 201
    assert response.json['message'] == "User registered successfully"

def test_login_success(client):
    """Test login returns a valid JWT token."""
    # First register
    client.post('/api/register', json={
        "username": "loginuser",
        "email": "login@test.com",
        "password": "Password123!",
        "full_names": "Login User"
    })
    # Then login
    response = client.post('/api/login', json={
        "username_or_email": "loginuser",
        "password": "Password123!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json

def test_get_user_profile(client, auth_headers):
    """Test fetching protected user data using JWT."""
    response = client.get('/api/user', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == "tester"

def test_quote_valid_symbol(client, auth_headers):
    """Test stock lookup with a real symbol."""
    response = client.post('/api/quote', 
                           json={"symbol": "AAPL"}, 
                           headers=auth_headers)
    assert response.status_code == 200
    assert response.json['symbol'] == "AAPL"
    assert "price" in response.json

def test_buy_stock_success(client, auth_headers):
    """Test purchasing a stock correctly updates balance."""
    # Assuming user starts with 10,000 cash
    buy_payload = {"symbol": "AAPL", "quantity": 2}
    response = client.post('/api/buy', json=buy_payload, headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['message'] == "BUY successful"
    
    # Verify portfolio state
    port_res = client.get('/api/portfolio', headers=auth_headers)
    assert len(port_res.json['portfolio']) == 1
    assert port_res.json['portfolio'][0]['symbol'] == "AAPL"

def test_trending_public(client):
    """Test that the trending endpoint is public (no headers needed)."""
    response = client.get('/api/trending')
    assert response.status_code == 200
    assert "stocks" in response.json
    assert isinstance(response.json['stocks'], list)

def test_insufficient_funds(client, auth_headers):
    """Test that a user cannot buy more than they can afford."""
    # Attempt to buy 1 million shares of Berkshire Hathaway
    payload = {"symbol": "BRK.A", "quantity": 15000}  # Assuming this exceeds available cash
    response = client.post('/api/buy', json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert response.json['error'] == "Insufficient funds"