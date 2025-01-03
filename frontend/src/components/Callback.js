import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Callback() {
  const location = useLocation();
  const { setTokenInfo } = useAuth();
  const [error, setError] = useState('');
  const [isProcessing, setIsProcessing] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const processCallback = async () => {
      try {
        console.log('Processing callback with hash:', location.hash);
        
        // Check for error in search params first
        const searchParams = new URLSearchParams(location.search);
        const searchError = searchParams.get('error');
        if (searchError) {
          throw new Error(searchError);
        }

        // Get token info from hash fragment
        // Remove '#/auth?' prefix to get just the params
        const hashString = location.hash.substring(2); // Remove '/#' prefix
        console.log('Parsed hash string:', hashString);
        
        const hashParams = new URLSearchParams(hashString);
        const error = hashParams.get('error');
        
        if (error) {
          throw new Error(error);
        }

        // Get token info from hash params
        const access_token = hashParams.get('access_token');
        const refresh_token = hashParams.get('refresh_token');
        const expires_in = hashParams.get('expires_in');
        const expires_at = hashParams.get('expires_at');

        console.log('Extracted tokens:', { 
          hasAccessToken: !!access_token,
          hasRefreshToken: !!refresh_token,
          expiresIn: expires_in,
          expiresAt: expires_at
        });

        if (!access_token || !refresh_token) {
          throw new Error('Missing token information');
        }

        const tokenInfo = {
          access_token,
          refresh_token,
          expires_in: parseInt(expires_in, 10),
          expires_at: parseInt(expires_at, 10)
        };

        // Store token info
        localStorage.setItem('spotify_token', JSON.stringify(tokenInfo));
        setTokenInfo(tokenInfo);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error in callback:', error);
        setError(error.message);
      } finally {
        setIsProcessing(false);
      }
    };

    processCallback();
  }, [location.search, location.hash, setTokenInfo]);

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