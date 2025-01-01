const config = {
  apiBaseUrl: 'http://localhost:3001',
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