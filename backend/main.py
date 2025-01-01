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

# Get the absolute path to the static directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

# Log the static directory path
logger.info(f"Static directory path: {static_dir}")
logger.info(f"Static directory contents: {os.listdir(static_dir)}")

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith(("/api/", "/auth/", "/playlist/", "/search/", "/brands/")):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )
    
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        logger.error(f"index.html not found at {index_path}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"index.html not found at {index_path}"}
        )

@app.get("/")
async def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        logger.error(f"index.html not found at {index_path}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"index.html not found at {index_path}"}
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "static_dir": static_dir, "files": os.listdir(static_dir)}