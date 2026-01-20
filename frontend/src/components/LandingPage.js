import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import StockTicker from './StockTicker';

const LandingPage = ({ token }) => {
  const [marketData, setMarketData] = useState([]);
  const [latency, setLatency] = useState(12);

  useEffect(() => {
    // 1. Fetch real Alpha Vantage data from your backend proxy
    fetch('http://localhost:5000/api/market-snapshot')
      .then(res => res.json())
      .then(data => setMarketData(data))
      .catch(err => console.error("Error fetching market data:", err));

    // 2. Simulated live latency heartbeat
    const interval = setInterval(() => {
      setLatency(Math.floor(Math.random() * (18 - 8 + 1) + 8));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // Calculate dynamic volume safely
  const totalVolume = marketData.reduce((acc, stock) => {
      const val = Number(stock.price) || 0;
      return acc + (val * 1.2);
  }, 0).toFixed(1);

  return (
    <div className="terminal-body min-vh-100 text-white">
      <StockTicker />

      <div className="container-fluid p-5">
        <div className="row">
          
          {/* LEFT SIDE: Branding and Main CTA */}
          <div className="col-lg-8">
            <h1 className="display-1 fw-black mb-0 text-gradient">QUANTUM</h1>
            <h2 className="display-4 fw-light mb-5">FINANCE TERMINAL</h2>

            <div className="d-flex gap-4 mb-5">
              {token ? (
                <Link to="/dashboard" className="btn btn-info btn-lg px-5 py-3 fw-bold">ACCESS TERMINAL</Link>
              ) : (
                <Link to="/login" className="btn btn-outline-info btn-lg px-5 py-3 fw-bold">INITIATE SESSION</Link>
              )}
            </div>

            <div className="row g-3">
              <div className="col-md-4">
                <div className="metric-panel">
                  <small className="text-muted d-block mb-1 text-uppercase">Network Latency</small>
                  <span className="fs-2 fw-bold text-success">{latency}ms</span>
                  <div className="progress mt-2" style={{height: '2px'}}>
                    <div className="bg-success w-100 opacity-50"></div>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="metric-panel">
                  <small className="text-muted d-block mb-1 text-uppercase">Market Cap Index (Rel)</small>
                  <span className="fs-2 fw-bold">${totalVolume}B</span>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT SIDE: Dynamic Sidebar */}
          {/* CHANGE THIS LINE */}
            <div className="col-lg-4 border-start-lg border-secondary mt-5 mt-lg-0">
            <div className="p-4">
              <h5 className="text-info mb-4 fs-6 fw-mono">MARKET_WATCH: <span className="text-success">LIVE</span></h5>
              
              <ul className="list-unstyled">
                {/* 🚀 THE CRITICAL FIX: Mapping through marketData defines 'stock' */}
                {marketData && marketData.length > 0 ? (
                  marketData.map((stock, index) => {
                    // Define 'price' inside the loop so it's not "undefined"

                    return (
                      <li key={index} className="mb-4 border-bottom border-dark pb-2">
                        <small className="d-block text-muted text-uppercase">{stock.symbol}</small>
                        <span className="fs-4">
                          {!isNaN(stock.price) && stock.price > 0 ? (
                            `$${stock.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}`
                          ) : (
                            <span className="text-info fs-6">
                              <span className="spinner-border spinner-border-sm me-2"></span>
                              Link Establishing...
                            </span>
                          )}
                          {stock.price > 0 && <span className="text-success fs-6 ms-2">+Live</span>}
                        </span>
                      </li>
                    );
                  })
                ) : (
                  <div className="text-muted small">
                    <span className="spinner-grow spinner-grow-sm me-2"></span>
                    Awaiting Market Feed...
                  </div>
                )}
              </ul>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default LandingPage;