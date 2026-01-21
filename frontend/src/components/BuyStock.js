import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const BuyStock = ({ userToken, updateBalance }) => {
    const [symbol, setSymbol] = useState("");
    const [quantity, setQuantity] = useState(1);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [currentPrice, setCurrentPrice] = useState(null);
    const [fetchingPrice, setFetchingPrice] = useState(false);

    const fetchPrice = async () => {
        if (!symbol.trim()) return;
        
        setFetchingPrice(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/quote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userToken}`
                },
                body: JSON.stringify({ symbol: symbol.trim().toUpperCase() })
            });

            if (response.ok) {
                const data = await response.json();
                setCurrentPrice(data.price);
            } else {
                setCurrentPrice(null);
            }
        } catch (err) {
            setCurrentPrice(null);
        } finally {
            setFetchingPrice(false);
        }
    };

    useEffect(() => {
        if (symbol && symbol.length >= 1) {
            const timer = setTimeout(() => {
                fetchPrice();
            }, 800);
            return () => clearTimeout(timer);
        } else {
            setCurrentPrice(null);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [symbol]);

    const handleBuy = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });

        try {
            const response = await fetch(`${API_BASE_URL}/api/buy`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userToken}`
                },
                body: JSON.stringify({ 
                    symbol: symbol.trim().toUpperCase(), 
                    quantity: parseInt(quantity) 
                })
            });

            const data = await response.json();

            if (response.ok) {
                setMessage({ type: 'success', text: `Success! Purchased ${quantity} shares of ${symbol.toUpperCase()}.` });
                setSymbol(""); // Clear form
                setQuantity(1);
                
                // Update the balance in the parent App.js
                if (data.new_balance !== undefined) {
                    updateBalance(data.new_balance);
                }
            } else {
                setMessage({ type: 'danger', text: data.error || "Transaction failed" });
            }
        } catch (err) {
            setMessage({ type: 'danger', text: "Could not connect to the server." });
        } finally {
            setLoading(false);
        }
    };

    const estimatedCost = currentPrice && quantity > 0 ? (currentPrice * quantity).toFixed(2) : null;

    return (
        <div className="p-3">
            {message.text && (
                <div className={`alert alert-${message.type} fade show`} role="alert">
                    {message.text}
                </div>
            )}

            <form onSubmit={handleBuy}>
                <div className="form-group">
                    <label className="form-label" htmlFor="symbol">Stock Symbol</label>
                    <input 
                        type="text" 
                        id="symbol"
                        className="form-control form-control-lg" 
                        placeholder="e.g. AAPL, TSLA"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                        required
                    />
                    <span className="help-block">Enter the ticker symbol of the company.</span>
                </div>

                {currentPrice && (
                    <div className="alert alert-light border mb-3">
                        <div className="row">
                            <div className="col-6">
                                <small className="text-muted d-block">Current Price</small>
                                <strong className="text-success">${parseFloat(currentPrice).toFixed(2)}</strong>
                            </div>
                            <div className="col-6">
                                <small className="text-muted d-block">Symbol</small>
                                <strong>{symbol.toUpperCase()}</strong>
                            </div>
                        </div>
                    </div>
                )}

                {fetchingPrice && !currentPrice && (
                    <div className="alert alert-info mb-3">
                        <span className="spinner-border spinner-border-sm mr-2"></span>
                        Fetching current price...
                    </div>
                )}

                <div className="form-group">
                    <label className="form-label" htmlFor="quantity">Quantity</label>
                    <input 
                        type="number" 
                        id="quantity"
                        className="form-control form-control-lg" 
                        min="1"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        required
                    />
                </div>

                {estimatedCost && (
                    <div className="alert alert-secondary">
                        <div className="d-flex justify-content-between align-items-center">
                            <span>Estimated Total Cost:</span>
                            <strong className="h5 mb-0 text-primary">
                                ${estimatedCost}
                            </strong>
                        </div>
                    </div>
                )}

                <div className="row no-gutters">
                    <div className="col-md-12 ml-auto text-right">
                        <button 
                            type="submit" 
                            className="btn btn-primary btn-lg waves-effect waves-themed"
                            disabled={loading}
                        >
                            {loading ? (
                                <><span className="spinner-border spinner-border-sm mr-1"></span> Processing...</>
                            ) : (
                                "Buy Shares"
                            )}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default BuyStock;