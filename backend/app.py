import os
from flask import Flask, flash, redirect, render_template,session, request, url_for, jsonify
from helpers import *
from create import *
from model import dbconnect, User, Address, Transaction, Portfolio
from flask_bootstrap import Bootstrap
from sqlalchemy.exc import IntegrityError
from flask_login import current_user, LoginManager, login_user, logout_user
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

session_db = dbconnect()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
bootstrap = Bootstrap(app)

# Custom filter
app.jinja_env.filters["usd"] = usd

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


@app.route("/", methods=["GET", "POST"])
def index():
    """Show portfolio of stocks"""
    if current_user.is_authenticated:
        user_id = current_user.id

        # 1. Get the stock holdings
        portfolio_data = get_portfolio_data(user_id)

        # 2. Get the available cash from the user object
        available_cash = current_user.cash

        # 3. Calculate grand total (Stocks + Cash)
        stock_value = sum(stock['total_value'] for stock in portfolio_data)
        grand_total = stock_value + available_cash

        # 4. Pass EVERYTHING to the template
        return render_template("index.html",stocks=portfolio_data,total=grand_total,cash=available_cash)

    else:
        # DYNAMIC LANDING PAGE LOGIC
        
        market_data = get_trending_stocks()

        # 3. Send the real-time data to the landing page
    return render_template("landing.html", stocks=market_data)

                                            



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = current_user.id
    
    # Get all transactions for the user, ordered by most recent
    transactions = session_db.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
    
    return render_template("history.html", transactions=transactions)

