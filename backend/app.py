from decimal import Decimal
import os
from flask import Flask, request, jsonify
from helpers import *
from create import *
from model import dbconnect, User, Transaction, Portfolio,init_db
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta


# Configure application

app = Flask(__name__, static_folder="static")

# CORS configuration for React frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})


session_db = dbconnect()


# Configure session_db to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
SECRET_KEY = os.urandom(64)
app.config['SECRET_KEY'] = SECRET_KEY

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', SECRET_KEY.hex())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)



# Make sure API key is set
from dotenv import load_dotenv
load_dotenv() # This loads the variables from .env into your system

api_key = os.getenv("API_KEY")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# REST API ENDPOINTS FOR REACT FRONTEND

@app.route("/api/register", methods=["POST"])
def api_register():
    """API endpoint for user registration"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'full_names']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    
    # Check if user already exists
    existing_user = session_db.query(User).filter(User.email == data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already exists"}), 400
    
    existing_username = session_db.query(User).filter(User.username == data['username']).first()
    if existing_username:
        return jsonify({"error": "Username already exists"}), 400
    
    try:
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        user = User(
            full_names=data['full_names'],
            email=data['email'],
            password_hash=hashed_password,
            username=data['username']
        )
        session_db.add(user)
        session_db.commit()
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_names": user.full_names
            }
        }), 201
    except Exception as e:
        session_db.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/login", methods=["POST"])
def api_login():
    """API endpoint for user login"""
    data = request.get_json()
    
    if not data or 'username_or_email' not in data or 'password' not in data:
        return jsonify({"error": "Username/email and password required"}), 400
    
    username_or_email = data['username_or_email']
    password = data['password']
    
    # Query for user
    user = session_db.query(User).filter(
        (User.email == username_or_email) | (User.username == username_or_email)
    ).first()
    
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    
    # Create JWT token
    access_token = create_access_token(identity = str(user.id))
    
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_names": user.full_names,
            "cash": float(user.cash)
        }
    }), 200

@app.route("/api/logout", methods=["POST"])
@jwt_required()
def api_logout():
    """API endpoint for user logout"""
    # JWT tokens are stateless, so we just return success
    # The frontend should remove the token
    return jsonify({"message": "Logout successful"}), 200
# Helper to convert DB objects to dictionaries
def portfolio_to_dict(holding):
    return {
        "symbol": holding.symbol,
        "shares": holding.shares,
        "price": float(holding.current_price), # Convert Decimal for JSON
        "total_value": float(holding.shares * holding.current_price)
    }

@app.route('/api/portfolio', methods=['GET'])
@jwt_required()
def get_portfolio():
    user_id = get_jwt_identity()
    user = session_db.get(User, int(user_id))
    
    # Check your database query for the user's stocks
    # Ensure it returns a list of objects with "symbol", "quantity", and "price"
    user_stocks = session_db.query(Portfolio).filter_by(user_id=user_id).all()
    
    holdings = []
    for s in user_stocks:
        holdings.append({
            "symbol": s.symbol,
            "quantity": s.quantity,     # <--- Must match React!
            "price": float(s.price)     # <--- Must match React!
        })
    
    total_stock_value = sum(h['quantity'] * h['price'] for h in holdings)

    return jsonify({
        "holdings": holdings,
        "total_value": float(user.cash) + total_stock_value,
        "cash": float(user.cash)
    })


@app.route("/api/quote", methods=["POST"])
@jwt_required()
def api_quote():
    data = request.get_json()

    if not data or 'symbol' not in data:
        # Changed message to match exactly what your test expects
        return jsonify({"error": "Invalid symbol"}), 400

    symbol = data['symbol'].upper()
    
    stock_info = lookup(symbol)
    if not stock_info:
        # Changed message to match exactly what your test expects
        return jsonify({"error": "Invalid symbol"}), 400 

    return jsonify({
        "name": stock_info.get("name", symbol), 
        "symbol": stock_info["symbol"],
        "price": float(stock_info["price"])
    }), 200
    
    
# HELPER FUNCTIONS FOR API ENDPOINTS
def buy_for_user(user_id, symbol, quantity):
    stock_info = lookup(symbol)
    if stock_info is None:
        return "Invalid symbol"

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return "Quantity must be positive"
    except (ValueError, TypeError):
        return "Invalid quantity"

    # Correct user lookup
    user = session_db.get(User, user_id)
    if not user:
        return "User not found"

   # Convert everything to Decimal
    current_cash = Decimal(user.cash)
    unit_price = Decimal(str(stock_info["price"]))
    total_cost = unit_price * quantity

    if total_cost > current_cash:
        return "Insufficient funds"

    # Deduct cash
    user.cash = current_cash - Decimal(str(total_cost))
    # Portfolio logic
    existing_portfolio = session_db.query(Portfolio).filter_by(
        user_id=user.id, symbol=symbol
    ).first()

    if existing_portfolio:
        existing_portfolio.quantity += quantity
        existing_portfolio.price = unit_price
    else:
        portfolio = Portfolio(
            user_id=user.id,
            symbol=symbol,
            quantity=quantity,
            price=unit_price
        )
        session_db.add(portfolio)

    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        symbol=symbol,
        quantity=quantity,
        price=unit_price,
        transaction_type="BUY"
    )
    session_db.add(transaction)

    session_db.commit()

    return "success"

@app.route("/api/buy", methods=["POST"])
@jwt_required()
def api_buy():
    user_id = int(get_jwt_identity())  # IMPORTANT
    data = request.get_json()

    if not data or "symbol" not in data or "quantity" not in data:
        return jsonify({"error": "Missing symbol or quantity"}), 400

    result = buy_for_user(user_id, data["symbol"], data["quantity"])

    if result == "success":
        return jsonify({"message": "Purchase successful"}), 200
    else:
        return jsonify({"error": result}), 400

    
    
@app.route("/api/sell", methods=["POST"])
@jwt_required()
def api_sell():
    """API endpoint to sell stocks"""
    user_id = get_jwt_identity()
    data = request.get_json()
    print(f"DEBUG: Received symbol to sell: '{data['symbol']}'")
    
    if not data or 'symbol' not in data or 'quantity' not in data:
        return jsonify({"error": "Symbol and quantity required"}), 400
    
    symbol = data['symbol']
    quantity = data['quantity']
    
    # Call existing sell function
    result = sell_for_user(user_id, symbol, quantity)
    
    if result == "Success":
        return jsonify({"message": "Stock sold successfully"}), 200
    else:
        return jsonify({"error": result}), 400

@app.route("/api/history", methods=["GET"])
@jwt_required()
def api_history():
    """API endpoint to get transaction history"""
    user_id = get_jwt_identity()
    
    # Get all transactions for the user
    transactions = session_db.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
    
    # Convert to JSON-serializable format
    transaction_list = []
    for t in transactions:
        transaction_list.append({
            "id": t.id,
            "symbol": t.symbol,
            "quantity": t.quantity,
            "price": float(t.price),
            "transaction_type": t.transaction_type,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None
        })
    
    return jsonify({"transactions": transaction_list}), 200

@app.route("/api/trending", methods=["GET"])
def api_trending():
    """API endpoint to get trending stocks (public endpoint)"""
    market_data = get_trending_stocks()
    return jsonify({"stocks": market_data}), 200

@app.route("/api/user", methods=["GET"])
@jwt_required()
def api_get_user():
    """API endpoint to get current user info"""
    user_id = get_jwt_identity()
    user = session_db.query(User).get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_names": user.full_names,
        "cash": float(user.cash)
    }), 200


def sell_for_user(user_id, symbol, quantity):
    """Sell shares of stock for a specific user (used by API)"""
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return "Quantity must be positive"
    except ValueError:
        return "Invalid quantity"
    
    user = session_db.query(User).get(user_id)
    if not user:
        return "User not found"
    
    # Check if user owns this stock
    portfolio_entry = session_db.query(Portfolio).filter_by(user_id=user.id, symbol=symbol).first()
    
    if not portfolio_entry:
        return "You don't own this stock"
    
    if portfolio_entry.quantity < quantity:
        return "Not enough shares"
    
    # Get current stock price
    stock_info = lookup(symbol)
    if stock_info is None:
        return "Invalid symbol"
    
    # Sell stock
    total_revenue = Decimal(stock_info["price"]) * Decimal(quantity)
    user.cash += total_revenue
    
    # Update portfolio
    portfolio_entry.quantity -= quantity
    if portfolio_entry.quantity == 0:
        session_db.delete(portfolio_entry)
    
    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        symbol=symbol,
        quantity=quantity,
        price=stock_info["price"],
        transaction_type='SELL'
    )
    session_db.add(transaction)
    session_db.commit()
    
    return "Success"
@app.route("/api/market-snapshot")
def get_market_snapshot():
    symbols = ["AAPL", "TSLA", "MSFT", "IBM", "GOOGL"]
    # 🟢 High-end fallback data to use when API is blocked
    mock_data = {
        "AAPL": 185.92, 
        "TSLA": 171.05, 
        "MSFT": 415.50, 
        "IBM": 190.20, 
        "GOOGL": 154.30
    }
    market_data = []

    for symbol in symbols:
        price = lookup(symbol)
        
        # If API returns 0 or None, use our mock_data
        if not price or price == 0:
            price = mock_data.get(symbol, 100.00)
            print(f"⚠️ API Limit hit for {symbol}. Using mock price: {price}")

        market_data.append({
            "symbol": symbol,
            "price": price
        })
    
    return jsonify(market_data)
# ============================================
# END OF REST API ENDPOINTS
# ============================================
        
if __name__ == '__main__':
    app.run(debug=True)
