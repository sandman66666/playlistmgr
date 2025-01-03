from fastapi import APIRouter, HTTPException, Header, Depends, Request, Body
from typing import Optional, Dict, List
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import time
from datetime import datetime
from .auth import get_auth_manager, extract_token
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Constants for API handling
REQUEST_DELAY = 0.2  # 200ms delay between requests to prevent rate limiting
MAX_RETRIES = 3
BATCH_SIZE = 20  # Reduced batch size to prevent memory issues

# Request Models
class AddTracksRequest(BaseModel):
    uris: List[str]

async def get_spotify_client(request: Request) -> spotipy.Spotify:
    """
    Create a Spotify client with token refresh handling.
    """
    try:
        # Get authorization header
        authorization = request.headers.get('Authorization')
        if not authorization:
            raise HTTPException(status_code=401, detail="No authorization header")

        # Extract token from Bearer header
        try:
            token = extract_token(authorization)
            if not token:
                raise ValueError("Empty token")
            
            # Create Spotify client with token directly
            sp = spotipy.Spotify(auth=token)
            
            # Test the client
            try:
                sp.me()
                logger.info("Successfully created Spotify client")
                return sp
            except Exception as e:
                logger.error(f"Error validating token with Spotify API: {str(e)}")
                raise HTTPException(status_code=401, detail="Invalid token")
            
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Spotify client: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token. Please re-authenticate."
        )

async def fetch_all_playlists(sp: spotipy.Spotify, user_id: str) -> List[Dict]:
    """
    Fetch all playlists for a user with comprehensive error handling and retries.
    """
    try:
        all_playlists = {}  # Use dict to prevent duplicates
        start_time = datetime.now()
        retry_count = 0
        
        # First, get user's owned and followed playlists
        offset = 0
        while True:
            try:
                logger.info(f"Fetching user playlists batch, offset: {offset}")
                playlists = sp.current_user_playlists(limit=BATCH_SIZE, offset=offset)
                retry_count = 0  # Reset retry count on success
                
                if not playlists or 'items' not in playlists:
                    logger.error("Invalid response from Spotify API")
                    break
                    
                if playlists['items']:
                    for playlist in playlists['items']:
                        all_playlists[playlist['id']] = {
                            **playlist,
                            'is_owner': playlist['owner']['id'] == user_id,
                            'fetch_time': datetime.now().isoformat()
                        }
                    logger.info(f"Added {len(playlists['items'])} playlists")
                
                if not playlists.get('next'):
                    break
                    
                offset += BATCH_SIZE
                time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    logger.error(f"Max retries reached while fetching playlists: {str(e)}")
                    break
                logger.warning(f"Retry {retry_count} after error: {str(e)}")
                time.sleep(REQUEST_DELAY * 2)
                continue
        
        # Get collaborative playlists
        try:
            logger.info("Fetching collaborative playlists")
            collab_playlists = sp.current_user_playlists(limit=BATCH_SIZE)
            
            while collab_playlists:
                for playlist in collab_playlists['items']:
                    if playlist.get('collaborative') and playlist['id'] not in all_playlists:
                        all_playlists[playlist['id']] = {
                            **playlist,
                            'is_owner': playlist['owner']['id'] == user_id,
                            'fetch_time': datetime.now().isoformat()
                        }
                
                if not collab_playlists.get('next'):
                    break
                    
                collab_playlists = sp.next(collab_playlists)
                time.sleep(REQUEST_DELAY)
                
        except Exception as e:
            logger.warning(f"Error fetching collaborative playlists: {str(e)}")
        
        # Get saved albums as playlists
        try:
            logger.info("Fetching saved albums")
            offset = 0
            
            while True:
                results = sp.current_user_saved_albums(limit=BATCH_SIZE, offset=offset)
                if not results or 'items' not in results:
                    break
                    
                for item in results['items']:
                    if 'album' in item:
                        album = item['album']
                        playlist_id = f"album_{album['id']}"
                        if playlist_id not in all_playlists:
                            all_playlists[playlist_id] = {
                                'id': playlist_id,
                                'name': album['name'],
                                'owner': {'id': album['artists'][0]['id'], 'display_name': album['artists'][0]['name']},
                                'images': album.get('images', []),
                                'tracks': {'total': album.get('total_tracks', 0)},
                                'type': 'album',
                                'is_owner': False,
                                'fetch_time': datetime.now().isoformat()
                            }
                
                if not results.get('next'):
                    break
                    
                offset += BATCH_SIZE
                time.sleep(REQUEST_DELAY)
                
        except Exception as e:
            logger.warning(f"Error fetching saved albums: {str(e)}")
        
        # Convert dict back to list
        playlists_list = list(all_playlists.values())
        
        # Add statistics
        owned = sum(1 for p in playlists_list if p['is_owner'])
        followed = len(playlists_list) - owned
        
        end_time = datetime.now()
        fetch_duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Successfully fetched {len(playlists_list)} playlists in {fetch_duration:.2f} seconds")
        logger.info(f"Owned: {owned}, Followed: {followed}")
        
        return playlists_list
        
    except Exception as e:
        logger.error(f"Error fetching playlists: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlists: {str(e)}")

