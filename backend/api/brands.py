from fastapi import APIRouter, HTTPException
from typing import Dict, List
import json
import os
from pathlib import Path
import logging
import random

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# For Anthropic
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

BRAND_PROFILES_DIR = Path(__file__).parent.parent / "data" / "brand_profiles"

@router.get("")
async def get_all_brands():
    try:
        if not BRAND_PROFILES_DIR.exists():
            BRAND_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
            return {"brands": []}
        
        brand_files = list(BRAND_PROFILES_DIR.glob("*.json"))
        brands = []
        
        for file in brand_files:
            with open(file, 'r') as f:
                brand_data = json.load(f)
                brands.append({
                    "id": file.stem,
                    "name": brand_data.get("brand", file.stem),
                    "description": brand_data.get("brand_essence", {}).get("core_identity", "")
                })
        
        return {"brands": brands}
    except Exception as e:
        logger.error(f"Error getting brands: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{brand_id}")
async def get_brand_profile(brand_id: str):
    try:
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Brand not found: {brand_id}")
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error getting brand {brand_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-music")
async def suggest_music(brand_profile: Dict):
    try:
        logger.info("Starting suggest-music endpoint")
        logger.info(f"Brand Profile: {brand_profile}")
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found")
            raise ValueError("ANTHROPIC_API_KEY not set")
            
        logger.info("Got API key, initializing Anthropic client")
        client = Anthropic(api_key=api_key.strip())

        brand_name = brand_profile.get("brand", "Unknown Brand")
        core_identity = brand_profile.get("brand_essence", {}).get("core_identity", "")

        user_prompt = f"""
You are a music curator. Suggest 10 songs that match this brand:
Brand: {brand_name}
Identity: {core_identity}

Format each suggestion as:
Song: [title]
Artist: [artist name]
Why it fits: [one sentence reason]
"""

        prompt = f"{HUMAN_PROMPT}{user_prompt}{AI_PROMPT}"
        logger.info("Sending request to Anthropic using completions.create()")
        response = client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=1500,
            stop_sequences=[HUMAN_PROMPT]
        )

        text_response = response.completion
        logger.info(f"Anthropic response:\n{text_response}")

        suggestions = []
        song_sections = text_response.split("\n\n")
        for section in song_sections:
            if "Song:" in section and "Artist:" in section:
                lines = section.strip().split("\n")
                track_line = lines[0].replace("Song:", "").strip()
                artist_line = lines[1].replace("Artist:", "").strip()
                reason_line = ""
                if len(lines) > 2:
                    reason_line = " ".join(lines[2:]).replace("Why it fits:", "").strip()

                suggestions.append({
                    "track": track_line,
                    "artist": artist_line,
                    "reason": reason_line
                })

        return {"suggestions": suggestions}

    except Exception as e:
        logger.error(f"Error in suggest-music: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

def find_existing_playlist(sp: spotipy.Spotify, playlist_name: str) -> Dict:
    """
    Helper function to find an existing playlist by name.
    Returns the playlist data if found, None otherwise.
    """
    try:
        logger.info(f"Searching for existing playlist: {playlist_name}")
        offset = 0
        limit = 50
        
        while True:
            playlists = sp.current_user_playlists(limit=limit, offset=offset)
            
            if not playlists['items']:
                logger.info("No more playlists to check")
                break
                
            for playlist in playlists['items']:
                # Case-insensitive comparison
                if playlist['name'].lower() == playlist_name.lower():
                    logger.info(f"Found existing playlist: {playlist['id']}")
                    return playlist
            
            if not playlists['next']:
                break
                
            offset += limit
            
        logger.info("No existing playlist found")
        return None
        
    except Exception as e:
        logger.error(f"Error finding existing playlist: {str(e)}")
        return None

@router.post("/create-playlist")
async def create_brand_playlist(payload: Dict):
    """
    If a playlist exists, replace half of its songs with new ones while maintaining the same total count.
    If no playlist exists, create a new one with all suggested songs.
    """
    try:
        token = payload.get("token")
        brand_id = payload.get("brand_id")
        suggestions = payload.get("suggestions")

        if not all([token, brand_id, suggestions]):
            raise HTTPException(status_code=422, detail="Missing required fields")

        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Brand not found: {brand_id}")

        with open(file_path, 'r') as f:
            brand_profile = json.load(f)

        # Create Spotify client with access token
        sp = spotipy.Spotify(auth=token)
        
        try:
            user_id = sp.current_user()["id"]
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        playlist_name = f"{brand_profile['brand']} Brand Playlist"
        description = f"A curated playlist for {brand_profile['brand']}"

        # Search for existing playlist
        existing_playlist = find_existing_playlist(sp, playlist_name)

        # Search for new tracks
        new_track_uris = []
        not_found = []
        for item in suggestions:
            try:
                query = f"track:{item['track']} artist:{item['artist']}"
                results = sp.search(q=query, type='track', limit=1)
                if results['tracks']['items']:
                    new_track_uris.append(results['tracks']['items'][0]['uri'])
                else:
                    not_found.append(f"{item['track']} by {item['artist']}")
            except Exception as e:
                logger.error(f"Error searching for track {item['track']}: {str(e)}")
                continue

        if existing_playlist:
            playlist_id = existing_playlist['id']
            logger.info(f"Updating existing playlist: {playlist_id}")
            
            # Get current tracks
            current_tracks = []
            results = sp.playlist_items(playlist_id)
            while results:
                current_tracks.extend([item['track']['uri'] for item in results['items'] if item['track']])
                if results['next']:
                    results = sp.next(results)
                else:
                    break

            total_tracks = len(current_tracks)
            if total_tracks > 0:
                # Keep half of the existing tracks
                tracks_to_keep = total_tracks // 2
                kept_tracks = random.sample(current_tracks, min(tracks_to_keep, len(current_tracks)))
                
                # Remove all current tracks
                logger.info("Removing all tracks from playlist")
                sp.playlist_replace_items(playlist_id, [])
                
                # Add back kept tracks
                logger.info(f"Adding back {len(kept_tracks)} kept tracks")
                if kept_tracks:
                    sp.playlist_add_items(playlist_id, kept_tracks)
                
                # Add new tracks to match original count
                remaining_slots = total_tracks - len(kept_tracks)
                new_tracks_to_add = new_track_uris[:remaining_slots]
                if new_tracks_to_add:
                    logger.info(f"Adding {len(new_tracks_to_add)} new tracks")
                    sp.playlist_add_items(playlist_id, new_tracks_to_add)
            else:
                # If playlist is empty, just add all new tracks
                if new_track_uris:
                    sp.playlist_add_items(playlist_id, new_track_uris)
            
        else:
            logger.info("Creating new playlist")
            try:
                new_playlist = sp.user_playlist_create(
                    user=user_id,
                    name=playlist_name,
                    public=False,
                    description=description
                )
                playlist_id = new_playlist['id']
                if new_track_uris:
                    sp.playlist_add_items(playlist_id, new_track_uris)
            except Exception as e:
                logger.error(f"Error creating playlist: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to create playlist")

        return {
            "playlist_id": playlist_id,
            "tracks_added": len(new_track_uris),
            "tracks_not_found": not_found,
            "playlist_url": f"https://open.spotify.com/playlist/{playlist_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating or updating playlist: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def create_brand_profile(brand_data: Dict):
    try:
        if "brand" not in brand_data:
            raise HTTPException(status_code=400, detail="Brand name required")
        
        BRAND_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        brand_id = brand_data["brand"].lower().replace(" ", "_")
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"

        if file_path.exists():
            raise HTTPException(status_code=400, detail=f"Brand exists: {brand_id}")

        with open(file_path, 'w') as f:
            json.dump(brand_data, f, indent=2)

        return {"message": "Brand profile created", "brand_id": brand_id}
    except Exception as e:
        logger.error(f"Error creating brand: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{brand_id}")
async def update_brand_profile(brand_id: str, brand_data: Dict):
    try:
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Brand not found: {brand_id}")

        with open(file_path, 'w') as f:
            json.dump(brand_data, f, indent=2)

        return {"message": "Brand profile updated"}
    except Exception as e:
        logger.error(f"Error updating brand {brand_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{brand_id}")
async def delete_brand_profile(brand_id: str):
    try:
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Brand not found: {brand_id}")

        os.remove(file_path)
        return {"message": "Brand profile deleted"}
    except Exception as e:
        logger.error(f"Error deleting brand {brand_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))