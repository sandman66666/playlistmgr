import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => {
    // Try to get existing token from localStorage
    const savedToken = localStorage.getItem('spotify_token');
    if (savedToken) {
      try {
        // Verify token format
        const tokenData = JSON.parse(savedToken);
        return tokenData.access_token;
      } catch (e) {
        // If token is not in JSON format, it might be the raw token
        return savedToken;
      }
    }
    return null;
  });
  
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const error = urlParams.get('error');

      if (error) {
        console.error('Auth error:', error);
        navigate('/login');
        setLoading(false);
        return;
      }

      if (code && !token) {
        try {
          console.log('Exchanging code for token...');
          const response = await fetch(`http://localhost:3001/auth/callback?code=${code}`);
          
          if (!response.ok) {
            throw new Error(`Failed to exchange code: ${response.statusText}`);
          }

          const data = await response.json();
          console.log('Received token data:', { ...data, access_token: '***' });

          if (data.access_token) {
            // Store the complete token data
            localStorage.setItem('spotify_token', JSON.stringify(data));
            setToken(data.access_token);
            navigate('/dashboard');
          } else {
            throw new Error('No access token in response');
          }
        } catch (error) {
          console.error('Error exchanging code for token:', error);
          navigate('/login');
        }
      }
      setLoading(false);
    };

    handleCallback();
  }, [token, navigate]);

  const logout = () => {
    setToken(null);
    localStorage.removeItem('spotify_token');
    navigate('/login');
  };

  const refreshToken = async () => {
    try {
      const tokenData = localStorage.getItem('spotify_token');
      if (!tokenData) return null;

      const parsedToken = JSON.parse(tokenData);
      if (!parsedToken.refresh_token) return null;

      const response = await fetch('http://localhost:3001/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: parsedToken.refresh_token
        })
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const newTokenData = await response.json();
      localStorage.setItem('spotify_token', JSON.stringify(newTokenData));
      setToken(newTokenData.access_token);
      return newTokenData.access_token;
    } catch (error) {
      console.error('Error refreshing token:', error);
      logout();
      return null;
    }
  };

  const getAccessToken = async () => {
    try {
      const tokenData = localStorage.getItem('spotify_token');
      if (!tokenData) return null;

      const parsedToken = JSON.parse(tokenData);
      if (!parsedToken.access_token) return null;

      // Check if token is expired
      const expiresAt = parsedToken.expires_at;
      if (expiresAt && Date.now() >= expiresAt * 1000) {
        // Token is expired, try to refresh
        return await refreshToken();
      }

      return parsedToken.access_token;
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="text-xl">Loading...</div>
    </div>;
  }

  return (
    <AuthContext.Provider value={{ 
      token, 
      setToken, 
      logout,
      refreshToken,
      getAccessToken
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};