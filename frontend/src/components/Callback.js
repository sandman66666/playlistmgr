import React, { useEffect, useState, useCallback } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';

function Callback() {
  const location = useLocation();
  const { setTokenInfo } = useAuth();
  const [error, setError] = useState('');
  const [isProcessing, setIsProcessing] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const processCallback = useCallback(async () => {
    try {
      const params = new URLSearchParams(location.search);
      const code = params.get('code');
      const state = params.get('state');
      
      // Validate state to prevent CSRF
      const savedState = localStorage.getItem('spotify_auth_state');
      if (state !== savedState) {
        throw new Error('State mismatch');
      }
      
      // Clear state from storage
      localStorage.removeItem('spotify_auth_state');
      
      if (!code) {
        throw new Error('No code provided');
      }

      // Exchange code for token
      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.auth.callback}?code=${code}&state=${state}`);
      if (!response.ok) {
        throw new Error('Failed to exchange code for token');
      }

      const data = await response.json();
      if (!data.token_info || !data.token_info.access_token) {
        throw new Error('Invalid token response');
      }

      // Store token info
      localStorage.setItem('spotify_token', JSON.stringify(data.token_info));
      setTokenInfo(data.token_info);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Error in callback:', error);
      setError(error.message);
    } finally {
      setIsProcessing(false);
    }
  }, [location.search, setTokenInfo]);

  useEffect(() => {
    processCallback();
  }, [processCallback]);

  if (!isProcessing && error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="text-xl text-red-600 mb-4">
            Authentication failed: {error}
          </div>
          <div className="text-gray-600 mb-4">
            Redirecting to login...
          </div>
          <Navigate to="/login" replace />
        </div>
      </div>
    );
  }

  if (!isProcessing && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <div className="text-xl mb-4">
          Completing authentication...
        </div>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
      </div>
    </div>
  );
}

export default Callback;