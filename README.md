# Spotify Playlist Manager

A web application for managing Spotify playlists, built with React and FastAPI.

## Features

- Search for songs on Spotify
- View your playlists
- Add songs to playlists
- OAuth2 authentication with Spotify

## Setup

### Backend

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Create a `.env` file in the backend directory:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:3000/callback
```

3. Run the backend server:
```bash
uvicorn main:app --reload --port 3001
```

### Frontend

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Run the frontend development server:
```bash
npm start
```

## Environment Setup

1. Create a Spotify Developer account and register your application
2. Add `http://localhost:3000/callback` to your Spotify App's Redirect URIs
3. Copy your Client ID and Client Secret to the backend `.env` file

## Development

- Backend API runs on `http://localhost:3001`
- Frontend development server runs on `http://localhost:3000`

## Deployment

### GitHub Setup

1. If you haven't already, clone the repository:
```bash
git clone https://github.com/sandman66666/playlistmgr.git
cd playlistmgr
```

2. After making changes, commit them:
```bash
git add .
git commit -m "Your commit message"
```

3. Push to GitHub:
```bash
git push origin main
```

### Heroku Configuration

1. Make the setup script executable:
```bash
chmod +x setup.sh
```

2. Run the setup script to configure buildpacks and environment variables:
```bash
./setup.sh
```

3. Update your Spotify App's settings:
   - Add `https://playlist-mgr-39a919ee8105.herokuapp.com/callback` to your Spotify App's Redirect URIs
   - Update the SPOTIFY_REDIRECT_URI in your Heroku config:
     ```bash
     heroku config:set SPOTIFY_REDIRECT_URI=https://playlist-mgr-39a919ee8105.herokuapp.com/callback
     ```

4. Heroku will automatically deploy when changes are pushed to the GitHub repository (github.com/sandman66666/playlistmgr)

### Troubleshooting Deployment

If you encounter issues:
1. Check the Heroku logs:
```bash
heroku logs --tail
```

2. Ensure buildpacks are correctly set:
```bash
heroku buildpacks
```

3. Verify environment variables:
```bash
heroku config
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.