@router.get("/user")
async def get_user_playlists(
    request: Request,
    sp: spotipy.Spotify = Depends(get_spotify_client)
):
    """
    Get all playlists for the authenticated user.
    """
    try:
        logger.info("Getting user playlists")
        user = sp.me()
        if not user or 'id' not in user:
            raise HTTPException(status_code=401, detail="Could not get user information")
            
        user_id = user['id']
        logger.info(f"Fetching playlists for user: {user_id}")
        playlists = await fetch_all_playlists(sp, user_id)
        
        return {
            "playlists": playlists,
            "total": len(playlists),
            "owned": sum(1 for p in playlists if p['is_owner']),
            "followed": sum(1 for p in playlists if not p['is_owner']),
            "fetch_time": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in get_user_playlists: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{playlist_id}")
async def get_playlist(
    playlist_id: str,
    request: Request,
    sp: spotipy.Spotify = Depends(get_spotify_client)
):
    """
    Get details of a specific playlist.
    """
    try:
        # Handle album-type playlists
        if playlist_id.startswith('album_'):
            album_id = playlist_id.replace('album_', '')
            album = sp.album(album_id)
            return {
                'id': playlist_id,
                'name': album['name'],
                'owner': {'id': album['artists'][0]['id'], 'display_name': album['artists'][0]['name']},
                'images': album.get('images', []),
                'tracks': {'total': album.get('total_tracks', 0)},
                'type': 'album'
            }
        
        # Regular playlist
        playlist = sp.playlist(playlist_id)
        return playlist
    except Exception as e:
        logger.error(f"Error getting playlist {playlist_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{playlist_id}/tracks")
async def add_tracks_to_playlist(
    playlist_id: str,
    uris: Dict[str, List[str]],
    request: Request,
    sp: spotipy.Spotify = Depends(get_spotify_client)
):
    """
    Add tracks to a playlist.
    """
    try:
        logger.info(f"Adding tracks {uris} to playlist {playlist_id}")
        sp.playlist_add_items(playlist_id, uris["uris"])
        return {"message": "Tracks added successfully"}
    except Exception as e:
        logger.error(f"Error adding tracks to playlist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{playlist_id}/tracks")
async def remove_from_playlist(
    playlist_id: str,
    track_uri: str,
    request: Request,
    sp: spotipy.Spotify = Depends(get_spotify_client)
):
    """
    Remove a track from a playlist.
    """
    try:
        logger.info(f"Removing track {track_uri} from playlist {playlist_id}")
        sp.playlist_remove_all_occurrences_of_items(playlist_id, [track_uri])
        return {"message": "Track removed successfully"}
    except Exception as e:
        logger.error(f"Error removing track from playlist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{playlist_id}/tracks")
async def get_playlist_tracks(
    playlist_id: str,
    request: Request,
    sp: spotipy.Spotify = Depends(get_spotify_client)
):
    """
    Get all tracks in a playlist with proper pagination and error handling.
    """
    try:
        logger.info(f"Getting tracks for playlist {playlist_id}")
        all_tracks = []
        offset = 0
        retry_count = 0
        
        # Handle album-type playlists
        if playlist_id.startswith('album_'):
            album_id = playlist_id.replace('album_', '')
            album_tracks = sp.album_tracks(album_id)
            return {
                "tracks": [{'track': track, 'added_at': None} for track in album_tracks['items']],
                "total": len(album_tracks['items']),
                "fetch_time": datetime.now().isoformat()
            }
        
        # Regular playlist
        while True:
            try:
                results = sp.playlist_items(
                    playlist_id,
                    offset=offset,
                    limit=BATCH_SIZE,
                    additional_types=['track']
                )
                retry_count = 0
                
                if results['items']:
                    tracks = [{
                        'track': item['track'],
                        'added_at': item['added_at']
                    } for item in results['items'] if item['track']]
                    all_tracks.extend(tracks)
                    logger.info(f"Fetched {len(tracks)} tracks, total: {len(all_tracks)}")
                
                if not results['next']:
                    break
                    
                offset += BATCH_SIZE
                time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                retry_count += 1
                if retry_count >= MAX_RETRIES:
                    logger.error(f"Max retries reached while fetching tracks: {str(e)}")
                    break
                logger.warning(f"Retry {retry_count} after error: {str(e)}")
                time.sleep(REQUEST_DELAY * 2)
                continue
        
        return {
            "tracks": all_tracks,
            "total": len(all_tracks),
            "fetch_time": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting playlist tracks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{playlist_id}/tracks")
async def update_playlist_tracks(
    playlist_id: str,
    track_uris: List[str],
    request: Request,
    sp: spotipy.Spotify = Depends(get_spotify_client)
):
    """
    Replace all tracks in a playlist with proper chunking and error handling.
    """
    try:
        logger.info(f"Updating tracks for playlist {playlist_id}")
        
        # Split track_uris into chunks of 100 (Spotify API limit)
        chunk_size = 100
        for i in range(0, len(track_uris), chunk_size):
            chunk = track_uris[i:i + chunk_size]
            if i == 0:
                # First chunk replaces all tracks
                sp.playlist_replace_items(playlist_id, chunk)
            else:
                # Subsequent chunks are added
                sp.playlist_add_items(playlist_id, chunk)
            time.sleep(REQUEST_DELAY)
            
        return {"message": "Playlist tracks updated successfully"}
    except Exception as e:
        logger.error(f"Error updating playlist tracks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))