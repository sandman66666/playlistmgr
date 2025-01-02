from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from api import auth, playlist, search, brands
import logging
import os
from pathlib import Path

# Find the STATIC_DIR definition and update it
STATIC_DIR = os.getenv('STATIC_DIR', str(Path(__file__).parent / "static"))
logger.info(f"Static directory path: {STATIC_DIR}")

# Create directory if it doesn't exist
Path(STATIC_DIR).mkdir(parents=True, exist_ok=True)

# Mount static files at root path - this should be the LAST route registration
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Get the absolute path to the static directory
STATIC_DIR = Path(__file__).parent / "static"
logger.info(f"Static directory path: {STATIC_DIR}")

# Ensure static directory exists
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Function to check if path is an API route
def is_api_route(path: str) -> bool:
    api_prefixes = ("/api/", "/auth/", "/playlist/", "/search/", "/brands/")
    return path.startswith(api_prefixes)

# Function to verify static files
def verify_static_files():
    try:
        if not STATIC_DIR.exists():
            logger.error("Static directory does not exist")
            return False
        
        index_path = STATIC_DIR / "index.html"
        if not index_path.exists():
            logger.error("index.html not found")
            return False
            
        logger.info(f"Static directory contents: {[f.name for f in STATIC_DIR.iterdir()]}")
        return True
    except Exception as e:
        logger.error(f"Error verifying static files: {e}")
        return False

# Mount static files with fallback
app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

@app.on_event("startup")
async def startup_event():
    """Verify static files on startup"""
    logger.info("Starting application...")
    if not verify_static_files():
        logger.warning("Static file verification failed - app may not serve frontend correctly")

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """Handle 404 errors - serve index.html for frontend routes"""
    if is_api_route(request.url.path):
        return JSONResponse(
            status_code=404,
            content={"detail": "API route not found"}
        )
    
    index_path = STATIC_DIR / "index.html"
    logger.debug(f"Attempting to serve index.html for path: {request.url.path}")
    
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        logger.error(f"index.html not found at {index_path}")
        current_files = list(STATIC_DIR.iterdir()) if STATIC_DIR.exists() else []
        logger.error(f"Current static files: {current_files}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Frontend assets not found"}
        )

@app.get("/")
async def serve_root():
    """Serve the main index.html"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        logger.debug("Serving index.html from root path")
        return FileResponse(str(index_path))
    logger.error("index.html not found for root path")
    raise HTTPException(status_code=404, detail="Frontend assets not found")

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed status"""
    static_exists = STATIC_DIR.exists()
    static_files = [f.name for f in STATIC_DIR.iterdir()] if static_exists else []
    index_exists = (STATIC_DIR / "index.html").exists()
    
    return {
        "status": "healthy" if index_exists else "degraded",
        "static_dir": str(STATIC_DIR),
        "static_exists": static_exists,
        "static_files": static_files,
        "index_exists": index_exists,
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# Catch-all route for SPA
@app.get("/{full_path:path}")
async def serve_spa(full_path: str, request: Request):
    """Serve the SPA for all other routes"""
    if is_api_route(request.url.path):
        raise HTTPException(status_code=404, detail="API route not found")
        
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        logger.debug(f"Serving index.html for path: {full_path}")
        return FileResponse(str(index_path))
    logger.error(f"index.html not found for path: {full_path}")
    raise HTTPException(status_code=404, detail="Frontend assets not found")