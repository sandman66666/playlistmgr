import React, { useState, useEffect } from 'react';

function Login() {
  const [debugLog, setDebugLog] = useState(() => {
    // Initialize from localStorage if exists
    const saved = localStorage.getItem('spotify_debug_log');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    // Check URL parameters on component mount
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const error = urlParams.get('error');
    
    if (code) {
      addDebugMessage(`Received code parameter: ${code.substring(0, 10)}...`);
    }
    if (error) {
      addDebugMessage(`Received error: ${error}`);
    }
  }, []);

  const addDebugMessage = (message) => {
    const newLog = [...debugLog, `${new Date().toISOString()}: ${message}`];
    setDebugLog(newLog);
    localStorage.setItem('spotify_debug_log', JSON.stringify(newLog));
  };

  const clearDebugLog = () => {
    setDebugLog([]);
    localStorage.removeItem('spotify_debug_log');
  };

  const handleLogin = async () => {
    try {
      addDebugMessage('Starting login process...');
      
      const response = await fetch('http://localhost:3001/auth/login');
      addDebugMessage(`Response status: ${response.status}`);
      
      const data = await response.json();
      addDebugMessage(`Received data: ${JSON.stringify(data)}`);
      
      if (data.auth_url) {
        addDebugMessage(`Redirecting to: ${data.auth_url}`);
        window.location.href = data.auth_url;
      } else {
        addDebugMessage('No auth_url in response');
      }
    } catch (error) {
      addDebugMessage(`Error: ${error.message}`);
      console.error('Login error:', error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-center mb-6">Spotify Playlist Manager</h1>
        
        <button
          onClick={handleLogin}
          className="w-full px-6 py-3 text-white bg-green-500 rounded-lg hover:bg-green-600 transition-colors"
        >
          Login with Spotify
        </button>

        {/* Debug Controls */}
        <div className="mt-4 flex justify-between">
          <button
            onClick={clearDebugLog}
            className="text-sm text-red-500 hover:text-red-600"
          >
            Clear Debug Log
          </button>
          <span className="text-sm text-gray-500">
            {debugLog.length} log entries
          </span>
        </div>

        {/* Debug Log Display */}
        <div className="mt-4">
          <h2 className="text-lg font-semibold mb-2">Debug Log:</h2>
          <div className="bg-gray-100 p-4 rounded-lg max-h-60 overflow-auto">
            {debugLog.map((log, index) => (
              <div key={index} className="text-sm font-mono mb-1 break-all whitespace-pre-wrap">
                {log}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;