import React, { useState, useEffect } from 'react';

const SellStock = ({ userToken, updateBalance }) => {
    const [holdings, setHoldings] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [quantity, setQuantity] = useState('');
    const [status, setStatus] = useState({ type: '', msg: '' });

    // 1. Get current holdings so the user knows what they can sell
    useEffect(() => {
        if (!userToken) return;
        fetch('http://localhost:5000/api/portfolio', {
            headers: { 'Authorization': `Bearer ${userToken}` }
        })
        .then(res => res.json())
        .then(data => setHoldings(data.holdings || []));
    }, [userToken]);

    const handleSell = (e) => {
        e.preventDefault();
        fetch('http://localhost:5000/api/sell', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${userToken}`
            },
            body: JSON.stringify({ symbol: selectedSymbol, quantity: parseInt(quantity) })
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                setStatus({ type: 'danger', msg: data.error });
            } else {
                setStatus({ type: 'success', msg: `Sold ${quantity} shares of ${selectedSymbol}!` });
                updateBalance(data.new_balance); // Update global cash state
                setQuantity('');
            }
        });
    };

    return (
        <div className="card shadow-sm">
            <div className="card-header bg-danger text-white">Sell Shares</div>
            <div className="card-body">
                {status.msg && <div className={`alert alert-${status.type}`}>{status.msg}</div>}
                <form onSubmit={handleSell}>
                    <div className="mb-3">
                        <label className="form-label">Select Stock</label>
                        <select 
                            className="form-select" 
                            value={selectedSymbol} 
                            onChange={(e) => setSelectedSymbol(e.target.value)}
                            required
                        >
                            <option value="">-- Choose a stock you own --</option>
                            {holdings.map(h => (
                                <option key={h.symbol} value={h.symbol}>
                                    {h.symbol} ({h.quantity} available)
                                </option>
                            ))}
                        </select>
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Quantity</label>
                        <input 
                            type="number" 
                            className="form-control" 
                            value={quantity} 
                            onChange={(e) => setQuantity(e.target.value)}
                            placeholder="How many to sell?"
                            required 
                        />
                    </div>
                    <button type="submit" className="btn btn-danger w-100">Confirm Sell</button>
                </form>
            </div>
        </div>
    );
};

export default SellStock;