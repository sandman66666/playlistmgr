# backend/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
import shutil
from pathlib import Path

# Import routers
from api import auth, playlist, search, brands

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
        if item.is_file():
            shutil.copy2(str(item), str(static_path))
        elif item.is_dir():
            dest_dir = static_path / item.name
            if dest_dir.exists():
                shutil.rmtree(str(dest_dir))
            shutil.copytree(str(item), str(dest_dir))

# Configure CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://playlist-mgr-39a919ee8105.herokuapp.com")
CORS_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:3001"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(playlist.router, prefix="/playlist", tags=["playlist"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(brands.router, prefix="/brands", tags=["brands"])

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
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# Serve static files
app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")

# Catch-all route for SPA
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

# Mount the root path to serve static files
app.mount("/", StaticFiles(directory=str(static_path), html=True), name="root")