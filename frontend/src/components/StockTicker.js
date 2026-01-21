import React, { useState, useEffect } from 'react';

const StockTicker = () => {
    const [stocks, setStocks] = useState([]);

    useEffect(() => {
        const fetchMarketData = () => {
            fetch('http://localhost:5000/api/market-snapshot')
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
                {stocks.map((stock, index) => (
                    <div key={index} className="ticker__item">
                        <span className="text-info fw-bold">{stock.symbol}</span>
                        <span className="ms-2 text-white">${Number(stock.price).toFixed(2)}</span>
                    </div>
                ))}
                {/* Duplicate the list for a seamless infinite loop */}
                {stocks.map((stock, index) => (
                    <div key={`dup-${index}`} className="ticker__item">
                        <span className="text-info fw-bold">{stock.symbol}</span>
                        <span className="ms-2 text-white">${Number(stock.price).toFixed(2)}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default StockTicker;