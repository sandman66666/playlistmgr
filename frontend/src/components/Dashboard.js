import React, { useState, useEffect } from 'react';

function Dashboard({ token, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [userPlaylists, setUserPlaylists] = useState([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch user profile and playlists on component mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        // Fetch profile
        const profileResponse = await fetch('https://api.spotify.com/v1/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const profileData = await profileResponse.json();
        setProfile(profileData);

        // Fetch playlists
        const playlistsResponse = await fetch('https://api.spotify.com/v1/me/playlists', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const playlistsData = await playlistsResponse.json();
        setUserPlaylists(playlistsData.items);
      } catch (error) {
        console.error('Error fetching initial data:', error);
        setError('Failed to load profile or playlists');
      }
    };

    fetchInitialData();
  }, [token]);

  // Search tracks
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `https://api.spotify.com/v1/search?q=${encodeURIComponent(searchQuery)}&type=track&limit=10`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      const data = await response.json();
      setSearchResults(data.tracks.items);
    } catch (error) {
      console.error('Search error:', error);
      setError('Failed to search tracks');
    } finally {
      setLoading(false);
    }
  };

  // Add track to playlist
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
          body: JSON.stringify({
            uris: [trackUri]
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to add track to playlist');
      }

      alert('Track added successfully!');
    } catch (error) {
      console.error('Error adding track:', error);
      setError('Failed to add track to playlist');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">
            Welcome, {profile?.display_name}
          </h1>
          <p className="text-gray-600">Spotify Playlist Manager</p>
        </div>
        <button
          onClick={onLogout}
          className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Search and Results Section */}
        <div className="md:col-span-2">
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for songs..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            {searchResults.map((track) => (
              <div
                key={track.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg shadow"
              >
                <div className="flex items-center space-x-4">
                  {track.album.images[0] && (
                    <img
                      src={track.album.images[0].url}
                      alt={track.album.name}
                      className="w-16 h-16 rounded"
                    />
                  )}
                  <div>
                    <h3 className="font-medium">{track.name}</h3>
                    <p className="text-sm text-gray-500">
                      {track.artists.map(artist => artist.name).join(', ')}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => addToPlaylist(track.uri)}
                  className="px-4 py-2 text-sm text-green-500 border border-green-500 rounded-md hover:bg-green-50"
                  disabled={!selectedPlaylist}
                >
                  Add to Playlist
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Playlists Section */}
        <div>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Your Playlists</h2>
            <select
              value={selectedPlaylist}
              onChange={(e) => setSelectedPlaylist(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              <option value="">Select a playlist</option>
              {userPlaylists.map((playlist) => (
                <option key={playlist.id} value={playlist.id}>
                  {playlist.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;