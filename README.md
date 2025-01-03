# Spotify Playlist Manager

A web application for managing Spotify playlists with advanced features and a modern user interface.

## Features

- Spotify Authentication
- Playlist Management
- Brand-based Playlist Creation
- Modern UI with React
- FastAPI Backend

## Tech Stack

### Frontend
- React
- React Router
- Tailwind CSS
- Modern JavaScript (ES6+)

### Backend
- FastAPI
- Python 3.11
- Spotify Web API
- PostgreSQL

## Development

### Prerequisites
- Node.js (v20+)
- Python 3.11+
- Spotify Developer Account

### Setup

1. Clone the repository:
```bash
git clone https://github.com/sandman66666/playlistmgr.git
cd playlistmgr
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the backend directory with your Spotify API credentials:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=your_redirect_uri
```

### Running the Application

1. Start the backend server:
```bash
cd backend
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

## Deployment

The application is deployed on Heroku with automatic deployments from the main branch.

## License

This project is licensed under the MIT License - see the LICENSE file for details.