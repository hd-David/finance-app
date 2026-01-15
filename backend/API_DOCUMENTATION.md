# Finance App Backend API Documentation

This document describes the REST API endpoints available for the React + Axios frontend.

## Base URL
```
http://localhost:5000
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After logging in, you'll receive an access token that should be included in the Authorization header for protected endpoints:

```
Authorization: Bearer <your_access_token>
```

## API Endpoints

### 1. User Registration

**Endpoint:** `POST /api/register`

**Description:** Register a new user account

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword",
  "full_names": "John Doe"
}
```

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_names": "John Doe"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Missing required fields or invalid data
- `400 Bad Request` - Email or username already exists

---

### 2. User Login

**Endpoint:** `POST /api/login`

**Description:** Login to get an access token

**Authentication:** Not required

**Request Body:**
```json
{
  "username_or_email": "johndoe",
  "password": "securepassword"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_names": "John Doe",
    "cash": 10000.0
  }
}
```

**Error Responses:**
- `400 Bad Request` - Missing username/email or password
- `401 Unauthorized` - Invalid credentials

---

### 3. User Logout

**Endpoint:** `POST /api/logout`

**Description:** Logout user (frontend should remove token)

**Authentication:** Required

**Success Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

### 4. Get User Information

**Endpoint:** `GET /api/user`

**Description:** Get current user's information

**Authentication:** Required

**Success Response (200):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_names": "John Doe",
  "cash": 10000.0
}
```

**Error Responses:**
- `404 Not Found` - User not found

---

### 5. Get Portfolio

**Endpoint:** `GET /api/portfolio`

**Description:** Get user's stock portfolio and financial summary

**Authentication:** Required

**Success Response (200):**
```json
{
  "portfolio": [
    {
      "symbol": "AAPL",
      "company_name": "AAPL",
      "price": 150.25,
      "shares": 10,
      "total_value": 1502.50
    },
    {
      "symbol": "TSLA",
      "company_name": "TSLA",
      "price": 245.80,
      "shares": 5,
      "total_value": 1229.00
    }
  ],
  "cash": 7268.50,
  "stock_value": 2731.50,
  "total": 10000.0
}
```

---

### 6. Get Stock Quote

**Endpoint:** `POST /api/quote`

**Description:** Get current price and information for a stock

**Authentication:** Required

**Request Body:**
```json
{
  "symbol": "AAPL",
  "quantity": 5
}
```

**Success Response (200):**
```json
{
  "name": "AAPL",
  "symbol": "AAPL",
  "price": 150.25,
  "quantity": 5,
  "order_price": 751.25
}
```

**Error Responses:**
- `400 Bad Request` - Missing symbol or invalid quantity
- `404 Not Found` - Invalid stock symbol

---

### 7. Buy Stock

**Endpoint:** `POST /api/buy`

**Description:** Purchase shares of a stock

**Authentication:** Required

**Request Body:**
```json
{
  "symbol": "AAPL",
  "quantity": 5
}
```

**Success Response (200):**
```json
{
  "message": "Stock purchased successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Missing symbol/quantity, invalid data, or insufficient funds

---

### 8. Sell Stock

**Endpoint:** `POST /api/sell`

**Description:** Sell shares of a stock

**Authentication:** Required

**Request Body:**
```json
{
  "symbol": "AAPL",
  "quantity": 3
}
```

**Success Response (200):**
```json
{
  "message": "Stock sold successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Missing symbol/quantity, don't own stock, or not enough shares

---

### 9. Get Transaction History

**Endpoint:** `GET /api/history`

**Description:** Get user's transaction history

**Authentication:** Required

**Success Response (200):**
```json
{
  "transactions": [
    {
      "id": 1,
      "symbol": "AAPL",
      "quantity": 5,
      "price": 150.25,
      "transaction_type": "BUY",
      "timestamp": "2026-01-15T21:00:00"
    },
    {
      "id": 2,
      "symbol": "TSLA",
      "quantity": 3,
      "price": 245.80,
      "transaction_type": "SELL",
      "timestamp": "2026-01-15T20:30:00"
    }
  ]
}
```

---

### 10. Get Trending Stocks

**Endpoint:** `GET /api/trending`

**Description:** Get trending stocks with price change information (Public endpoint)

**Authentication:** Not required

**Success Response (200):**
```json
{
  "stocks": [
    {
      "name": "AAPL",
      "price": 150.25,
      "change": 2.5
    },
    {
      "name": "TSLA",
      "price": 245.80,
      "change": -1.2
    },
    {
      "name": "NVDA",
      "price": 520.30,
      "change": 5.7
    },
    {
      "name": "SOFI",
      "price": 8.45,
      "change": 0.5
    }
  ]
}
```

---

## CORS Configuration

The backend is configured to accept requests from the following origins:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:3000`
- `http://127.0.0.1:5173`

These cover common development ports for React (Create React App uses 3000, Vite uses 5173).

## Using Axios

### Example: Login Request

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

async function login(username, password) {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/login`, {
      username_or_email: username,
      password: password
    });
    
    // Store the token
    localStorage.setItem('access_token', response.data.access_token);
    
    return response.data;
  } catch (error) {
    console.error('Login error:', error.response.data);
    throw error;
  }
}
```

### Example: Authenticated Request

```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Example: Get portfolio
async function getPortfolio() {
  try {
    const response = await api.get('/api/portfolio');
    return response.data;
  } catch (error) {
    console.error('Error fetching portfolio:', error.response.data);
    throw error;
  }
}

// Example: Buy stock
async function buyStock(symbol, quantity) {
  try {
    const response = await api.post('/api/buy', {
      symbol: symbol,
      quantity: quantity
    });
    return response.data;
  } catch (error) {
    console.error('Error buying stock:', error.response.data);
    throw error;
  }
}
```

## Running the Backend

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables (create a `.env` file):
```
API_KEY=your_alpha_vantage_api_key
JWT_SECRET_KEY=your_jwt_secret_key_here
```

3. Initialize the database:
```bash
python init_db.py
```

4. Run the Flask application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## Notes

- The JWT access token expires after 24 hours
- All monetary values are returned as floats
- Stock prices are fetched from Alpha Vantage API
- Initial user balance is $10,000
- All timestamps are in ISO 8601 format
