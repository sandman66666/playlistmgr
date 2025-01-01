from setuptools import setup, find_packages

setup(
    name="spotify_playlist_manager",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "spotipy",
        "python-dotenv"
    ],
)