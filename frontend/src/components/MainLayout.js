import React from 'react';
import { Link, Outlet } from 'react-router-dom';

const MainLayout = ({ token, username, cash, handleLogout }) => {
  return (
    <div className="page-wrapper">
      <div className="page-inner">
        {/* Sidebar */}
        <aside className="page-sidebar" style={{ minWidth: '250px', background: '#333', display: 'block' }}>          <div className="page-logo">
            <span className="page-logo-text">C$50 Finance</span>
          </div>
          <nav className="primary-nav">
            <ul className="nav-menu">
              <li><Link to="/"><i className="fal fa-home"></i> Home</Link></li>
              {token && (
                <>
                  <li><Link to="/dashboard"><i className="fal fa-tachometer"></i> Dashboard</Link></li>
                  <li><Link to="/buy"><i className="fal fa-shopping-cart"></i> Buy</Link></li>
                  <li><Link to="/sell"><i className="fal fa-dollar-sign"></i> Sell</Link></li>
                  <li><Link to="/history"><i className="fal fa-history"></i> History</Link></li>
                </>
              )}
            </ul>
          </nav>
        </aside>

        <div className="page-content-wrapper">
          <header className="page-header">
             {/* Header content with Balance/Logout */}
             <div className="ml-auto d-flex align-items-center">
                {token && <span className="mr-3">Balance: ${cash}</span>}
                {token ? (
                  <button onClick={handleLogout} className="btn btn-sm btn-outline-danger">Logout</button>
                ) : (
                  <Link to="/login" className="btn btn-sm btn-primary">Login</Link>
                )}
             </div>
          </header>
          
          <main className="page-content">
            {/* The actual page content loads here! */}
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};

export default MainLayout;