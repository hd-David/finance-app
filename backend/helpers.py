import os
import requests

# Make sure API key is set
from dotenv import load_dotenv
load_dotenv() # This loads the variables from .env into your system

api_key = os.getenv("API_KEY")
# Set the base configuration once at the top
BASE_URL = "https://www.alphavantage.co/query"

def _make_api_request(params):
    """
    Private helper to handle all Alpha Vantage communication.
    Returns JSON data or None if something goes wrong.
    """
    if not api_key:
        print("API_KEY not found in environment")
        return None

    # Merge the specific function params with the API key
    params["apikey"] = api_key
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Request Error: {e}")
        return None
def lookup(symbol):
    """Look up quote for symbol using Alpha Vantage."""
    try:
        api_key = os.getenv("API_KEY")
        if not api_key:
            print("Error: API_KEY is missing!")
            return None # This stops if key is missing

        # ALL THIS CODE MUST BE FLUSH WITH THE 'IF' BLOCK, NOT INSIDE IT
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE", 
            "symbol": symbol.upper(),
            "apikey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data_json = response.json()
        
        # Alpha Vantage returns 'Note' when you hit the rate limit
        if "Note" in data_json:
            print("API Rate Limit Hit!")
            return None

        quote = data_json.get("Global Quote")

        if not quote or "05. price" not in quote:
            return None

        data = {
            "name": symbol.upper(),
            "symbol": quote["01. symbol"],
            "price": float(quote["05. price"])
        }

        print(f"Successfully fetched: {data}")
        return data
    
    except Exception as e:
        print(f"Lookup error: {e}")
        return None

def get_trending_stocks():
    """Specific logic for market gainers/losers."""
    data = _make_api_request({"function": "TOP_GAINERS_LOSERS"})
    if not data:
        return []

    # Just combine gainers/losers and return
    combined = data.get("top_gainers", [])[:5] + data.get("top_losers", [])[:5]
    return [{
        "symbol": i.get("ticker"),
        "price": float(i.get("price", 0)),
        "change": i.get("change_percentage", "0%")
    } for i in combined]