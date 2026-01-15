from model import *

def register_user(user_dict):
    user = User()
    user.username = user_dict['username']
    user.password_hash = user_dict['password_hash']
    user.email = user_dict['email']
    return user

def add_stock_porfolio(stock):
    portfolio = Portfolio()
    portfolio.user_id = stock['user_id']
    portfolio.symbol = stock['symbol']
    portfolio.quantity = stock['quantity']
    portfolio.price = stock['price']