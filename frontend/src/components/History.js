import React, { useState, useEffect } from 'react';

const History = ({ userToken }) => {
    const [transactions, setTransactions] = useState([]);

useEffect(() => {
    // 🛑 STOP if token isn't ready yet
    if (!userToken || userToken === "undefined") {
        console.log("Waiting for token...");
        return;
    }

    fetch('http://localhost:5000/api/history', {
        headers: { 'Authorization': `Bearer ${userToken}` }
    })
    .then(res => res.json())
    .then(data => {
        if (data.msg) {
            console.error("Server says:", data.msg); // This catches the segment error
        }
        setTransactions(data.transactions || []);
    })
    .catch(err => console.error("History fetch error:", err));
}, [userToken]);

    return (
        <div className="card">
            <div className="card-header">Transaction History</div>
            <div className="card-body">
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Symbol</th>
                            <th>Shares</th>
                            <th>Price</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                        <tbody>
                        {transactions.map((t) => (
                            <tr key={t.id}>
                                <td>
                                    <span className={`badge ${t.transaction_type === 'BUY' ? 'bg-success' : 'bg-danger'}`}>
                                        {t.transaction_type}
                                    </span>
                                </td>
                                <td><strong>{t.symbol}</strong></td>
                                <td>{t.quantity}</td>
                                <td>${t.price.toFixed(2)}</td>
                                <td>{t.timestamp ? new Date(t.timestamp).toLocaleString() : 'N/A'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default History;