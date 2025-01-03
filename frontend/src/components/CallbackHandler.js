import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';

function CallbackHandler() {
  const navigate = useNavigate();
  const { token, setToken } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const handleCallback = async () => {
      // If we already have a token, redirect to dashboard
      if (token) {
        navigate('/dashboard');
        return;
      }

      const params = new URLSearchParams(window.location.search);
      const code = params.get('code');
      const incomingState = params.get('state');
      const error = params.get('error');

      // Get stored state from localStorage
      const storedState = localStorage.getItem('spotify_auth_state');

      // Clear URL parameters and stored state
      window.history.replaceState({}, document.title, window.location.pathname);
      localStorage.removeItem('spotify_auth_state');

      if (error) {
        console.error('Auth error:', error);
        setError(`Authentication error: ${error}`);
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      if (!incomingState || !storedState || incomingState !== storedState) {
        console.error('State mismatch or missing state parameter');
        setError('Invalid state parameter. Please try logging in again.');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      if (code) {
        try {
          console.log('Exchanging code for token...');
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
          console.log('Token exchange successful');

          if (data.access_token) {
            // Store token data
            localStorage.setItem('spotify_token', JSON.stringify({
              access_token: data.access_token,
              refresh_token: data.refresh_token,
              expires_at: data.expires_at
            }));
            
            setToken(data.access_token);
            navigate('/dashboard');
          } else {
            throw new Error('No access token in response');
          }
        } catch (error) {
          console.error('Error exchanging code for token:', error);
          setError(error.message);
          setTimeout(() => navigate('/login'), 3000);
        }
      }
    };

    handleCallback();
  }, [token, setToken, navigate]);

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