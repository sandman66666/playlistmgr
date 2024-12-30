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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Get the path to the brand_profiles directory
BRAND_PROFILES_DIR = Path(__file__).parent.parent / "data" / "brand_profiles"

@router.post("/suggest-music")
async def suggest_music(brand_profile: Dict):
    """Get music suggestions from Anthropic based on brand profile"""
    try:
        logger.info("Initializing Anthropic client")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        client = Anthropic(
            api_key=api_key.strip()  # Ensure no whitespace
        )
        logger.info("Anthropic client initialized successfully")
        
        # Construct the prompt with the required format
        prompt = f"""\n\nHuman: You are a music curator with deep knowledge of music and brand aesthetics. Analyze this brand profile and suggest 10 songs that perfectly embody the brand's aesthetic, values, and cultural positioning.

        Brand Profile:
        Name: {brand_profile.get('brand')}
        Core Identity: {brand_profile.get('brand_essence', {}).get('core_identity', '')}
        Aesthetic: {brand_profile.get('aesthetic_pillars', {}).get('visual_language', [])}
        Cultural Values: {brand_profile.get('cultural_positioning', {}).get('core_values', [])}

        For each song, explain how it specifically aligns with the brand's values and aesthetic. 
        Consider factors like:
        - Production quality and sound matching the brand's sophistication level
        - Lyrical themes aligning with brand values
        - Artist image and cultural positioning
        - Emotional resonance with the target audience
        - Cultural relevance and zeitgeist alignment

        Format each suggestion as:
        Song: [title]
        Artist: [name]
        Why it fits: [detailed explanation connecting to brand attributes]

        \n\nAssistant: I'll help you find songs that perfectly match GUCCI's brand identity. Here are 10 carefully curated suggestions:"""

        logger.info("Creating completion with Anthropic")
        response = client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=1500,
            temperature=0.7,
            stop_sequences=["\n\nHuman:"]
        )
        logger.info("Completion created successfully")

        # Parse the response into structured suggestions
        try:
            logger.info("Parsing Anthropic response")
            response_text = response.completion
            # Split response into sections for each song
            song_sections = response_text.split('\n\n')
            suggestions = []
            
            for section in song_sections:
                if 'Song:' in section and 'Artist:' in section:
                    lines = section.split('\n')
                    suggestion = {
                        "track": lines[0].replace('Song:', '').strip(),
                        "artist": lines[1].replace('Artist:', '').strip(),
                        "reason": ' '.join(lines[2:]).replace('Why it fits:', '').strip()
                    }
                    suggestions.append(suggestion)
            
            logger.info(f"Successfully parsed {len(suggestions)} suggestions")
            return {"suggestions": suggestions}

        except Exception as parse_error:
            logger.error(f"Error parsing response: {parse_error}")
            logger.error(f"Raw response: {response.completion}")
            return {"error": "Failed to parse suggestions", "raw_response": response_text}

    except Exception as e:
        logger.error(f"Error in suggest_music: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"Error getting music suggestions: {str(e)}")

@router.post("/create-playlist")
async def create_brand_playlist(token: str, brand_id: str, suggestions: List[Dict]):
    """Create a Spotify playlist from the suggestions"""
    try:
        # Get brand profile
        brand_profile = await get_brand_profile(brand_id)
        
        # Initialize Spotify client
        sp = spotipy.Spotify(auth=token)
        
        # Create playlist
        user_id = sp.current_user()["id"]
        playlist_name = f"{brand_profile['brand']} Brand Playlist"
        description = f"A curated playlist capturing {brand_profile['brand']}'s aesthetic and values"
        
        playlist = sp.user_playlist_create(
            user_id,
            playlist_name,
            public=False,
            description=description
        )
        
        # Search and add tracks
        track_uris = []
        not_found = []
        
        for suggestion in suggestions:
            query = f"track:{suggestion['track']} artist:{suggestion['artist']}"
            results = sp.search(q=query, type='track', limit=1)
            
            if results['tracks']['items']:
                track_uris.append(results['tracks']['items'][0]['uri'])
            else:
                not_found.append(f"{suggestion['track']} by {suggestion['artist']}")
        
        # Add found tracks to playlist
        if track_uris:
            sp.playlist_add_items(playlist['id'], track_uris)
        
        return {
            "playlist_id": playlist['id'],
            "tracks_added": len(track_uris),
            "tracks_not_found": not_found,
            "playlist_url": f"https://open.spotify.com/playlist/{playlist['id']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating playlist: {str(e)}")

@router.get("/brands")
async def get_all_brands():
    """Get a list of all available brand profiles"""
    try:
        # Ensure the directory exists
        if not BRAND_PROFILES_DIR.exists():
            return {"brands": []}
        
        # Get all JSON files in the brand_profiles directory
        brand_files = list(BRAND_PROFILES_DIR.glob("*.json"))
        brands = []
        
        for file in brand_files:
            with open(file, 'r') as f:
                brand_data = json.load(f)
                brands.append({
                    "id": file.stem,  # filename without extension
                    "name": brand_data.get("brand", file.stem),
                    "description": brand_data.get("brand_essence", {}).get("core_identity", "")
                })
        
        return {"brands": brands}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading brand profiles: {str(e)}")

@router.get("/brands/{brand_id}")
async def get_brand_profile(brand_id: str):
    """Get a specific brand profile by ID"""
    try:
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Brand profile not found: {brand_id}")
        
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading brand profile: {str(e)}")

@router.post("/brands")
async def create_brand_profile(brand_data: Dict):
    """Create a new brand profile"""
    try:
        if "brand" not in brand_data:
            raise HTTPException(status_code=400, detail="Brand name is required")
        
        # Create directory if it doesn't exist
        BRAND_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate a filename-safe brand ID
        brand_id = brand_data["brand"].lower().replace(" ", "_")
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        
        # Don't overwrite existing profiles
        if file_path.exists():
            raise HTTPException(status_code=400, detail=f"Brand profile already exists: {brand_id}")
        
        with open(file_path, 'w') as f:
            json.dump(brand_data, f, indent=2)
        
        return {"message": "Brand profile created successfully", "brand_id": brand_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating brand profile: {str(e)}")

@router.put("/brands/{brand_id}")
async def update_brand_profile(brand_id: str, brand_data: Dict):
    """Update an existing brand profile"""
    try:
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Brand profile not found: {brand_id}")
        
        with open(file_path, 'w') as f:
            json.dump(brand_data, f, indent=2)
        
        return {"message": "Brand profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating brand profile: {str(e)}")

@router.delete("/brands/{brand_id}")
async def delete_brand_profile(brand_id: str):
    """Delete a brand profile"""
    try:
        file_path = BRAND_PROFILES_DIR / f"{brand_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Brand profile not found: {brand_id}")
        
        os.remove(file_path)
        return {"message": "Brand profile deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting brand profile: {str(e)}")