import React, { useState } from 'react';

const BuyStock = ({ userToken, updateBalance }) => {
    const [symbol, setSymbol] = useState("");
    const [quantity, setQuantity] = useState(1);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState({ type: '', text: '' });

    const handleBuy = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });

        try {
            const response = await fetch('http://localhost:5000/api/buy', {
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