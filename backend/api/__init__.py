from fastapi import APIRouter
from .auth import router as auth_router
from .playlist import router as playlist_router
from .search import router as search_router
from .brands import router as brands_router

# Export the routers
auth = auth_router
playlist = playlist_router
search = search_router
brands = brands_router

# Basic status endpoints for monitoring
@auth.get("/status")
async def auth_status():
    return {"status": "operational"}

@playlist.get("/status")
async def playlist_status():
    return {"status": "operational"}

@search.get("/status")
async def search_status():
    return {"status": "operational"}

@brands.get("/status")
async def brands_status():
    return {"status": "operational"}