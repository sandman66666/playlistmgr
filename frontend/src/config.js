const isProd = process.env.NODE_ENV === 'production';
const prodDomain = 'https://playlist-mgr-39a919ee8105.herokuapp.com';
const devDomain = 'http://localhost:3001';

const config = {
  apiBaseUrl: isProd ? prodDomain : devDomain,
  endpoints: {
    auth: {
      login: '/auth/login',
      callback: '/auth/callback',
      refresh: '/auth/refresh',
      validate: '/auth/validate'
    },
    playlist: {
      user: '/api/playlist/user',
      details: (id) => `/api/playlist/${id}`,
      tracks: (id) => `/api/playlist/${id}/tracks`,
      addTracks: (id) => `/api/playlist/${id}/tracks`,
      removeTracks: (id) => `/api/playlist/${id}/tracks`
    },
    brands: {
      list: '/api/brands',
      details: (id) => `/api/brands/${id}`,
      suggestMusic: '/api/brands/suggest-music',
      createPlaylist: '/api/brands/create-playlist'
    }
  }
};

export default config;