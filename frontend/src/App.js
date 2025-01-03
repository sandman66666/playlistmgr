import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import BrandPlaylist from './components/BrandPlaylist';
import Callback from './components/Callback';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  const location = useLocation();
  
  // Show nothing while checking authentication
  if (loading) {
    return null;
  }
  
  if (!token) {
    // Pass the attempted location to redirect back after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
};

// App wrapper to provide auth context
const AppWrapper = () => {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
};

// Main App component
function App() {
  const { token } = useAuth();
  
  return (
    <Routes>
      <Route path="/login" element={
        token ? <Navigate to="/dashboard" replace /> : <Login />
      } />
      <Route path="/auth" element={<Callback />} />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="/brands" element={
        <ProtectedRoute>
          <BrandPlaylist />
        </ProtectedRoute>
      } />
      <Route path="/" element={
        token ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
      } />
    </Routes>
  );
}

// Export wrapped version
export default function Root() {
  return (
    <Router>
      <AppWrapper />
    </Router>
  );
}