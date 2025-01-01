import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from api import auth, playlist, search, brands
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'spotify_app_{os.getenv("ENVIRONMENT", "development")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith("/api/") or request.url.path.startswith("/auth/"):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )
    try:
        return FileResponse(os.path.join(static_dir, "index.html"))
    except Exception:
        # If index.html is not found, try to serve from the root of static directory
        return FileResponse(os.path.join(static_dir, "../static/index.html"))

@app.get("/")
async def read_root():
    try:
        return FileResponse(os.path.join(static_dir, "index.html"))
    except Exception:
        # If index.html is not found, try to serve from the root of static directory
        return FileResponse(os.path.join(static_dir, "../static/index.html"))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}