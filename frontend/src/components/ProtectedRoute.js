import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ token, children }) => {
  if (!token) {
    // No token? Send them to login! 🚪
    return <Navigate to="/login" replace />;
  }

  // Token exists? Show the protected page 🔓
  return children;
};

export default ProtectedRoute;