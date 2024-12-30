import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function Dashboard() {
  const { token, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [userPlaylists, setUserPlaylists] = useState([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchUserPlaylists = useCallback(async () => {
    if (!token) return;
    try {
      setLoading(true);
      const response = await fetch('https://api.spotify.com/v1/me/playlists', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Failed to fetch playlists');
      const data = await response.json();
      setUserPlaylists(data.items || []);
    } catch (error) {
      setError('Failed to load playlists');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchUserPlaylists();
  }, [fetchUserPlaylists]);

  const handleSearch = useCallback(async (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || !token) return;
    try {
      setLoading(true);
      const response = await fetch(
        `https://api.spotify.com/v1/search?q=${encodeURIComponent(searchQuery)}&type=track`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      setSearchResults(data.tracks?.items || []);
    } catch (error) {
      setError('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, token]);

  const addToPlaylist = async (trackUri) => {
    if (!selectedPlaylist) {
      setError('Please select a playlist first');
      return;
    }
    try {
      const response = await fetch(
        `https://api.spotify.com/v1/playlists/${selectedPlaylist}/tracks`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ uris: [trackUri] })
        }
      );
      if (!response.ok) throw new Error('Failed to add track');
      alert('Track added successfully!');
      fetchUserPlaylists(); // Refresh playlists
    } catch (error) {
      setError('Failed to add track to playlist');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Spotify Playlist Manager</h1>
        <div className="space-x-4">
          <Link to="/brands" className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
            Brand Playlists
          </Link>
          <button onClick={logout} className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">
            Logout
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="md:col-span-3">
          <form onSubmit={handleSearch} className="flex gap-4 mb-8">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for tracks..."
              className="flex-1 p-2 border border-gray-300 rounded"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>

          {searchResults.length > 0 && (
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-4">Search Results</h2>
              <div className="grid grid-cols-1 gap-4">
                {searchResults.map(track => (
                  <div key={track.id} className="p-4 bg-white rounded-lg shadow flex justify-between items-center">
                    <div>
                      <div className="font-medium">{track.name}</div>
                      <div className="text-sm text-gray-600">{track.artists.map(a => a.name).join(', ')}</div>
                      <div className="text-sm text-gray-500">{track.album.name}</div>
                    </div>
                    <button
                      onClick={() => addToPlaylist(track.uri)}
                      disabled={!selectedPlaylist}
                      className="px-4 py-2 text-white bg-green-500 rounded hover:bg-green-600 disabled:bg-gray-400"
                    >
                      Add to Playlist
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="md:col-span-1">
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-bold mb-4">Select Playlist</h2>
            <select
              value={selectedPlaylist}
              onChange={(e) => setSelectedPlaylist(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded mb-4"
            >
              <option value="">Choose a playlist...</option>
              {userPlaylists.map(playlist => (
                <option key={playlist.id} value={playlist.id}>
                  {playlist.name}
                </option>
              ))}
            </select>

            <h3 className="font-bold mb-2">Your Playlists</h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {userPlaylists.map(playlist => (
                <div
                  key={playlist.id}
                  onClick={() => setSelectedPlaylist(playlist.id)}
                  className={`p-2 rounded cursor-pointer ${
                    selectedPlaylist === playlist.id ? 'bg-green-100' : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="font-medium">{playlist.name}</div>
                  <div className="text-sm text-gray-600">{playlist.tracks.total} tracks</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;