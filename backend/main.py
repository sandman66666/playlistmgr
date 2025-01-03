# backend/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import logging
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Get the absolute path to the static directory
BASE_DIR = Path(__file__).parent
STATIC_DIR = os.getenv('STATIC_DIR', str(BASE_DIR / "static"))
logger.info(f"Base directory: {BASE_DIR}")
logger.info(f"Static directory path: {STATIC_DIR}")

# Ensure static directory exists
static_path = Path(STATIC_DIR)
static_path.mkdir(parents=True, exist_ok=True)

# Copy frontend build files to static directory if they exist
frontend_build = BASE_DIR.parent / "frontend" / "build"
if frontend_build.exists():
    logger.info(f"Copying frontend build files from {frontend_build} to {static_path}")
    for item in frontend_build.glob('*'):
        dest_dir = static_path / item.name
        if item.is_file():
            shutil.copy2(str(item), str(static_path))
        elif item.is_dir():
            if dest_dir.exists():
                try:
                    shutil.rmtree(str(dest_dir))
                except FileNotFoundError:
                    logger.warning(f"Directory not found while trying to remove: {dest_dir}")
                except Exception as e:
                    logger.error(f"Error removing directory {dest_dir}: {str(e)}")
            try:
                shutil.copytree(str(item), str(dest_dir))
            except Exception as e:
                logger.error(f"Error copying directory {item} to {dest_dir}: {str(e)}")

# Configure CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://playlist-mgr-39a919ee8105.herokuapp.com",
    "https://playlist-mgr-39a919ee8105-1641bf424db9.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers with error handling
try:
    from api import auth, playlist, search, brands
    
    # Include routers with basic error handling
    for router_info in [
        (auth, "/auth", "auth"),
        (playlist, "/playlist", "playlist"),
        (search, "/search", "search"),
        (brands, "/brands", "brands")
    ]:
        try:
            router, prefix, tag = router_info
            app.include_router(router, prefix=prefix, tags=[tag])
            logger.info(f"Successfully mounted {tag} router at {prefix}")
        except Exception as e:
            logger.warning(f"Failed to mount {tag} router: {str(e)}")
            
except ImportError as e:
    logger.warning(f"Some API modules could not be imported: {str(e)}")
    logger.info("Continuing with limited functionality")

# Function to check if path is an API route
def is_api_route(path: str) -> bool:
    api_prefixes = ("/api/", "/auth/", "/playlist/", "/search/", "/brands/", "/health", "/debug-static")
    return path.startswith(api_prefixes)

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    static_exists = static_path.exists()
    static_files = []
    try:
        static_files = [f.name for f in static_path.iterdir()] if static_exists else []
    except Exception as e:
        logger.error(f"Error reading static directory: {e}")
    
    index_exists = (static_path / "index.html").exists()
    
    return {
        "status": "healthy" if index_exists else "degraded",
        "static_dir": str(STATIC_DIR),
        "static_exists": static_exists,
        "static_files": static_files,
        "index_exists": index_exists,
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Handle Spotify callback at root level
@app.get("/callback")
async def spotify_callback(code: str, state: str = None):
    """Redirect Spotify callback to auth router"""
    return RedirectResponse(url=f"/auth/callback?code={code}&state={state}")

# Serve static files from the root directory
app.mount("/", StaticFiles(directory=str(static_path), html=True), name="root")

# Catch-all route for SPA - this should be the last route
@app.get("/{full_path:path}")
async def serve_spa(full_path: str, request: Request):
    """Serve the SPA for all other routes"""
    if is_api_route(request.url.path):
        raise HTTPException(status_code=404, detail="API route not found")
        
    index_path = static_path / "index.html"
    if not index_path.exists():
        logger.error(f"index.html not found at {index_path}")
        raise HTTPException(status_code=500, detail="Frontend assets not found")
        
    return FileResponse(str(index_path))