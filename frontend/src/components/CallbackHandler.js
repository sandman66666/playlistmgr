import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';

function CallbackHandler() {
  const navigate = useNavigate();
  const { token, setTokenInfo } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleCallback = async () => {
      console.log('CallbackHandler: Starting auth callback processing');
      
      // If we already have a token, redirect to dashboard
      if (token) {
        console.log('CallbackHandler: Token already exists, redirecting to dashboard');
        navigate('/dashboard');
        return;
      }

      try {
        // First, try to handle hash-based auth (direct from backend)
        if (window.location.hash) {
          console.log('CallbackHandler: Processing hash-based auth');
          let paramString = window.location.hash;
          
          // Remove the initial '#' or '#/auth?'
          if (paramString.startsWith('#/auth?')) {
            paramString = paramString.replace('#/auth?', '');
          } else if (paramString.startsWith('#')) {
            paramString = paramString.substring(1);
          }

          const params = new URLSearchParams(paramString);
          const access_token = params.get('access_token');
          const refresh_token = params.get('refresh_token');
          const expires_in = params.get('expires_in');
          const expires_at = params.get('expires_at');

          console.log('CallbackHandler: Extracted token info:', {
            hasAccessToken: !!access_token,
            hasRefreshToken: !!refresh_token,
            expiresIn: expires_in,
            expiresAt: expires_at
          });

          if (access_token && refresh_token) {
            const tokenInfo = {
              access_token,
              refresh_token,
              expires_in: parseInt(expires_in, 10),
              expires_at: parseInt(expires_at, 10)
            };

            // Store token info
            localStorage.setItem('spotify_token', JSON.stringify(tokenInfo));
            setTokenInfo(tokenInfo);
            console.log('CallbackHandler: Token info stored, redirecting to dashboard');
            navigate('/dashboard');
            return;
          }
        }

        // If no hash params, try query-based auth
        const queryParams = new URLSearchParams(window.location.search);
        const code = queryParams.get('code');
        const incomingState = queryParams.get('state');
        const queryError = queryParams.get('error');

        if (queryError) {
          console.error('CallbackHandler: Auth error from query params:', queryError);
          throw new Error(`Authentication error: ${queryError}`);
        }

        // Get stored state from localStorage
        const storedState = localStorage.getItem('spotify_auth_state');

        if (code) {
          if (!incomingState || !storedState || incomingState !== storedState) {
            console.error('CallbackHandler: State mismatch or missing state parameter');
            throw new Error('Invalid state parameter. Please try logging in again.');
          }

          console.log('CallbackHandler: Exchanging code for token...');
          const response = await fetch(`${config.apiBaseUrl}${config.endpoints.auth.callback}?code=${code}&state=${incomingState}`, {
            method: 'GET',
            headers: {
              'Accept': 'application/json'
            }
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to exchange code: ${response.statusText}`);
          }

          const data = await response.json();
          console.log('CallbackHandler: Token exchange successful');

          if (data.access_token) {
            const tokenInfo = {
              access_token: data.access_token,
              refresh_token: data.refresh_token,
              expires_at: data.expires_at
            };
            
            localStorage.setItem('spotify_token', JSON.stringify(tokenInfo));
            setTokenInfo(tokenInfo);
            navigate('/dashboard');
          } else {
            throw new Error('No access token in response');
          }
        }

        // Clear URL parameters and stored state
        window.history.replaceState({}, document.title, window.location.pathname);
        localStorage.removeItem('spotify_auth_state');

      } catch (error) {
        console.error('CallbackHandler: Error processing callback:', error);
        setError(error.message);
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    handleCallback();
  }, [token, setTokenInfo, navigate]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="p-8 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-red-600">{error}</h2>
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">Processing authentication...</h2>
        <div className="w-8 h-8 border-4 border-t-blue-500 border-b-blue-500 rounded-full animate-spin mx-auto"></div>
      </div>
    </div>
  );
}

export default CallbackHandler;