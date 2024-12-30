import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function BrandPlaylist() {
  const navigate = useNavigate();
  const { token, getAccessToken } = useAuth();
  const [brands, setBrands] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [brandProfile, setBrandProfile] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 1. Fetch brand list
  const fetchBrands = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      setError('');
      const response = await fetch('http://localhost:3001/brands');
      if (!response.ok) {
        throw new Error(`Failed to fetch brands: ${response.statusText}`);
      }
      const data = await response.json();
      setBrands(data.brands || []);
    } catch (err) {
      console.error('Error fetching brands:', err);
      setError('Failed to load brands. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // 2. On mount or token update, load brand list
  useEffect(() => {
    if (token) {
      fetchBrands();
    }
  }, [token, fetchBrands]);

  // 3. Handle brand selection
  const handleBrandSelect = async (brandId) => {
    if (!brandId || !token) return;
    try {
      setLoading(true);
      setError('');

      // Get brand profile
      const profileRes = await fetch(`http://localhost:3001/brands/${brandId}`);
      if (!profileRes.ok) {
        throw new Error(`Failed to fetch brand profile: ${profileRes.statusText}`);
      }
      const profileData = await profileRes.json();
      setBrandProfile(profileData);
      setSelectedBrand(brandId);

      // Get music suggestions from Anthropic
      const suggestRes = await fetch('http://localhost:3001/brands/suggest-music', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData),
      });
      if (!suggestRes.ok) {
        throw new Error(`Failed to get music suggestions: ${suggestRes.statusText}`);
      }
      const suggestionsData = await suggestRes.json();
      setSuggestions(suggestionsData.suggestions || []);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
      setBrandProfile(null);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  // 4. Create Spotify playlist
  const createPlaylist = async () => {
    if (!token) {
      setError('Please log in to create a playlist');
      return;
    }
    if (!selectedBrand) {
      setError('Please select a brand first');
      return;
    }
    if (!suggestions || suggestions.length === 0) {
      setError('No songs to add to playlist');
      return;
    }

    try {
      setLoading(true);
      setError('');

      // Get fresh access token
      const accessToken = await getAccessToken();
      if (!accessToken) {
        throw new Error('Failed to get access token');
      }
      
      const response = await fetch('http://localhost:3001/brands/create-playlist', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          token: accessToken,
          brand_id: selectedBrand,
          suggestions: suggestions
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || 'Failed to create playlist');
      }

      const data = await response.json();
      alert(`Playlist created successfully! You can find it at: ${data.playlist_url}`);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'Failed to create playlist. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Please Log In</h2>
          <Link to="/login" className="text-green-500 hover:text-green-600">
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Brand-Based Playlist Creator</h2>
        <Link to="/dashboard" className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600">
          Back to Dashboard
        </Link>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Brand dropdown */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select a Brand</label>
        <select
          className="w-full p-2 border border-gray-300 rounded-md"
          onChange={(e) => handleBrandSelect(e.target.value)}
          value={selectedBrand || ''}
          disabled={loading}
        >
          <option value="">Choose a brand...</option>
          {brands.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-xl">Loading...</div>
        </div>
      )}

      {/* Brand Profile Info */}
      {brandProfile && !loading && (
        <div className="mb-8 p-4 bg-white rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">{brandProfile.brand}</h3>
          <div className="prose">
            <h4 className="font-medium">Brand Essence</h4>
            <p>{brandProfile.brand_essence?.core_identity}</p>
            
            <h4 className="font-medium mt-4">Aesthetic Pillars</h4>
            <ul className="list-disc pl-5">
              {brandProfile.aesthetic_pillars?.visual_language?.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Claude Suggestions */}
      {suggestions.length > 0 && !loading && (
        <div className="mb-8">
          <h3 className="text-xl font-semibold mb-4">Suggested Tracks</h3>
          <div className="space-y-4">
            {suggestions.map((s, idx) => (
              <div key={idx} className="p-4 bg-white rounded-lg shadow">
                <p className="font-medium">{s.track}</p>
                <p className="text-sm text-gray-600">{s.artist}</p>
                <p className="text-sm text-gray-500 mt-2">{s.reason}</p>
              </div>
            ))}
          </div>

          <button
            onClick={createPlaylist}
            disabled={loading}
            className="mt-4 px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-gray-400"
          >
            {loading ? 'Creating...' : 'Create Playlist'}
          </button>
        </div>
      )}
    </div>
  );
}

export default BrandPlaylist;