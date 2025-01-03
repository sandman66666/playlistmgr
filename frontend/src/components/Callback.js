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
        console.log('Processing callback with location:', location);
        console.log('Raw hash:', location.hash);
        
        // Handle both hash formats:
        // 1. '#access_token=...' (direct from Spotify)
        // 2. '#/auth?access_token=...' (from our router)
        let paramString = location.hash;
        if (paramString.startsWith('#/auth?')) {
          paramString = paramString.replace('#/auth?', '');
        } else if (paramString.startsWith('#')) {
          paramString = paramString.substring(1);
        }
        
        console.log('Processed param string:', paramString);
        const params = new URLSearchParams(paramString);
        
        // Check for error
        const error = params.get('error');
        if (error) {
          throw new Error(error);
        }

        // Get token info
        const access_token = params.get('access_token');
        const refresh_token = params.get('refresh_token');
        const expires_in = params.get('expires_in');
        const expires_at = params.get('expires_at');

        console.log('Extracted tokens:', { 
          hasAccessToken: !!access_token,
          hasRefreshToken: !!refresh_token,
          expiresIn: expires_in,
          expiresAt: expires_at,
          rawParams: Object.fromEntries(params.entries())
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

    if (location.hash) {
      processCallback();
    } else {
      console.log('No hash parameters found in URL');
      setError('No authentication data received');
      setIsProcessing(false);
    }
  }, [location.hash, setTokenInfo]);

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