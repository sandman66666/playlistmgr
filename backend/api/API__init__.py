from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .search import router as search_router
from .playlist import router as playlist_router
from .auth import router as auth_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with proper prefixes
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(search_router, prefix="/api", tags=["search"])
app.include_router(playlist_router, prefix="/api/playlist", tags=["playlist"])