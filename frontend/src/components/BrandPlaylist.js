import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function BrandPlaylist() {
  const navigate = useNavigate();
  const { token, loading: authLoading, checkAuth } = useAuth();
  const [brands, setBrands] = useState([]);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [brandProfile, setBrandProfile] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
    } catch (error) {
      console.error('Error fetching brands:', error);
      setError('Failed to load brands. Please try again later.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    const init = async () => {
      const isAuthenticated = await checkAuth();
      if (isAuthenticated) {
        fetchBrands();
      }
    };

    init();
  }, [checkAuth, fetchBrands]);

  const handleBrandSelect = async (brandId) => {
    if (!brandId || !token) return;
    
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch(`http://localhost:3001/brands/${brandId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch brand profile: ${response.statusText}`);
      }
      
      const data = await response.json();
      setBrandProfile(data);
      setSelectedBrand(brandId);
      
      // Get music suggestions from Anthropic
      const suggestionsResponse = await fetch('http://localhost:3001/brands/suggest-music', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      if (!suggestionsResponse.ok) {
        throw new Error(`Failed to get music suggestions: ${suggestionsResponse.statusText}`);
      }
      
      const suggestionsData = await suggestionsResponse.json();
      setSuggestions(suggestionsData.suggestions || []);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to load brand profile or get music suggestions. Please try again later.');
      setBrandProfile(null);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const createPlaylist = async () => {
    if (!token) {
      setError('Please log in to create a playlist');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('http://localhost:3001/brands/create-playlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          brand_id: selectedBrand,
          suggestions: suggestions
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create playlist: ${response.statusText}`);
      }
      
      const data = await response.json();
      alert(`Playlist created successfully! You can find it at: ${data.playlist_url}`);
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to create playlist. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

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
        <Link
          to="/dashboard"
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Back to Dashboard
        </Link>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {/* Brand Selection */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select a Brand
        </label>
        <select
          className="w-full p-2 border border-gray-300 rounded-md"
          onChange={(e) => handleBrandSelect(e.target.value)}
          value={selectedBrand || ''}
          disabled={loading}
        >
          <option value="">Choose a brand...</option>
          {brands.map((brand) => (
            <option key={brand.id} value={brand.id}>
              {brand.name}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-xl">Loading...</div>
        </div>
      )}

      {/* Brand Profile Display */}
      {brandProfile && !loading && (
        <div className="mb-8 p-4 bg-white rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">{brandProfile.brand}</h3>
          <div className="prose">
            <h4 className="font-medium">Brand Essence</h4>
            <p>{brandProfile.brand_essence?.core_identity}</p>
            
            <h4 className="font-medium mt-4">Aesthetic Pillars</h4>
            <ul className="list-disc pl-5">
              {brandProfile.aesthetic_pillars?.visual_language?.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>

            <h4 className="font-medium mt-4">Cultural Values</h4>
            <ul className="list-disc pl-5">
              {brandProfile.cultural_positioning?.core_values?.map((value, index) => (
                <li key={index}>{value}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Music Suggestions */}
      {suggestions.length > 0 && !loading && (
        <div className="mb-8">
          <h3 className="text-xl font-semibold mb-4">Suggested Tracks</h3>
          <div className="space-y-4">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="p-4 bg-white rounded-lg shadow">
                <p className="font-medium">{suggestion.track}</p>
                <p className="text-sm text-gray-600">{suggestion.artist}</p>
                <p className="text-sm text-gray-500 mt-2">{suggestion.reason}</p>
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