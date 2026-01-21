import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const StockTicker = () => {
    const [stocks, setStocks] = useState([]);

    useEffect(() => {
        const fetchMarketData = () => {
            fetch(`${API_BASE_URL}/api/market-snapshot`)
                .then(res => res.json())
                .then(data => setStocks(data))
                .catch(err => console.error("Ticker error:", err));
        };

        fetchMarketData();
        const interval = setInterval(fetchMarketData, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="ticker-wrap glass-card">
            <div className="ticker">
                {stocks.map((stock) => (
                    <div key={stock.symbol} className="ticker__item">
                        <span className="text-info fw-bold">{stock.symbol}</span>
                        <span className="ms-2 text-white">${Number(stock.price).toFixed(2)}</span>
                    </div>
                ))}
                {/* Duplicate the list for a seamless infinite loop */}
                {stocks.map((stock) => (
                    <div key={`dup-${stock.symbol}`} className="ticker__item">
                        <span className="text-info fw-bold">{stock.symbol}</span>
                        <span className="ms-2 text-white">${Number(stock.price).toFixed(2)}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StockTicker;