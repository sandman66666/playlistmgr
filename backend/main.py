from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, search, playlist, brands

app = FastAPI(title="Spotify Playlist Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(playlist.router, prefix="/playlist", tags=["playlist"])
app.include_router(brands.router, prefix="/brands", tags=["brands"])