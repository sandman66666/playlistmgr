import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';

function Dashboard() {
  const { logout, getAuthHeader } = useAuth();
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedSong, setSelectedSong] = useState(null);
  const [showPlaylistModal, setShowPlaylistModal] = useState(false);
  const [addingToPlaylist, setAddingToPlaylist] = useState(false);

  const fetchPlaylists = useCallback(async () => {
    try {
      setError('');
      const authHeader = await getAuthHeader();
      if (!authHeader) {
        throw new Error('No valid authentication');
      }

      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.playlist.user}`, {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch playlists');
      }

      const data = await response.json();
      setPlaylists(data.playlists || []);
    } catch (error) {
      console.error('Error fetching playlists:', error);
      setError(error.message);
      if (error.message.includes('authentication') || error.message.includes('token')) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  }, [getAuthHeader, logout]);

  const searchSongs = useCallback(async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setSearchLoading(true);
      const authHeader = await getAuthHeader();
      if (!authHeader) {
        throw new Error('No valid authentication');
      }

      const response = await fetch(`${config.apiBaseUrl}/tracks?q=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to search songs');
      }

      const data = await response.json();
      setSearchResults(data.tracks || []);
    } catch (error) {
      console.error('Error searching songs:', error);
      setError(error.message);
    } finally {
      setSearchLoading(false);
    }
  }, [searchQuery, getAuthHeader]);

  const addToPlaylist = async (playlistId) => {
    if (!selectedSong) return;

    try {
      setAddingToPlaylist(true);
      const authHeader = await getAuthHeader();
      if (!authHeader) {
        throw new Error('No valid authentication');
      }

      const response = await fetch(`${config.apiBaseUrl}${config.endpoints.playlist.addTracks(playlistId)}`, {
        method: 'POST',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          uris: [selectedSong.uri]
        })
      });

      if (!response.ok) {
        throw new Error('Failed to add song to playlist');
      }

      // Refresh playlists to show updated track count
      await fetchPlaylists();
      setShowPlaylistModal(false);
      setSelectedSong(null);
      alert('Song added to playlist successfully!');
    } catch (error) {
      console.error('Error adding song to playlist:', error);
      setError(error.message);
    } finally {
      setAddingToPlaylist(false);
    }
  };

  useEffect(() => {
    fetchPlaylists();
  }, [fetchPlaylists]);

  useEffect(() => {
    const debounceTimeout = setTimeout(() => {
      if (searchQuery) {
        searchSongs();
      }
    }, 500);

    return () => clearTimeout(debounceTimeout);
  }, [searchQuery, searchSongs]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="text-xl">Loading playlists...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Your Playlists</h1>
        <div className="space-x-4">
          <Link to="/brands" className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
            Brand Profiles
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

      {/* Search Section */}
      <div className="mb-8">
        <div className="relative">
          <input
            type="text"
            placeholder="Search for songs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          {searchLoading && (
            <div className="absolute right-3 top-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500"></div>
            </div>
          )}
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-4 bg-white rounded-lg shadow-lg p-4">
            <h2 className="text-xl font-semibold mb-4">Search Results</h2>
            <div className="space-y-4">
              {searchResults.map(song => (
                <div key={song.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                  <div>
                    <p className="font-medium">{song.name}</p>
                    <p className="text-sm text-gray-600">
                      {song.artists.map(artist => artist.name).join(', ')}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedSong(song);
                      setShowPlaylistModal(true);
                    }}
                    className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    Add to Playlist
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Playlists Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {playlists.map(playlist => (
          <div key={playlist.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="aspect-w-1 aspect-h-1">
              {playlist.images && playlist.images[0] ? (
                <img 
                  src={playlist.images[0].url} 
                  alt={playlist.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                  <span className="text-gray-400">No Image</span>
                </div>
              )}
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-2 truncate" title={playlist.name}>
                {playlist.name}
              </h3>
              <p className="text-sm text-gray-600 mb-2">
                {playlist.tracks?.total || 0} tracks
              </p>
              <p className="text-xs text-gray-500">
                {playlist.is_owner ? 'Your playlist' : `By ${playlist.owner?.display_name || 'Unknown'}`}
              </p>
            </div>
          </div>
        ))}
      </div>

      {playlists.length === 0 && !error && (
        <div className="text-center py-8">
          <p className="text-gray-600">No playlists found</p>
        </div>
      )}

      {/* Playlist Selection Modal */}
      {showPlaylistModal && selectedSong && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-semibold mb-4">
              Add "{selectedSong.name}" to Playlist
            </h2>
            <div className="max-h-96 overflow-y-auto">
              {playlists.map(playlist => (
                <button
                  key={playlist.id}
                  onClick={() => addToPlaylist(playlist.id)}
                  disabled={addingToPlaylist}
                  className="w-full text-left p-3 hover:bg-gray-100 rounded mb-2 disabled:opacity-50"
                >
                  <p className="font-medium">{playlist.name}</p>
                  <p className="text-sm text-gray-600">
                    {playlist.tracks?.total || 0} tracks
                  </p>
                </button>
              ))}
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  setShowPlaylistModal(false);
                  setSelectedSong(null);
                }}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
                disabled={addingToPlaylist}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;