import os
from flask import Flask, request, jsonify
from helpers import lookup
from model import dbconnect, User, Transaction, Portfolio
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from werkzeug.security import generate_password_hash




# Configure application
app = Flask(__name__)

# CORS configuration for React frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Database
session_db = dbconnect()

# JWT Configuration
SECRET_KEY = os.urandom(64)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', SECRET_KEY.hex())
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# ============================================
# REST API ENDPOINTS
# ============================================

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
    """API endpoint to get stock quote"""
    data = request.get_json()
    
    if not data or 'symbol' not in data:
        return jsonify({"error": "Stock symbol required"}), 400
    
    symbol = data['symbol']
    quantity = data.get('quantity', 1)
    
    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400
    except ValueError:
        return jsonify({"error": "Invalid quantity"}), 400
    
    # Lookup stock
    stock_info = lookup(symbol)
    if not stock_info:
        return jsonify({"error": "Invalid stock symbol"}), 404
    
    return jsonify({
        "name": stock_info["name"],
        "symbol": stock_info["symbol"],
        "price": float(stock_info["price"]),
        "quantity": quantity,
        "order_price": float(stock_info["price"] * quantity)
    }), 200

@app.route("/api/buy", methods=["POST"])
@jwt_required()
def api_buy():
    """API endpoint to buy stocks"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'symbol' not in data or 'quantity' not in data:
        return jsonify({"error": "Symbol and quantity required"}), 400
    
    symbol = data['symbol']
    quantity = data['quantity']
    
    # Call existing buy function
    result = buy_for_user(user_id, symbol, quantity)
    
    if result == "Success":
        return jsonify({"message": "Stock purchased successfully"}), 200
    else:
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

# ============================================
# HELPER FUNCTIONS
# ============================================

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

def get_portfolio_data(user_id):
    """Get portfolio data for a user"""
    # Retrieve the portfolio for the given user_id
    portfolio = session_db.query(Portfolio).filter_by(user_id=user_id).all()

    # Create an empty list to store the portfolio data
    portfolio_data = []

    # Iterate over each portfolio entry
    for entry in portfolio:
        # Retrieve the stock symbol and quantity from the portfolio entry
        symbol = entry.symbol
        quantity = entry.quantity

        # Use the lookup function to fetch the stock quote data for the symbol
        quote_data = lookup(symbol)

        # If the lookup was successful and quote data is available
        if quote_data:
            # Extract the company name and price from the quote data
            company_name = quote_data["name"]
            price = quote_data["price"]

            # Calculate the total value of the stock holding
            total_value = price * quantity

            # Create a dictionary with the portfolio data for this stock
            stock_data = {
                "symbol": symbol,
                "company_name": company_name,
                "price": price,
                "shares": quantity,
                "total_value": total_value,
            }

            # Add the stock data to the portfolio_data list
            portfolio_data.append(stock_data)

    # Return the portfolio data
    return portfolio_data

def get_trending_stocks():
    """Get trending stocks data"""
    symbols = ["AAPL", "TSLA", "NVDA", "SOFI"]
    stocks = []

    for symbol in symbols:
        quote = lookup(symbol)
        if not quote:
            continue

        current_price = quote["price"]
    
        # fetch last stored price
        last_price = (session_db.query(Portfolio.price).filter(Portfolio.symbol == symbol).order_by(Portfolio.price.desc()).first())

        previous_price = last_price.price if last_price is not None else current_price
    
        change = ((current_price - previous_price) / previous_price) * 100

        stocks.append({
            "name": quote["name"],
            "price": current_price,
            "change": round(change, 2)
        })

    return stocks
        
if __name__ == '__main__':
    app.run(debug=True)
