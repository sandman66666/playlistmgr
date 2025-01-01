#!/bin/bash

# Add Node.js buildpack first
heroku buildpacks:clear
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set SPOTIFY_CLIENT_ID=39334229925441f79f881f8ca90ca55a
heroku config:set SPOTIFY_CLIENT_SECRET=49aa3c1a3c9442109221e49705d57403
heroku config:set SPOTIFY_REDIRECT_URI=https://playlist-mgr-39a919ee8105-1641bf424db9.herokuapp.com/callback

# Set build environment
heroku config:set NODE_ENV=production
heroku config:set NPM_CONFIG_PRODUCTION=false

echo "Buildpacks and environment variables have been configured."
echo "IMPORTANT: Add this URL to your Spotify App Dashboard Redirect URIs:"
echo "https://playlist-mgr-39a919ee8105-1641bf424db9.herokuapp.com/callback"
echo ""
echo "Now you can deploy using:"
echo "git push heroku main"