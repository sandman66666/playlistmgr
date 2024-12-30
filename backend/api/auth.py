from fastapi import APIRouter, HTTPException
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Debug prints for environment variables
print("Environment variables loaded:")
print(f"Client ID: {'*' * len(os.getenv('SPOTIFY_CLIENT_ID', ''))}") # Masked for security
print(f"Client Secret: {'*' * len(os.getenv('SPOTIFY_CLIENT_SECRET', ''))}")  # Masked for security
print(f"Redirect URI: {os.getenv('SPOTIFY_REDIRECT_URI', 'Not set')}")

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:3000/callback")

if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI]):
    print("WARNING: Missing required Spotify credentials!")

def get_auth_manager():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="playlist-modify-public playlist-modify-private user-read-private"
    )

@router.get("/login")
async def login():
    try:
        print("Login endpoint called")
        auth_manager = get_auth_manager()
        auth_url = auth_manager.get_authorize_url()
        print(f"Generated auth URL: {auth_url}")
        
        return JSONResponse(
            content={"auth_url": auth_url},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    except Exception as e:
        print(f"Error in login route: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def callback(code: str):
    try:
        print(f"Callback received with code: {code[:10]}...")  # Print first 10 chars of code
        auth_manager = get_auth_manager()
        token_info = auth_manager.get_access_token(code)
        print("Token successfully obtained")
        
        # Return token info with CORS headers
        return JSONResponse(
            content=token_info,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    except Exception as e:
        print(f"Error in callback route: {str(e)}")
        error_msg = str(e)
        print(f"Full error details: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)