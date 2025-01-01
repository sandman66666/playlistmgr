import React, { useState, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Login() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { token } = useAuth();

  // If already logged in, redirect to dashboard
  if (token) {
    return <Navigate to="/dashboard" replace />;
  }

  const initiateLogin = useCallback(async () => {
    if (loading) return;
    
    try {
      setError('');
      setLoading(true);

      // Get login URL from backend
      const response = await fetch('http://localhost:3001/auth/login');
      if (!response.ok) {
        throw new Error('Failed to get login URL');
      }

      const data = await response.json();
      if (!data.auth_url) {
        throw new Error('Invalid login URL');
      }

      // Extract state parameter from auth_url
      const url = new URL(data.auth_url);
      const state = url.searchParams.get('state');
      if (state) {
        // Save state in localStorage for CSRF protection
        localStorage.setItem('spotify_auth_state', state);
      }

      // Redirect to Spotify login
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Login error:', error);
      setError(error.message);
      setLoading(false);
    }
  }, [loading]);

  if (loading && !error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="text-xl mb-4">
            Connecting to Spotify...
          </div>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="text-xl text-red-600 mb-4">
            Failed to connect to Spotify: {error}
          </div>
          <button
            onClick={() => {
              setError('');
              initiateLogin();
            }}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-8">Spotify Playlist Manager</h1>
        <button
          onClick={initiateLogin}
          disabled={loading}
          className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          Connect with Spotify
        </button>
      </div>
    </div>
  );
}

export default Login;