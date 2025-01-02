from fastapi import APIRouter

# Create individual routers
auth = APIRouter()
playlist = APIRouter()
search = APIRouter()
brands = APIRouter()

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