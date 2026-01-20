import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// Layout & Security
import MainLayout from './components/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './components/Login';
import Register from './components/Register';
import BuyStock from './components/BuyStock';
import Dashboard from './components/Dashboard'; 
import SellStock from './components/SellStock';
import History from './components/History';
import LandingPage from './components/LandingPage';


function App() {
  // 1. Core State 💾
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [cash, setCash] = useState(0);
  const [username, setUsername] = useState("Guest");

  // 2. Profile Sync 🔄
 useEffect(() => {
  if (!token) return;

  fetch('http://localhost:5000/api/user', {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(res =>
    res.json().then(data => {
      if (!res.ok) {
        console.error("User API error:", data);
        throw new Error(data.msg || "Profile fetch failed");
      }
      return data;
    })
  )
  .then(data => {
    setCash(data.cash);
    setUsername(data.username);
  })
  .catch(err => {
    console.error("Profile fetch error:", err.message);
  });
}, [token]);


  // 3. Actions ⚡
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCash(0);
    setUsername("Guest");
  };

  const updateBalance = (newBalance) => {
    setCash(newBalance);
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* The Frame: Always shows Sidebar & Header */}
        <Route element={<MainLayout token={token} cash={cash} username={username} handleLogout={handleLogout} />}>
          
          {/* Public Routes 🔓 */}
          <Route path="/" element={<LandingPage token={token} />} />
          <Route path="/login" element={<Login setToken={setToken} />} />
          <Route path="/register" element={<Register />} />

                          {/* Protected Routes 🛡️ */}
                  <Route path="/dashboard" element={
                    <ProtectedRoute token={token}>
                      <Dashboard userToken={token} /> {/* Added userToken here */}
                    </ProtectedRoute>
                  } />

                  <Route path="/buy" element={
                    <ProtectedRoute token={token}>
                      <BuyStock userToken={token} updateBalance={updateBalance} />
                    </ProtectedRoute>
                  } />

                  <Route path="/sell" element={
                    <ProtectedRoute token={token}>
                      <SellStock userToken={token} /> {/* Added userToken here */}
                    </ProtectedRoute>
                  } />

                  <Route path="/history" element={
                    <ProtectedRoute token={token}>
                      <History userToken={token} /> {/* Added userToken here */}
                    </ProtectedRoute>
                  } />
                            
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;