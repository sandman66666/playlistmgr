from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from api import auth, playlist, search, brands
import logging
import os
from pathlib import Path

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get the absolute path to the static directory
STATIC_DIR = os.getenv('STATIC_DIR', str(Path(__file__).parent / "static"))

app = FastAPI()

# Configure CORS - restrict in production
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

# Ensure static directory exists
Path(STATIC_DIR).mkdir(parents=True, exist_ok=True)
logger.info(f"Static directory path: {STATIC_DIR}")

# Function to check if path is an API route
def is_api_route(path: str) -> bool:
    api_prefixes = ("/api/", "/auth/", "/playlist/", "/search/", "/brands/", "/health")
    return path.startswith(api_prefixes)

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    static_path = Path(STATIC_DIR)
    static_exists = static_path.exists()
    static_files = [f.name for f in static_path.iterdir()] if static_exists else []
    index_exists = (static_path / "index.html").exists()
    
    return {
        "status": "healthy" if index_exists else "degraded",
        "static_dir": str(STATIC_DIR),
        "static_exists": static_exists,
        "static_files": static_files,
        "index_exists": index_exists,
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# Handle static files - the order of these routes is important
@app.get("/{full_path:path}")
async def serve_static(full_path: str, request: Request):
    """Serve static files and handle SPA routes"""
    if is_api_route(request.url.path):
        raise HTTPException(status_code=404, detail="API route not found")

    index_path = Path(STATIC_DIR) / "index.html"
    logger.debug(f"Serving path: {full_path}")
    logger.debug(f"Index path: {index_path}")
    
    if index_path.exists():
        return FileResponse(str(index_path))
    
    logger.error(f"index.html not found at {index_path}")
    raise HTTPException(status_code=500, detail="Static files not found")

# Mount static files after all routes are defined
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")