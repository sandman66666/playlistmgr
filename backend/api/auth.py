# backend/api/auth.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:3000/callback")
def get_auth_manager():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="playlist-modify-public playlist-modify-private user-read-private"
    )

@router.get("/login")
async def login():
    auth_manager = get_auth_manager()
    auth_url = auth_manager.get_authorize_url()
    return {"auth_url": auth_url}

@router.get("/callback")
async def callback(code: str):
    try:
        auth_manager = get_auth_manager()
        token_info = auth_manager.get_access_token(code)
        return token_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))