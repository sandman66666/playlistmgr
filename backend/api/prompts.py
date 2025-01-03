def get_music_suggestion_prompt(brand_profile):
    return f"""I need song suggestions that match this brand profile and identity:

Brand: {brand_profile.get('brand')}
Core Identity: {brand_profile.get('brand_essence', {}).get('core_identity', '')}
Visual Language: {', '.join(brand_profile.get('aesthetic_pillars', {}).get('visual_language', []))}
Brand Voice: {brand_profile.get('brand_essence', {}).get('brand_voice', '')}

Please suggest 10 songs that perfectly match this brand's identity. For each song suggestion, provide:
1. The exact song title
2. The exact artist name
3. A brief explanation of why it fits the brand (max 2 sentences)

Format each suggestion exactly like this example:
SONG: Shape of You
ARTIST: Ed Sheeran
WHY: The upbeat pop sound and modern production align with the brand's contemporary identity. The lyrics about human connection match the brand's emphasis on emotional engagement.

Please provide exactly 10 suggestions in this format."""