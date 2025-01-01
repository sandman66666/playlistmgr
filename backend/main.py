import os
import sys
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Serve static files from frontend build
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "build")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the SPA's index.html for any path not handled by the API or static files"""
        return FileResponse(os.path.join(static_dir, "index.html"))

# Root endpoint for health check
@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/auth", "/api/search", "/api/playlist", "/api/brands"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)