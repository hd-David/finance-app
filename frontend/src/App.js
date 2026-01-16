import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import BuyStock from './components/BuyStock';
import SellStock from './components/SellStock';
import Quote from './components/Quote';
import History from './components/History';
import Login from './components/Login';
import Register from './components/Register';

function App() {
  // 1. Core State
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isRegistering, setIsRegistering] = useState(false);
  const [cash, setCash] = useState(0);
  const [username, setUsername] = useState("Guest");
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

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
    setCurrentView('dashboard');
  };

  const updateBalance = (newBalance) => {
    setCash(newBalance);
  };

  const navigateTo = (view) => {
    setCurrentView(view);
    setSidebarOpen(false);
  };

  const getViewTitle = () => {
    if (!token) return isRegistering ? "Join C$50 Finance" : "Secure Login";
    
    switch (currentView) {
      case 'dashboard': return 'Portfolio Dashboard';
      case 'buy': return 'Buy Stocks';
      case 'sell': return 'Sell Stocks';
      case 'quote': return 'Stock Quote';
      case 'history': return 'Transaction History';
      default: return 'Dashboard';
    }
  };

  const renderContent = () => {
    if (!token) {
      return isRegistering ? (
        <Register onFinished={() => setIsRegistering(false)} />
      ) : (
        <Login setToken={setToken} onRegisterClick={() => setIsRegistering(true)} />
      );
    }

    switch (currentView) {
      case 'dashboard':
        return <Dashboard userToken={token} cash={cash} />;
      case 'buy':
        return <BuyStock userToken={token} updateBalance={updateBalance} />;
      case 'sell':
        return <SellStock userToken={token} updateBalance={updateBalance} />;
      case 'quote':
        return <Quote userToken={token} />;
      case 'history':
        return <History userToken={token} />;
      default:
        return <Dashboard userToken={token} cash={cash} />;
    }
  };

  return (
    <div className="page-wrapper">
      <div className="page-inner">
        
        {/* Left Sidebar */}
        <aside className={`page-sidebar ${sidebarOpen ? 'mobile-open' : ''}`}>
          <div className="page-logo">
            <span className="page-logo-text">C$50 Finance</span>
          </div>
          <nav id="js-primary-nav" className="primary-nav" role="navigation">
            <ul id="js-nav-menu" className="nav-menu">
              {token ? (
                <>
                  <li className={currentView === 'dashboard' ? 'active' : ''}>
                    <a href="#dashboard" onClick={(e) => { e.preventDefault(); navigateTo('dashboard'); }}>
                      <i className="fal fa-home"></i> Dashboard
                    </a>
                  </li>
                  <li className={currentView === 'buy' ? 'active' : ''}>
                    <a href="#buy" onClick={(e) => { e.preventDefault(); navigateTo('buy'); }}>
                      <i className="fal fa-shopping-cart"></i> Buy
                    </a>
                  </li>
                  <li className={currentView === 'sell' ? 'active' : ''}>
                    <a href="#sell" onClick={(e) => { e.preventDefault(); navigateTo('sell'); }}>
                      <i className="fal fa-hand-holding-usd"></i> Sell
                    </a>
                  </li>
                  <li className={currentView === 'quote' ? 'active' : ''}>
                    <a href="#quote" onClick={(e) => { e.preventDefault(); navigateTo('quote'); }}>
                      <i className="fal fa-search-dollar"></i> Quote
                    </a>
                  </li>
                  <li className={currentView === 'history' ? 'active' : ''}>
                    <a href="#history" onClick={(e) => { e.preventDefault(); navigateTo('history'); }}>
                      <i className="fal fa-history"></i> History
                    </a>
                  </li>
                  <li className="nav-divider"></li>
                  <li>
                    <a href="#logout" onClick={(e) => { e.preventDefault(); handleLogout(); }}>
                      <i className="fal fa-sign-out"></i> Logout
                    </a>
                  </li>
                </>
              ) : (
                <>
                  <li className="active">
                    <a href="/"><i className="fal fa-home"></i> Dashboard</a>
                  </li>
                  <li>
                    <a href="#register" onClick={(e) => { e.preventDefault(); setIsRegistering(!isRegistering); }}>
                      <i className={isRegistering ? "fal fa-sign-in" : "fal fa-user-plus"}></i>
                      {isRegistering ? " Switch to Login" : " Register Account"}
                    </a>
                  </li>
                </>
              )}
            </ul>
          </nav>
        </aside>

        {/* Mobile Sidebar Overlay */}
        {sidebarOpen && (
          <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)}></div>
        )}

        <div className="page-content-wrapper">
          {/* Header */}
          <header className="page-header" role="banner">
            <button 
              className="mobile-menu-toggle btn btn-link"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <i className="fal fa-bars fa-lg"></i>
            </button>
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
              <div className={`${currentView === 'dashboard' ? 'col-xl-12' : 'col-xl-6'} mx-auto`}>
                <div id="panel-main" className="panel">
                  <div className="panel-hdr">
                    <h2>{getViewTitle()}</h2>
                  </div>
                  <div className="panel-container show">
                    <div className="panel-content">
                      {renderContent()}
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