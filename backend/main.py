import os
import sys
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from api import auth, search, playlist, brands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'spotify_app_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)

# Create logger for this file
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Spotify Playlist Manager API")
    logger.info("Configured routes:")
    logger.info("- /auth: Authentication endpoints")
    logger.info("- /api/search: Search endpoints")
    logger.info("- /api/playlist: Playlist management endpoints")
    logger.info("- /api/brands: Brand profile endpoints")
    yield
    # Shutdown
    logger.info("Shutting down Spotify Playlist Manager API")

app = FastAPI(
    title="Spotify Playlist Manager",
    lifespan=lifespan
)

# Get the port from Heroku environment, or use default
port = int(os.environ.get("PORT", 3001))

# Configure CORS
allowed_origins = [
    "http://localhost:3000",
    "https://playlist-mgr-39a919ee8105.herokuapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with logging
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(playlist.router, prefix="/api/playlist", tags=["playlist"])
app.include_router(brands.router, prefix="/api/brands", tags=["brands"])

# Determine the static files directory based on environment
is_heroku = "DYNO" in os.environ
if is_heroku:
    static_dir = os.path.join(os.getcwd(), "frontend", "build")
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(os.path.dirname(current_dir), "frontend", "build")

# Log the static directory path
logger.info(f"Static directory path: {static_dir}")

# Function to serve index.html
def get_index_html():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return index_path
    else:
        logger.error(f"index.html not found at {index_path}")
        raise HTTPException(status_code=404, detail="Frontend not built")

# Mount static files if the directory exists
if os.path.exists(static_dir):
    logger.info(f"Serving static files from: {static_dir}")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Also mount at root to serve other static assets
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="root")
else:
    logger.warning(f"Static directory not found: {static_dir}")

@app.exception_handler(404)
async def custom_404_handler(request, exc):
    """Handle 404 errors by serving index.html for frontend routes"""
    if request.url.path.startswith("/api") or request.url.path.startswith("/auth"):
        return JSONResponse(
            status_code=404,
            content={"detail": "API endpoint not found"}
        )
    try:
        return FileResponse(get_index_html())
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "static_dir": static_dir,
        "static_dir_exists": os.path.exists(static_dir),
        "index_exists": os.path.exists(os.path.join(static_dir, "index.html")) if static_dir else False
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)