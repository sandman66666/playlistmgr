const isProd = process.env.NODE_ENV === 'production';
const prodDomain = 'https://playlist-mgr-39a919ee8105-1641bf424db9.herokuapp.com';
const devDomain = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const config = {
  apiBaseUrl: isProd ? prodDomain : devDomain,
  // Updated to use hash-based routing
  spotifyCallbackUrl: isProd ? `${prodDomain}/#/auth` : `${devDomain}/#/auth`,
  endpoints: {
    auth: {
      login: '/auth/login',
      callback: '/auth/callback',
      refresh: '/auth/refresh',
      validate: '/auth/validate'
    },
    playlist: {
      user: '/playlist/user',
      details: (id) => `/playlist/${id}`,
      tracks: (id) => `/playlist/${id}/tracks`,
      addTracks: (id) => `/playlist/${id}/tracks`,
      removeTracks: (id) => `/playlist/${id}/tracks`
    },
    brands: {
      list: '/brands',
      details: (id) => `/brands/${id}`,
      suggestMusic: '/brands/suggest-music',
      createPlaylist: '/brands/create-playlist'
    }
  }
};

export default config;