# backend/api/__init__.py
from .auth import router as auth_router
from .playlist import router as playlist_router
from .search import router as search_router
from .brands import router as brands_router

# Export the routers
auth = auth_router
playlist = playlist_router
search = search_router
brands = brands_router