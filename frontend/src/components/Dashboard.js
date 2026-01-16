import React, { useState, useEffect } from 'react';

const Dashboard = ({ userToken, cash }) => {
    const [portfolio, setPortfolio] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchPortfolio = async () => {
        setLoading(true);
        setError('');
        
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
            setPortfolio(data);
        } catch (err) {
            setError('Unable to load portfolio data. Please try again.');
            console.error('Portfolio fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPortfolio();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [userToken]);

    const calculateTotalValue = () => {
        if (!portfolio || !portfolio.holdings) return cash;
        
        const stocksValue = portfolio.holdings.reduce((sum, holding) => {
            return sum + (holding.current_price * holding.shares);
        }, 0);
        
        return cash + stocksValue;
    };

    const calculateGainLoss = (holding) => {
        const currentValue = holding.current_price * holding.shares;
        const costBasis = holding.avg_price * holding.shares;
        return currentValue - costBasis;
    };

    if (loading) {
        return (
            <div className="text-center p-5">
                <div className="spinner-border text-primary" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
                <p className="mt-2">Loading portfolio...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="alert alert-danger" role="alert">
                {error}
                <button className="btn btn-sm btn-outline-danger ml-3" onClick={fetchPortfolio}>
                    Retry
                </button>
            </div>
        );
    }

    const totalValue = calculateTotalValue();
    const stocksValue = totalValue - cash;

    return (
        <div className="p-3">
            {/* Summary Cards */}
            <div className="row mb-4">
                <div className="col-md-4 mb-3">
                    <div className="card border-left-primary shadow-sm">
                        <div className="card-body">
                            <div className="text-xs font-weight-bold text-primary text-uppercase mb-1">
                                Cash Balance
                            </div>
                            <div className="h5 mb-0 font-weight-bold text-gray-800">
                                ${parseFloat(cash).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div className="col-md-4 mb-3">
                    <div className="card border-left-success shadow-sm">
                        <div className="card-body">
                            <div className="text-xs font-weight-bold text-success text-uppercase mb-1">
                                Stocks Value
                            </div>
                            <div className="h5 mb-0 font-weight-bold text-gray-800">
                                ${parseFloat(stocksValue).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div className="col-md-4 mb-3">
                    <div className="card border-left-info shadow-sm">
                        <div className="card-body">
                            <div className="text-xs font-weight-bold text-info text-uppercase mb-1">
                                Total Portfolio
                            </div>
                            <div className="h5 mb-0 font-weight-bold text-gray-800">
                                ${parseFloat(totalValue).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Holdings Table */}
            <div className="card shadow-sm">
                <div className="card-header py-3">
                    <h6 className="m-0 font-weight-bold text-primary">Stock Holdings</h6>
                </div>
                <div className="card-body">
                    {portfolio && portfolio.holdings && portfolio.holdings.length > 0 ? (
                        <div className="table-responsive">
                            <table className="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Symbol</th>
                                        <th className="text-right">Shares</th>
                                        <th className="text-right">Avg Price</th>
                                        <th className="text-right">Current Price</th>
                                        <th className="text-right">Total Value</th>
                                        <th className="text-right">Gain/Loss</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {portfolio.holdings.map((holding, index) => {
                                        const gainLoss = calculateGainLoss(holding);
                                        const gainLossPercent = ((holding.current_price - holding.avg_price) / holding.avg_price) * 100;
                                        const isPositive = gainLoss >= 0;
                                        
                                        return (
                                            <tr key={index}>
                                                <td>
                                                    <strong>{holding.symbol}</strong>
                                                    {holding.name && <div className="small text-muted">{holding.name}</div>}
                                                </td>
                                                <td className="text-right">{holding.shares}</td>
                                                <td className="text-right">
                                                    ${parseFloat(holding.avg_price).toFixed(2)}
                                                </td>
                                                <td className="text-right">
                                                    ${parseFloat(holding.current_price).toFixed(2)}
                                                </td>
                                                <td className="text-right">
                                                    ${parseFloat(holding.current_price * holding.shares).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                                </td>
                                                <td className={`text-right ${isPositive ? 'text-success' : 'text-danger'}`}>
                                                    <strong>
                                                        {isPositive ? '+' : ''}${parseFloat(gainLoss).toFixed(2)}
                                                    </strong>
                                                    <div className="small">
                                                        ({isPositive ? '+' : ''}{gainLossPercent.toFixed(2)}%)
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="text-center py-5 text-muted">
                            <i className="fal fa-inbox fa-3x mb-3 d-block"></i>
                            <p>No stock holdings yet. Start by buying some shares!</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
