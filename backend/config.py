import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Spotify API Configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Define all required scopes
SPOTIFY_SCOPES = [
    'playlist-read-private',
    'playlist-read-collaborative',
    'playlist-modify-public',
    'playlist-modify-private',
    'user-read-private',
    'user-read-email',
    'user-follow-read',
    'user-library-read',
    'user-library-modify',
    'user-follow-modify',
    'user-read-playback-state',
    'user-modify-playback-state',
    'streaming',
    'user-top-read'
]

# API Configuration
API_PREFIX = "/api"
DEBUG = True

# Cache Configuration
CACHE_PATH = None  # Disable file caching to prevent token persistence issues
CACHE_HANDLER = None  # Use in-memory caching

# Request Configuration
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 0.1  # seconds

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create necessary directories
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        'logs',
        'cache',
        'data'
    ]
    base_path = Path(__file__).parent
    for directory in directories:
        path = base_path / directory
        path.mkdir(exist_ok=True)

# Initialize directories
ensure_directories()