import React, { useState, useEffect } from 'react';

const SellStock = ({ userToken, updateBalance }) => {
    const [holdings, setHoldings] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState("");
    const [quantity, setQuantity] = useState(1);
    const [loading, setLoading] = useState(false);
    const [fetchingHoldings, setFetchingHoldings] = useState(true);
    const [message, setMessage] = useState({ type: '', text: '' });
    const [currentPrice, setCurrentPrice] = useState(null);

    useEffect(() => {
        fetchHoldings();
    }, [userToken]);

    useEffect(() => {
        if (selectedSymbol) {
            fetchCurrentPrice(selectedSymbol);
        }
    }, [selectedSymbol]);

    const fetchHoldings = async () => {
        setFetchingHoldings(true);
        try {
            const response = await fetch('http://localhost:5000/api/portfolio', {
                headers: {
                    'Authorization': `Bearer ${userToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch portfolio');
            }

            const data = await response.json();
            if (data.holdings && data.holdings.length > 0) {
                setHoldings(data.holdings);
                setSelectedSymbol(data.holdings[0].symbol);
            }
        } catch (err) {
            setMessage({ type: 'danger', text: 'Unable to load your holdings.' });
            console.error('Holdings fetch error:', err);
        } finally {
            setFetchingHoldings(false);
        }
    };

    const fetchCurrentPrice = async (symbol) => {
        try {
            const response = await fetch('http://localhost:5000/api/quote', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${userToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ symbol })
            });

            if (response.ok) {
                const data = await response.json();
                setCurrentPrice(data.price);
            }
        } catch (err) {
            console.error('Price fetch error:', err);
        }
    };

    const handleSell = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });

        try {
            const response = await fetch('http://localhost:5000/api/sell', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userToken}`
                },
                body: JSON.stringify({
                    symbol: selectedSymbol,
                    quantity: parseInt(quantity)
                })
            });

            const data = await response.json();

            if (response.ok) {
                setMessage({ 
                    type: 'success', 
                    text: `Success! Sold ${quantity} shares of ${selectedSymbol}.` 
                });
                
                // Update balance
                if (data.new_balance !== undefined) {
                    updateBalance(data.new_balance);
                }
                
                // Refresh holdings
                await fetchHoldings();
                setQuantity(1);
            } else {
                setMessage({ type: 'danger', text: data.error || "Transaction failed" });
            }
        } catch (err) {
            setMessage({ type: 'danger', text: "Could not connect to the server." });
        } finally {
            setLoading(false);
        }
    };

    const selectedHolding = holdings.find(h => h.symbol === selectedSymbol);
    const estimatedProceeds = currentPrice ? (currentPrice * quantity).toFixed(2) : '...';

    if (fetchingHoldings) {
        return (
            <div className="text-center p-5">
                <div className="spinner-border text-primary" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
                <p className="mt-2">Loading your holdings...</p>
            </div>
        );
    }

    if (holdings.length === 0) {
        return (
            <div className="alert alert-info" role="alert">
                <i className="fal fa-info-circle mr-2"></i>
                You don't own any stocks yet. Buy some shares first!
            </div>
        );
    }

    return (
        <div className="p-3">
            {message.text && (
                <div className={`alert alert-${message.type} fade show`} role="alert">
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSell}>
                <div className="form-group">
                    <label className="form-label" htmlFor="symbol">Select Stock</label>
                    <select 
                        id="symbol"
                        className="form-control form-control-lg"
                        value={selectedSymbol}
                        onChange={(e) => setSelectedSymbol(e.target.value)}
                        required
                    >
                        {holdings.map((holding) => (
                            <option key={holding.symbol} value={holding.symbol}>
                                {holding.symbol} - {holding.shares} shares owned
                            </option>
                        ))}
                    </select>
                </div>

                {selectedHolding && (
                    <div className="alert alert-light border mb-3">
                        <div className="row">
                            <div className="col-6">
                                <small className="text-muted d-block">Shares Owned</small>
                                <strong>{selectedHolding.shares}</strong>
                            </div>
                            <div className="col-6">
                                <small className="text-muted d-block">Current Price</small>
                                <strong className="text-success">
                                    ${currentPrice ? parseFloat(currentPrice).toFixed(2) : '...'}
                                </strong>
                            </div>
                        </div>
                    </div>
                )}

                <div className="form-group">
                    <label className="form-label" htmlFor="quantity">Quantity to Sell</label>
                    <input 
                        type="number" 
                        id="quantity"
                        className="form-control form-control-lg" 
                        min="1"
                        max={selectedHolding ? selectedHolding.shares : 1}
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        required
                    />
                    {selectedHolding && (
                        <span className="help-block">
                            Maximum: {selectedHolding.shares} shares
                        </span>
                    )}
                </div>

                <div className="alert alert-secondary">
                    <div className="d-flex justify-content-between align-items-center">
                        <span>Estimated Proceeds:</span>
                        <strong className="h5 mb-0 text-success">
                            ${estimatedProceeds}
                        </strong>
                    </div>
                </div>

                <div className="row no-gutters">
                    <div className="col-md-12 ml-auto text-right">
                        <button 
                            type="submit" 
                            className="btn btn-danger btn-lg waves-effect waves-themed"
                            disabled={loading}
                        >
                            {loading ? (
                                <><span className="spinner-border spinner-border-sm mr-1"></span> Processing...</>
                            ) : (
                                "Sell Shares"
                            )}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default SellStock;
