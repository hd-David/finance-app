import React, { useState, useEffect } from 'react';
import DashboardChart from './DashboardChart'; // Adjust the path if it's in a /components folder

const Dashboard = ({ userToken }) => {
    const [portfolio, setPortfolio] = useState([]);
    const [stats, setStats] = useState({ total_value: 0, cash: 0 });

    useEffect(() => {
  if (!userToken) return;

  fetch('http://localhost:5000/api/portfolio', {
    headers: {
      Authorization: `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    }
  })
  .then(res =>
    res.json().then(data => {
      if (!res.ok) throw data;
      return data;
    })
  )
  .then(data => {
    setPortfolio(data.holdings || []);
    setStats({
      total_value: Number(data.total_value) || 0,
      cash: Number(data.cash) || 0
    });
  })
  .catch(err => {
    console.error("Portfolio error:", err);
  });
}, [userToken]);

    return (
        <div className="container-fluid">
            <div className="row mb-4">
                <div className="col-md-4">
                    <div className="p-3 bg-primary text-white rounded">
                        <h5>Total Portfolio Value</h5>
                        <h2 className="display-4">${stats.total_value.toFixed(2)}</h2>
                    </div>
                </div>
            </div>

            <div className="card">
                <div className="card-header">Your Holdings</div>
                <div className="card-body">
                    <table className="table table-hover">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Shares</th>
                                <th>Current Price</th>
                                <th>Total Value</th>
                            </tr>
                        </thead>
                        <tbody>
                           {portfolio.map(stock => (
                                <tr key={stock.symbol}>
                                    <td><strong>{stock.symbol}</strong></td>
                                    <td>{stock.quantity}</td> {/* Use quantity here! */}
                                    <td>${stock.price}</td>
                                    <td>${(stock.quantity * stock.price).toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
    
  <div className="dashboard-wrapper bg-black text-white min-vh-100">
    {/* ... Your Top Bar / Balance Section ... */}

    <div className="container-fluid p-4">
      <div className="row">
        <div className="col-12">
          <div className="table-responsive">
            <table className="table table-dark">
              {/* Your existing table code */}
            </table>
          </div>
        </div>
      </div>

      {/* 🚀 SNAP THE CHARTS IN HERE */}
      <DashboardChart portfolioData={portfolio} /> 

    </div>
  </div>

        </div>
    );
};

export default Dashboard;