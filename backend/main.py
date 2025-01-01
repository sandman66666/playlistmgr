import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from api import auth, playlist, search, brands

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "https://playlist-mgr-39a919ee8105-1641bf424db9.herokuapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(playlist.router, prefix="/api/playlist", tags=["playlist"])
app.include_router(brands.router, prefix="/api/brands", tags=["brands"])

# Redirect /callback to /auth/callback
@app.get("/callback")
async def redirect_callback(code: str = None, state: str = None):
    """Redirect /callback to /auth/callback"""
    params = []
    if code:
        params.append(f"code={code}")
    if state:
        params.append(f"state={state}")
    query_string = "&".join(params)
    redirect_url = f"/auth/callback?{query_string}" if params else "/auth/callback"
    return RedirectResponse(url=redirect_url)

# Static files handling
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

if os.path.exists(static_dir):
    logger.info(f"Mounting static files from {static_dir}")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    logger.warning(f"Static directory not found at {static_dir}")
    # Fallback to frontend/build for local development
    frontend_build = os.path.join(current_dir, "..", "frontend", "build")
    if os.path.exists(frontend_build):
        logger.info(f"Mounting static files from {frontend_build}")
        app.mount("/", StaticFiles(directory=frontend_build, html=True), name="static")
    else:
        logger.warning("No static directory found in any of the search paths")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve SPA for any unmatched routes"""
    if os.path.exists(static_dir):
        index_path = os.path.join(static_dir, "index.html")
    else:
        index_path = os.path.join(current_dir, "..", "frontend", "build", "index.html")
        
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Not found")

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("Starting Spotify Playlist Manager API")
    logger.info("Configured routes:")
    logger.info("- /auth: Authentication endpoints")
    logger.info("- /api/search: Search endpoints")
    logger.info("- /api/playlist: Playlist management endpoints")
    logger.info("- /api/brands: Brand profile endpoints")
    logger.info(f"Static files directory: {static_dir}")

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    logger.info("Shutting down Spotify Playlist Manager API")