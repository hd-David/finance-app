import os
import requests,csv
import urllib.parse
from flask_login import login_required as flask_login_required

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    @flask_login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol using Alpha Vantage."""
    try:
        api_key = os.environ.get("API_KEY")
        if not api_key:
            return None

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE", "symbol": symbol.upper(),"apikey": api_key}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        quote = response.json().get("Global Quote")

        if not quote:
            return None

        data = {"name": symbol.upper(),  # Alpha doesn’t return company name here
                "symbol": quote["01. symbol"],
                "price": float(quote["05. price"])
                }

        print(data)
        return data

    except (requests.RequestException, KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
