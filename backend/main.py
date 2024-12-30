from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, search, playlist

app = FastAPI(title="Spotify Playlist Manager")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(playlist.router, prefix="/playlist", tags=["playlist"])

@app.get("/")
async def root():
    return {"message": "Spotify Playlist Manager API"}