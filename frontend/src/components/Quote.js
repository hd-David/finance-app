import React, { useState } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const Quote = ({ userToken }) => {
    const [symbol, setSymbol] = useState("");
    const [quote, setQuote] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleQuote = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setQuote(null);

        try {
            const response = await fetch(`${API_BASE_URL}/api/quote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userToken}`
                },
                body: JSON.stringify({ 
                    symbol: symbol.trim().toUpperCase()
                })
            });

            const data = await response.json();

            if (response.ok) {
                setQuote(data);
                setError("");
            } else {
                setError(data.error || "Unable to fetch quote");
                setQuote(null);
            }
        } catch (err) {
            setError("Could not connect to the server.");
            setQuote(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-3">
            <form onSubmit={handleQuote}>
                <div className="form-group">
                    <label className="form-label" htmlFor="symbol">Stock Symbol</label>
                    <div className="input-group input-group-lg">
                        <input 
                            type="text" 
                            id="symbol"
                            className="form-control" 
                            placeholder="e.g. AAPL, MSFT, TSLA"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value)}
                            required
                        />
                        <div className="input-group-append">
                            <button 
                                type="submit" 
                                className="btn btn-primary"
                                disabled={loading}
                            >
                                {loading ? (
                                    <><span className="spinner-border spinner-border-sm mr-1"></span> Fetching...</>
                                ) : (
                                    <>
                                        <i className="fal fa-search mr-1"></i> Get Quote
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                    <span className="help-block">Enter a stock ticker symbol to view its current price.</span>
                </div>
            </form>

            {error && (
                <div className="alert alert-danger fade show mt-3" role="alert">
                    <i className="fal fa-exclamation-circle mr-2"></i>
                    {error}
                </div>
            )}

            {quote && (
                <div className="card shadow-sm mt-4">
                    <div className="card-body text-center">
                        <div className="mb-3">
                            <h2 className="mb-1 font-weight-bold text-primary">
                                {quote.symbol}
                            </h2>
                            {quote.name && (
                                <p className="text-muted mb-0">{quote.name}</p>
                            )}
                        </div>
                        
                        <div className="border-top pt-3">
                            <p className="text-muted small mb-1">Current Price</p>
                            <h1 className="display-4 font-weight-bold text-success mb-0">
                                ${parseFloat(quote.price).toFixed(2)}
                            </h1>
                        </div>

                        {quote.change !== undefined && (
                            <div className="mt-3 pt-3 border-top">
                                <div className="row">
                                    <div className="col-6">
                                        <small className="text-muted d-block">Change</small>
                                        <span className={`font-weight-bold ${quote.change >= 0 ? 'text-success' : 'text-danger'}`}>
                                            {quote.change >= 0 ? '+' : ''}${parseFloat(quote.change).toFixed(2)}
                                        </span>
                                    </div>
                                    <div className="col-6">
                                        <small className="text-muted d-block">Change %</small>
                                        <span className={`font-weight-bold ${quote.changePercent >= 0 ? 'text-success' : 'text-danger'}`}>
                                            {quote.changePercent >= 0 ? '+' : ''}{parseFloat(quote.changePercent).toFixed(2)}%
                                        </span>
                                    </div>
                                </div>
                            </div>
                        )}

                        {quote.volume !== undefined && (
                            <div className="mt-3 pt-3 border-top">
                                <div className="row text-center">
                                    <div className="col-4">
                                        <small className="text-muted d-block">Open</small>
                                        <strong>${parseFloat(quote.open || quote.price).toFixed(2)}</strong>
                                    </div>
                                    <div className="col-4">
                                        <small className="text-muted d-block">High</small>
                                        <strong>${parseFloat(quote.high || quote.price).toFixed(2)}</strong>
                                    </div>
                                    <div className="col-4">
                                        <small className="text-muted d-block">Low</small>
                                        <strong>${parseFloat(quote.low || quote.price).toFixed(2)}</strong>
                                    </div>
                                </div>
                            </div>
                        )}

                        {quote.marketCap && (
                            <div className="mt-3 pt-3 border-top">
                                <small className="text-muted d-block">Market Cap</small>
                                <strong>{quote.marketCap}</strong>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {!quote && !error && !loading && (
                <div className="text-center py-5 text-muted">
                    <i className="fal fa-chart-line fa-3x mb-3 d-block"></i>
                    <p>Enter a stock symbol above to view real-time pricing information.</p>
                </div>
            )}
        </div>
    );
};

export default Quote;