# User loader function
@login_manager.user_loader
def load_user(user_id):
    # Load and return the User object based on the user_id
    user = session_db.query(User).get(int(user_id))
    return user

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # User reached route via POST (by submitting a form via POST)
    if request.method == "POST":
        username_or_email = request.form.get("username_or_email")
        password_entered = request.form.get("password")

        if username_or_email == "":
            return "Username or email missing", 403
        elif password_entered == "":
            return "Password missing", 403

        # Query the database for the user using the full_names or email
        user = session_db.query(User).filter(
            (User.email == username_or_email) | (User.username == username_or_email)
        ).first()

        # Ensure the user exists and the password is correct
        if user is None or not user.verify_password(password_entered):
            return "Invalid username or password", 403

        # Remember which user has logged in
        login_user(user)

        # Redirect the user to the home page or any other desired page
        return redirect("/")

    # User reached route via GET (by clicking a link or via redirect)
    else:
        return render_template("page_login.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    logout_user()

    # Redirect user to login form
    return render_template("landing.html")



@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        quantity = request.form.get('number_of_shares', 1)
        
        # we check the data user entered
        if not symbol or not quantity:
            return "Missing stock symbol and number of stocks", 400
        # Negative number of stocks
        try:
            quantity = int(quantity)
            if quantity < 0:
                return "Please enter a positive number of stocks", 400
        except ValueError:
            return "Invalid quantity", 400
            
        stock_info = lookup(symbol)
        # Use lookup function to check if stock code is valid
        if not stock_info:
            return "stock code was not found, please enter a valid stock symbol", 400
        else:
            # Display the stock information to the user: Stock code, price, and stock name
            return render_template("quoted.html", name=stock_info["name"], symbol=stock_info["symbol"],  price = stock_info["price"], order_price = (stock_info["price"] * quantity), quantity=quantity)

    return render_template("quote.html")



@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell_stocks():
    if request.method == 'POST':
        symbol = request.form['ticker']
        quantity = request.form['quantity']
        
        # Call sell function
        result = sell(symbol, quantity)
        if result == "Success":
            flash("Stock sold successfully!", "success")
        else:
            flash(result, "error")
        
        return redirect(url_for('index'))
    else:
        # Get user's portfolio for the dropdown
        user_id = current_user.id
        portfolio = session_db.query(Portfolio).filter_by(user_id=user_id).all()
        return render_template('sell.html', portfolio=portfolio)

def sell(symbol, quantity):
    """Sell shares of stock"""
    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return "Quantity must be positive"
    except ValueError:
        return "Invalid quantity"
    
    user = session_db.query(User).get(current_user.id)
    
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
    
    # Record the transaction
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_names = request.form.get('full_names')
        
        # Validate inputs
        if not username or not email or not password or not full_names:
            flash('All fields are required.')
            return render_template('register.html')
        
        # Check if the user or email already exists in the database
        existing_user = session_db.query(User).filter(User.email == email).first()
        existing_username = session_db.query(User).filter(User.username == username).first()
        
        if existing_user is not None and existing_user.email == email:
            flash('This email already exists, please use a different email address.')
            return render_template('register.html')
        if existing_username is not None and existing_username.username == username:
            flash('This username already exists, please use a different username.')
            return render_template('register.html')
        
        try:
            # Create the user object
            hashed_password = generate_password_hash(password)
            user = User(
                full_names=full_names,
                email=email,
                password_hash=hashed_password,
                username=username
            )
            # Add the user to the session and commit to the database
            session_db.add(user)
            session_db.commit()

            flash('You have successfully registered.')
            return redirect(url_for('login'))
        except IntegrityError:
            # Handle the case when the username or email already exists
            session_db.rollback()
            flash('Username or email already exists. Please choose a different one.')
        except Exception as e:
            # Catch any other errors that may occur and handle them appropriately
            flash('An error occurred while registering the user: {}'.format(e))

    return render_template('register.html')




@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy_route():
    if request.method == 'POST':
        # Get user input from form
        symbol = request.form['ticker']
        quantity = request.form['quantity']
        
        # Call buy function
        result = buy(symbol, quantity)
        if result == "Success":
            flash("Stock purchased successfully!", "success")
        else:
            flash(result, "error")
        
        return redirect(url_for('index'))
    
    # Render form for GET request
    return render_template('buy.html')


def buy(symbol, quantity):
    stock_info = lookup(symbol)
    # Check if stock exists
    if stock_info is None:
        return "Invalid symbol"
    
    # Validate quantity
    try:
        quantity = int(quantity)
        if quantity <= 0:
            return "Quantity must be positive"
    except ValueError:
        return "Invalid quantity"
    
    user = session_db.query(User).get(current_user.id)
    budget = user.cash
    # Check if sufficient funds available
    if stock_info["price"] * quantity > budget:
        return "Insufficient funds"
    
    # Purchase stock
    total_cost = stock_info["price"] * quantity
    user.cash -= total_cost
    
    # Check if user already owns this stock
    existing_portfolio = session_db.query(Portfolio).filter_by(user_id=user.id, symbol=symbol).first()
    if existing_portfolio:
        # Update existing position
        existing_portfolio.quantity += quantity
        existing_portfolio.price = stock_info["price"]
    else:
        # Add new stock to user's portfolio
        portfolio = Portfolio(user_id=user.id, symbol=symbol, quantity=quantity, price=stock_info["price"])
        session_db.add(portfolio)
    
    # Record the transaction
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


def get_portfolio_data(user_id):
    # Retrieve the portfolio for the given user_id
    portfolio = session_db.query(Portfolio).filter_by(user_id=user_id).all()
    print(portfolio)

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
    symbols = ["AAPL", "TSLA", "NVDA", "SOFI"]
    stocks = []

    for symbol in symbols:
        quote = lookup(symbol)
        if not quote:
            continue

        current_price = quote["price"]
    
        # fetch last stored price
    

        last_price = (session_db.query(Portfolio.price).filter(Portfolio.symbol == symbol).order_by(Portfolio.price.desc()).first())
                

        previous_price = last_price.price if last_price is not None  else current_price
    
        change = ((current_price - previous_price) / previous_price) * 100

        stocks.append({
            "name": quote["name"],
            "price": current_price,
            "change": round(change, 2)
        })

    return stocks

# ============================================
# REST API ENDPOINTS FOR REACT FRONTEND
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
