import os
import requests

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

        # Note: Alpha Vantage GLOBAL_QUOTE doesn't include company name,
        # so we use the symbol as a placeholder for display purposes
        data = {"name": symbol.upper(),
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
