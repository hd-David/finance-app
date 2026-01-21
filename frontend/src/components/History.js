import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const History = ({ userToken }) => {
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchHistory = async () => {
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_BASE_URL}/api/history`, {
                headers: {
                    'Authorization': `Bearer ${userToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch transaction history');
            }

            const data = await response.json();
            setTransactions(data.transactions || []);
        } catch (err) {
            setError('Unable to load transaction history. Please try again.');
            console.error('History fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [userToken]);

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="text-center p-5">
                <div className="spinner-border text-primary" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
                <p className="mt-2">Loading transaction history...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="alert alert-danger" role="alert">
                {error}
                <button className="btn btn-sm btn-outline-danger ml-3" onClick={fetchHistory}>
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="p-3">
            <div className="card shadow-sm">
                <div className="card-header py-3">
                    <h6 className="m-0 font-weight-bold text-primary">Transaction History</h6>
                </div>
                <div className="card-body">
                    {transactions.length > 0 ? (
                        <div className="table-responsive">
                            <table className="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Date & Time</th>
                                        <th>Type</th>
                                        <th>Symbol</th>
                                        <th className="text-right">Shares</th>
                                        <th className="text-right">Price</th>
                                        <th className="text-right">Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {transactions.map((transaction, index) => {
                                        const isBuy = transaction.type === 'BUY' || transaction.type === 'buy';
                                        const total = transaction.price * transaction.shares;
                                        
                                        return (
                                            <tr key={index}>
                                                <td>
                                                    <span className="d-block">{formatDate(transaction.timestamp || transaction.date)}</span>
                                                </td>
                                                <td>
                                                    <span className={`badge badge-${isBuy ? 'success' : 'danger'} badge-pill`}>
                                                        {transaction.type.toUpperCase()}
                                                    </span>
                                                </td>
                                                <td>
                                                    <strong>{transaction.symbol}</strong>
                                                </td>
                                                <td className="text-right">
                                                    {transaction.shares}
                                                </td>
                                                <td className="text-right">
                                                    ${parseFloat(transaction.price).toFixed(2)}
                                                </td>
                                                <td className={`text-right font-weight-bold ${isBuy ? 'text-danger' : 'text-success'}`}>
                                                    {isBuy ? '-' : '+'}${parseFloat(total).toFixed(2)}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="text-center py-5 text-muted">
                            <i className="fal fa-history fa-3x mb-3 d-block"></i>
                            <p>No transactions yet. Start trading to see your history!</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Mobile Card View - Hidden on Desktop */}
            {transactions.length > 0 && (
                <div className="d-md-none mt-3">
                    {transactions.map((transaction, index) => {
                        const isBuy = transaction.type === 'BUY' || transaction.type === 'buy';
                        const total = transaction.price * transaction.shares;
                        
                        return (
                            <div key={index} className="card mb-2 shadow-sm">
                                <div className="card-body">
                                    <div className="d-flex justify-content-between align-items-start mb-2">
                                        <div>
                                            <h5 className="mb-0">{transaction.symbol}</h5>
                                            <small className="text-muted">
                                                {formatDate(transaction.timestamp || transaction.date)}
                                            </small>
                                        </div>
                                        <span className={`badge badge-${isBuy ? 'success' : 'danger'} badge-pill`}>
                                            {transaction.type.toUpperCase()}
                                        </span>
                                    </div>
                                    <div className="row mt-2">
                                        <div className="col-4">
                                            <small className="text-muted d-block">Shares</small>
                                            <strong>{transaction.shares}</strong>
                                        </div>
                                        <div className="col-4">
                                            <small className="text-muted d-block">Price</small>
                                            <strong>${parseFloat(transaction.price).toFixed(2)}</strong>
                                        </div>
                                        <div className="col-4">
                                            <small className="text-muted d-block">Total</small>
                                            <strong className={isBuy ? 'text-danger' : 'text-success'}>
                                                {isBuy ? '-' : '+'}${parseFloat(total).toFixed(2)}
                                            </strong>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default History;
