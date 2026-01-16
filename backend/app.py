import os
from flask import Flask, request, jsonify
from helpers import *
from create import *
from model import dbconnect, User, Transaction, Portfolio
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
    access_token = create_access_token(identity=user.id)
    
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

@app.route("/api/portfolio", methods=["GET"])
@jwt_required()
def api_get_portfolio():
    """API endpoint to get user's portfolio"""
    user_id = get_jwt_identity()
    
    # Get portfolio data
    portfolio_data = get_portfolio_data(user_id)
    
    # Get user's cash
    user = session_db.query(User).get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Calculate totals
    stock_value = sum(stock['total_value'] for stock in portfolio_data)
    grand_total = stock_value + user.cash
    
    return jsonify({
        "portfolio": portfolio_data,
        "cash": float(user.cash),
        "stock_value": float(stock_value),
        "total": float(grand_total)
    }), 200


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
def buy(symbol, quantity):
    stock_info = lookup(symbol)
    if stock_info is None:
        return "Invalid symbol"
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return "Quantity must be positive"
    except ValueError:
        return "Invalid quantity"
    
    # 1. Use session_db.get() to remove the LegacyAPIWarning
    user = session_db.get(User, user.id)
    
    # 2. Convert to float to avoid TypeError in tests
    current_cash = float(user.cash)
    unit_price = float(stock_info["price"])
    total_cost = unit_price * quantity
    
    if total_cost > current_cash:
        return "Insufficient funds"
    
    # 3. Apply the subtraction
    user.cash = current_cash - total_cost
    
    # Portfolio logic... (Keep your existing logic below this)
    existing_portfolio = session_db.query(Portfolio).filter_by(user_id=user.id, symbol=symbol).first()
    if existing_portfolio:
        existing_portfolio.quantity += quantity
        existing_portfolio.price = unit_price
    else:
        portfolio = Portfolio(user_id=user.id, symbol=symbol, quantity=quantity, price=unit_price)
        session_db.add(portfolio)
    
    # Record the transaction
    transaction = Transaction(
        user_id=user.id,
        symbol=symbol,
        quantity=quantity,
        price=unit_price,
        transaction_type='BUY'
    )
    session_db.add(transaction)
    session_db.commit()
   
    return "Success"
    
@app.route("/api/buy", methods=["POST"])
@jwt_required()
def api_buy():
    """The endpoint your frontend/tests talk to."""
    user_id = get_jwt_identity() 
    data = request.get_json()
    
    if not data or 'symbol' not in data or 'quantity' not in data:
        return jsonify({"error": "Missing symbol or quantity"}), 400

    # Call the fixed helper
    result = buy_for_user(user_id, data['symbol'], data['quantity'])

    if result == "success":
        # Return 200 for React success
        return jsonify({"message": "Purchase successful"}), 200
    else:
        # Return 400 with the specific error (e.g., "Insufficient funds") 
        # This matches what your pytest: assert response.json['error'] == "..."
        return jsonify({"error": result}), 400
    
    
@app.route("/api/sell", methods=["POST"])
@jwt_required()
def api_sell():
    """API endpoint to sell stocks"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
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

# Helper functions for API endpoints
def buy_for_user(user_id, symbol, quantity):
    """Buy stocks for a specific user (used by API)"""
    stock_info = lookup(symbol)
    if stock_info is None:
        return "Invalid symbol"
    
    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return "Quantity must be positive"
    except ValueError:
        return "Invalid quantity"
    
    user = session_db.query(User).get(user_id)
    if not user:
        return "User not found"
    
    budget = user.cash
    if stock_info["price"] * quantity > budget:
        return "Insufficient funds"
    
    # Purchase stock
    total_cost = stock_info["price"] * quantity
    user.cash -= total_cost
    
    # Check if user already owns this stock
    existing_portfolio = session_db.query(Portfolio).filter_by(user_id=user.id, symbol=symbol).first()
    if existing_portfolio:
        existing_portfolio.quantity += quantity
        existing_portfolio.price = stock_info["price"]
    else:
        portfolio = Portfolio(user_id=user.id, symbol=symbol, quantity=quantity, price=stock_info["price"])
        session_db.add(portfolio)
    
    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        symbol=symbol,
        quantity=quantity,
        price=stock_info["price"],
        transaction_type='BUY'
    )
    session_db.add(transaction)
    session_db.commit()
    
    return "Success"

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
    total_revenue = stock_info["price"] * quantity
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

# ============================================
# END OF REST API ENDPOINTS
# ============================================
        
if __name__ == '__main__':
    app.run(debug=True)
