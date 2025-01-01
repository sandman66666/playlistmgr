from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import logging
import json
import os
import secrets
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

# Store states in memory (in production, use Redis or similar)
active_states = {}

def generate_state():
    """Generate a secure random state string"""
    state = secrets.token_urlsafe(32)
    active_states[state] = datetime.now()
    # Clean up old states
    for s in list(active_states.keys()):
        if (datetime.now() - active_states[s]).total_seconds() > 600:  # 10 minutes
            del active_states[s]
    return state

def validate_state(state: str) -> bool:
    """Validate the state parameter"""
    if not state or state not in active_states:
        return False
    # Remove used state
    del active_states[state]
    return True

def get_auth_manager():
    """Create SpotifyOAuth manager with configured scopes"""
    scopes = [
        'playlist-read-private',
        'playlist-read-collaborative',
        'playlist-modify-public',
        'playlist-modify-private',
        'user-library-read',
        'user-read-private',
        'user-read-email'
    ]
    
    try:
        auth_manager = SpotifyOAuth(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
            scope=' '.join(scopes),
            open_browser=False,
            cache_handler=None  # Disable cache to prevent token persistence
        )
        logger.info("Created SpotifyOAuth manager with configured scopes")
        return auth_manager
    except Exception as e:
        logger.error(f"Error creating SpotifyOAuth manager: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize authentication")

def extract_token(authorization: str) -> str:
    """Extract token from Authorization header"""
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization.replace('Bearer ', '').strip()

def validate_spotify_token(token: str) -> bool:
    """Validate token by making a test request to Spotify API"""
    try:
        sp = spotipy.Spotify(auth=token)
        sp.me()  # Test request
        return True
    except:
        return False

async def validate_token_string(token: str) -> bool:
    """Helper function to validate just the token string"""
    try:
        return validate_spotify_token(token)
    except Exception as e:
        logger.error(f"Error validating token string: {str(e)}")
        return False

@router.get("/login")
async def login():
    """Generate login URL for Spotify OAuth"""
    try:
        auth_manager = get_auth_manager()
        state = generate_state()
        auth_url = auth_manager.get_authorize_url(state=state)
        logger.info("Generated auth URL for login with comprehensive scopes")
        return {"auth_url": auth_url, "state": state}
    except Exception as e:
        logger.error(f"Error generating login URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate login URL")

@router.get("/callback")
async def callback(code: str, state: Optional[str] = None):
    """Handle OAuth callback from Spotify"""
    try:
        if not state or not validate_state(state):
            raise ValueError("Invalid state parameter")
            
        auth_manager = get_auth_manager()
        token_info = auth_manager.get_access_token(code, check_cache=False)
        if not token_info:
            raise ValueError("Failed to get token info")
            
        # Add expiration timestamp
        token_info['expires_at'] = int(datetime.now().timestamp() + token_info['expires_in'])
        
        # Validate token works
        if not validate_spotify_token(token_info['access_token']):
            raise ValueError("Invalid token received from Spotify")
        
        logger.info("Successfully obtained and validated token with all required scopes")
        return {"token_info": token_info}
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.post("/validate")
async def validate_token(request: Request):
    """Validate access token and refresh if needed"""
    try:
        # Get token from Authorization header
        authorization = request.headers.get('Authorization')
        if not authorization:
            return JSONResponse(status_code=401, content={"valid": False, "error": "No authorization header"})
            
        token = extract_token(authorization)
        if not token:
            return JSONResponse(status_code=401, content={"valid": False, "error": "Invalid token format"})
        
        # First try to validate the token directly
        if validate_spotify_token(token):
            return {"valid": True}
            
        # If direct validation fails, try to refresh using the token info from request body
        try:
            body = await request.json()
            token_info = body.get('token_info', {})
            if not token_info or not token_info.get('refresh_token'):
                return {"valid": False, "error": "No refresh token available"}
                
            auth_manager = get_auth_manager()
            new_token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
            
            if new_token_info and validate_spotify_token(new_token_info['access_token']):
                # Add expiration timestamp
                new_token_info['expires_at'] = int(datetime.now().timestamp() + new_token_info['expires_in'])
                return {"valid": True, "token_info": new_token_info}
        except:
            pass
            
        return {"valid": False}
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}")
        return {"valid": False, "error": str(e)}

@router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh access token"""
    try:
        # Get current token from Authorization header
        authorization = request.headers.get('Authorization')
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization header")
            
        current_token = extract_token(authorization)
        if not current_token:
            raise HTTPException(status_code=401, detail="Invalid token format")
            
        # Get refresh token from request body
        body = await request.json()
        refresh_token = body.get('refresh_token')
        if not refresh_token:
            raise HTTPException(status_code=400, detail="No refresh token provided")
            
        auth_manager = get_auth_manager()
        
        # Try to refresh the token
        try:
            new_token_info = auth_manager.refresh_access_token(refresh_token)
            if not new_token_info or not new_token_info.get('access_token'):
                raise ValueError("Failed to refresh token")
                
            # Validate new token works
            if not validate_spotify_token(new_token_info['access_token']):
                raise ValueError("Invalid token received from refresh")
                
            # Add expiration timestamp
            new_token_info['expires_at'] = int(datetime.now().timestamp() + new_token_info['expires_in'])
            
            return new_token_info
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise HTTPException(status_code=401, detail="Failed to refresh token")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))