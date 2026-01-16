import React, { useState, useEffect } from 'react';
import BuyStock from './components/BuyStock';
import Login from './components/Login';
import Register from './components/Register';

function App() {
  // 1. Core State
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isRegistering, setIsRegistering] = useState(false);
  const [cash, setCash] = useState(0);
  const [username, setUsername] = useState("Guest");

  // 2. Fetch User Profile (Balance & Name) whenever the token changes
  useEffect(() => {
    if (token) {
      fetch('http://localhost:5000/api/user/profile', {
        headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
      })
      .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then(data => {
        setCash(data.cash);
        setUsername(data.username);
      })
      .catch(err => {
        console.error("Profile fetch error:", err);
        // If token is invalid/expired, log out the user
        handleLogout();
      });
    }
  }, [token]);

  // 3. Actions
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCash(0);
    setUsername("Guest");
    setIsRegistering(false);
  };

  const updateBalance = (newBalance) => {
    setCash(newBalance);
  };

  return (
    <div className="page-wrapper">
      <div className="page-inner">
        
        {/* Left Sidebar */}
        <aside className="page-sidebar">
          <div className="page-logo">
            <span className="page-logo-text">C$50 Finance</span>
          </div>
          <nav id="js-primary-nav" className="primary-nav" role="navigation">
            <ul id="js-nav-menu" className="nav-menu">
              <li className="active">
                <a href="/"><i className="fal fa-home"></i> Dashboard</a>
              </li>
              
              {!token ? (
                <li>
                  {/* Toggle between Login and Register via the sidebar */}
                  <a href="#" onClick={(e) => { e.preventDefault(); setIsRegistering(!isRegistering); }}>
                    <i className={isRegistering ? "fal fa-sign-in" : "fal fa-user-plus"}></i>
                    {isRegistering ? " Switch to Login" : " Register Account"}
                  </a>
                </li>
              ) : (
                <li>
                  <a href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}>
                    <i className="fal fa-sign-out"></i> Logout
                  </a>
                </li>
              )}
            </ul>
          </nav>
        </aside>

        <div className="page-content-wrapper">
          {/* Header */}
          <header className="page-header" role="banner">
            <div className="ml-auto d-flex align-items-center">
              {token && (
                <div className="mr-4 text-right">
                  <span className="text-muted d-block small">Available Balance</span>
                  <strong className="text-success" style={{ fontSize: '1.1rem' }}>
                    ${parseFloat(cash).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </strong>
                </div>
              )}
              <span className={`badge ${token ? 'badge-success' : 'badge-warning'} mt-1 mr-4`}>
                {token ? 'Status: Connected' : 'Status: Offline'}
              </span>
            </div>
          </header>

          {/* Main Content Area */}
          <main id="js-page-content" role="main" className="page-content">
            <div className="subheader">
              <h1 className="subheader-title">
                <i className='subheader-icon fal fa-chart-area'></i> 
                {token ? `Welcome back, ${username}` : "Market Terminal"}
              </h1>
            </div>
            
            <div className="row">
              <div className="col-xl-6 mx-auto">
                <div id="panel-main" className="panel">
                  <div className="panel-hdr">
                    <h2>
                      {token ? "Execute Trade" : (isRegistering ? "Join C$50 Finance" : "Secure Login")}
                    </h2>
                  </div>
                  <div className="panel-container show">
                    <div className="panel-content">
                      
                      {/* --- ROUTING LOGIC --- */}
                      {token ? (
                        <BuyStock userToken={token} updateBalance={updateBalance} />
                      ) : isRegistering ? (
                        <Register onFinished={() => setIsRegistering(false)} />
                      ) : (
                        <Login setToken={setToken} onRegisterClick={() => setIsRegistering(true)} />
                      )}
                      {/* --- END ROUTING LOGIC --- */}

                    </div>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;