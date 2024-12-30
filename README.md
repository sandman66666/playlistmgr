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

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.