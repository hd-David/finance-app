# Finance App Backend

This is the backend API for the Finance App, built with Flask. It provides REST API endpoints for a React + Axios frontend.

## Features

- 🔐 JWT-based authentication
- 📊 Stock portfolio management
- 💰 Buy and sell stocks
- 📈 Real-time stock quotes (Alpha Vantage API)
- 📜 Transaction history
- 🌐 CORS-enabled for frontend integration
- 🔄 Backward compatible with template-based routes

## Prerequisites

- Python 3.7+
- pip
- Alpha Vantage API key (get one free at https://www.alphavantage.co/support/#api-key)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the backend directory:
```env
API_KEY=your_alpha_vantage_api_key_here
JWT_SECRET_KEY=your_secure_random_string_here
```

3. Initialize the database:
```bash
python init_db.py
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed API endpoint documentation.

### Quick Reference

#### Public Endpoints
- `GET /api/trending` - Get trending stocks

#### Authentication Endpoints
- `POST /api/register` - Register new user
- `POST /api/login` - Login and get JWT token
- `POST /api/logout` - Logout

#### Protected Endpoints (Require JWT Token)
- `GET /api/user` - Get current user info
- `GET /api/portfolio` - Get user's portfolio
- `POST /api/quote` - Get stock quote
- `POST /api/buy` - Buy stocks
- `POST /api/sell` - Sell stocks
- `GET /api/history` - Get transaction history

## Testing the API

### Using the Test Script

```bash
# Make sure the server is running first
python test_api.py
```

### Using curl

```bash
# Register a user
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123","full_names":"Test User"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"testuser","password":"test123"}'

# Get portfolio (replace YOUR_TOKEN with the token from login)
curl -X GET http://localhost:5000/api/portfolio \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Project Structure

```
backend/
├── app.py              # Main Flask application with API endpoints
├── model.py            # Database models (User, Portfolio, Transaction)
├── helpers.py          # Helper functions (lookup, usd formatter)
├── create.py           # User creation helpers
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── finance.db          # SQLite database (created after init_db.py)
├── API_DOCUMENTATION.md # Detailed API documentation
├── README.md           # This file
└── test_api.py         # API testing script
```

## Frontend Integration

The backend is configured to work with React frontends running on:
- `http://localhost:3000` (Create React App)
- `http://localhost:5173` (Vite)

CORS is enabled for these origins with the following methods: GET, POST, PUT, DELETE, OPTIONS

### Axios Example

```javascript
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: 'http://localhost:5000',
});

// Add JWT token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Use the API
async function getPortfolio() {
  const response = await api.get('/api/portfolio');
  return response.data;
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY` | Alpha Vantage API key for stock data | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Optional (auto-generated if not provided) |
| `DATABASE_URL` | Database connection URL | Optional (defaults to `sqlite:///finance.db`) |

## Database Schema

### User Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email
- `password_hash` - Hashed password
- `full_names` - Full name
- `cash` - Available cash (default: 10000)
- `create_date` - Account creation date

### Portfolio Table
- `id` - Primary key
- `user_id` - Foreign key to User
- `symbol` - Stock symbol
- `quantity` - Number of shares
- `price` - Last purchase price

### Transaction Table
- `id` - Primary key
- `user_id` - Foreign key to User
- `symbol` - Stock symbol
- `quantity` - Number of shares
- `price` - Transaction price
- `transaction_type` - BUY or SELL
- `timestamp` - Transaction time

## Notes

- JWT tokens expire after 24 hours
- Initial user balance is $10,000
- Stock prices are fetched in real-time from Alpha Vantage
- The API maintains backward compatibility with the original template-based routes

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "API_KEY not found"
Make sure you've created a `.env` file with your Alpha Vantage API key.

### CORS errors from frontend
Check that your frontend is running on one of the allowed origins (localhost:3000 or localhost:5173). If using a different port, update the CORS configuration in `app.py`.

### Database errors
Re-initialize the database:
```bash
rm finance.db
python init_db.py
```
