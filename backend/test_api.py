"""
Simple test script to verify API endpoints are working
This can be run manually to test the backend API
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_trending_stocks():
    """Test the public trending stocks endpoint"""
    print("\n=== Testing GET /api/trending (Public endpoint) ===")
    try:
        response = requests.get(f"{BASE_URL}/api/trending", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_register():
    """Test user registration"""
    print("\n=== Testing POST /api/register ===")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_names": "Test User"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/register", json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 201, 400]  # 400 if already exists
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test user login and return token"""
    print("\n=== Testing POST /api/login ===")
    data = {
        "username_or_email": "testuser",
        "password": "testpass123"
    }
    try:
        response = requests.post(f"{BASE_URL}/api/login", json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            return response_data.get("access_token")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_user(token):
    """Test getting user info"""
    print("\n=== Testing GET /api/user (Authenticated) ===")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/user", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_portfolio(token):
    """Test getting portfolio"""
    print("\n=== Testing GET /api/portfolio (Authenticated) ===")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{BASE_URL}/api/portfolio", headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_quote(token):
    """Test stock quote"""
    print("\n=== Testing POST /api/quote (Authenticated) ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"symbol": "AAPL", "quantity": 5}
    try:
        response = requests.post(f"{BASE_URL}/api/quote", json=data, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Finance App Backend API Test Suite")
    print("=" * 60)
    print("\nNOTE: Make sure the Flask server is running on http://localhost:5000")
    print("Run: python app.py")
    
    input("\nPress Enter to start tests...")
    
    results = {}
    
    # Test public endpoint
    results['Trending Stocks'] = test_trending_stocks()
    
    # Test registration
    results['Registration'] = test_register()
    
    # Test login and get token
    token = test_login()
    results['Login'] = token is not None
    
    if token:
        # Test authenticated endpoints
        results['Get User'] = test_get_user(token)
        results['Get Portfolio'] = test_get_portfolio(token)
        results['Quote Stock'] = test_quote(token)
    else:
        print("\n⚠️  Cannot test authenticated endpoints without token")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    main()
