import React, { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import debounce from 'lodash/debounce';
import config from '../config';

const AuthContext = createContext(null);

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

// Debounce delay for token validation (1 second)
const VALIDATION_DELAY = 1000;

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [tokenInfo, setTokenInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const lastValidationRef = useRef(0);
  const navigate = useNavigate();

  // Initialize token from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('spotify_token');
    if (storedToken) {
      try {
        const parsedToken = JSON.parse(storedToken);
        setTokenInfo(parsedToken);
        setToken(parsedToken.access_token);
      } catch (e) {
        console.error('Error parsing stored token:', e);
        localStorage.removeItem('spotify_token');
      }
    }
    setLoading(false);
  }, []);

  // Token validation function
  const validateTokenFn = useCallback(async (tokenToValidate, tokenInfoToValidate) => {
    try {
      const now = Date.now();
      // Skip validation if within cache duration
      if (now - lastValidationRef.current < CACHE_DURATION) {
        return true;
      }

      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.auth.validate}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokenToValidate}`
        },
        body: JSON.stringify({ token_info: tokenInfoToValidate })
      });

      const data = await response.json();
      lastValidationRef.current = now;

      if (data.token_info) {
        localStorage.setItem('spotify_token', JSON.stringify(data.token_info));
        setTokenInfo(data.token_info);
        setToken(data.token_info.access_token);
      }

      return data.valid;
    } catch (e) {
      console.error('Token validation error:', e);
      return false;
    }
  }, [setToken, setTokenInfo]); // Add dependencies for state setters

  // Debounced validate token
  const validateToken = useCallback(
    debounce(validateTokenFn, VALIDATION_DELAY),
    [validateTokenFn]
  );

  const refreshToken = useCallback(async () => {
    if (!tokenInfo?.refresh_token) {
      console.error('No refresh token available');
      return false;
    }

    try {
      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.auth.refresh}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          refresh_token: tokenInfo.refresh_token
        })
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const newTokenInfo = await response.json();
      localStorage.setItem('spotify_token', JSON.stringify(newTokenInfo));
      setTokenInfo(newTokenInfo);
      setToken(newTokenInfo.access_token);
      return true;
    } catch (e) {
      console.error('Token refresh error:', e);
      return false;
    }
  }, [token, tokenInfo?.refresh_token]);

  const logout = useCallback(() => {
    localStorage.removeItem('spotify_token');
    setToken(null);
    setTokenInfo(null);
    navigate('/login');
  }, [navigate]);

  const getAuthHeader = useCallback(async () => {
    if (!token || !tokenInfo) {
      return null;
    }

    try {
      const isValid = await validateToken(token, tokenInfo);
      if (!isValid) {
        const refreshed = await refreshToken();
        if (!refreshed) {
          logout();
          return null;
        }
      }
      return `Bearer ${token}`;
    } catch (e) {
      console.error('Error getting auth header:', e);
      return null;
    }
  }, [token, tokenInfo, validateToken, refreshToken, logout]);

  const login = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.auth.login}`);
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (e) {
      console.error('Login error:', e);
      setError('Failed to initiate login');
    } finally {
      setLoading(false);
    }
  }, []);

  const value = {
    token,
    tokenInfo,
    loading,
    error,
    login,
    logout,
    setTokenInfo,
    getAuthHeader
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}