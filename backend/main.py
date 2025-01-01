import os
import sys
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with logging
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(playlist.router, prefix="/api/playlist", tags=["playlist"])
app.include_router(brands.router, prefix="/api/brands", tags=["brands"])

# Root endpoint for health check
@app.get("/")
async def root():
    logger.info("Health check endpoint called")
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/auth", "/api/search", "/api/playlist", "/api/brands"]
    }