from fastapi import APIRouter, HTTPException
from typing import Dict, List
import json
import os
from pathlib import Path
from anthropic import Anthropic
import spotipy
from dotenv import load_dotenv
import logging

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
        
        prompt = f"""You are a music curator. Suggest 10 songs that match this brand:
        Brand: {brand_profile.get('brand')}
        Identity: {brand_profile.get('brand_essence', {}).get('core_identity', '')}
        
        Format as:
        Song: [title]
        Artist: [name]
        Why it fits: [explanation]"""
        
        logger.info("Sending request to Anthropic")
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        logger.info("Got response from Anthropic")
        logger.info(f"Response: {response.content}")
        
        suggestions = []
        song_sections = response.content.split('\n\n')
        
        for section in song_sections:
            if 'Song:' in section and 'Artist:' in section:
                lines = section.split('\n')
                suggestions.append({
                    "track": lines[0].replace('Song:', '').strip(),
                    "artist": lines[1].replace('Artist:', '').strip(),
                    "reason": ' '.join(lines[2:]).replace('Why it fits:', '').strip()
                })

        return {"suggestions": suggestions}

    except Exception as e:
        logger.error(f"Error in suggest-music: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-playlist")
async def create_brand_playlist(token: str, brand_id: str, suggestions: List[Dict]):
    try:
        brand_profile = await get_brand_profile(brand_id)
        sp = spotipy.Spotify(auth=token)
        
        user_id = sp.current_user()["id"]
        playlist_name = f"{brand_profile['brand']} Brand Playlist"
        description = f"A curated playlist for {brand_profile['brand']}"
        
        playlist = sp.user_playlist_create(
            user_id,
            playlist_name,
            public=False,
            description=description
        )
        
        track_uris = []
        not_found = []
        
        for suggestion in suggestions:
            query = f"track:{suggestion['track']} artist:{suggestion['artist']}"
            results = sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track_uris.append(results['tracks']['items'][0]['uri'])
            else:
                not_found.append(f"{suggestion['track']} by {suggestion['artist']}")
        
        if track_uris:
            sp.playlist_add_items(playlist['id'], track_uris)
        
        return {
            "playlist_id": playlist['id'],
            "tracks_added": len(track_uris),
            "tracks_not_found": not_found,
            "playlist_url": f"https://open.spotify.com/playlist/{playlist['id']}"
        }
        
    except Exception as e:
        logger.error(f"Error creating playlist: {str(e)}")
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
        logger.error(f"Error creating brand: {str(e)}")
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
        logger.error(f"Error deleting brand {brand_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))