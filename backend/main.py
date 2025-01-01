import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from api import auth, playlist, search, brands
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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

# Get the absolute path to the frontend build directory
build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "build")
logger.info(f"Frontend build directory path: {build_dir}")

# Create build directory if it doesn't exist
os.makedirs(build_dir, exist_ok=True)

# Log build directory contents
try:
    logger.info(f"Build directory contents: {os.listdir(build_dir)}")
except Exception as e:
    logger.error(f"Error listing build directory: {e}")

# Mount frontend build files at root path
app.mount("/", StaticFiles(directory=build_dir, html=True), name="frontend")

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    if request.url.path.startswith(("/api/", "/auth/", "/playlist/", "/search/", "/brands/")):
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )
    
    index_path = os.path.join(build_dir, "index.html")
    logger.debug(f"Attempting to serve index.html from: {index_path}")
    
    if os.path.exists(index_path):
        logger.info(f"Serving index.html from: {index_path}")
        try:
            with open(index_path, 'r') as f:
                logger.debug(f"index.html contents: {f.read()}")
        except Exception as e:
            logger.error(f"Error reading index.html: {e}")
        return FileResponse(index_path)
    else:
        logger.error(f"index.html not found at {index_path}")
        try:
            logger.error(f"Directory contents: {os.listdir(os.path.dirname(index_path))}")
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"index.html not found at {index_path}"}
        )

@app.get("/health")
async def health_check():
    # Add directory structure to health check
    dir_contents = {}
    try:
        dir_contents = {
            "build_dir": build_dir,
            "build_files": os.listdir(build_dir),
            "index_exists": os.path.exists(os.path.join(build_dir, "index.html")),
            "cwd": os.getcwd(),
            "abs_build_path": os.path.abspath(build_dir)
        }
    except Exception as e:
        dir_contents = {"error": str(e)}
    
    return {
        "status": "healthy",
        "directory_info": dir_contents
    }