#!/bin/bash

# Add Node.js buildpack first
heroku buildpacks:clear
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set SPOTIFY_CLIENT_ID=$SPOTIFY_CLIENT_ID
heroku config:set SPOTIFY_CLIENT_SECRET=$SPOTIFY_CLIENT_SECRET
heroku config:set SPOTIFY_REDIRECT_URI=https://playlist-mgr-39a919ee8105.herokuapp.com/callback
heroku config:set ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Set build environment
heroku config:set NODE_ENV=production
heroku config:set NPM_CONFIG_PRODUCTION=false

echo "Buildpacks and environment variables have been configured."
echo "Now you can deploy using:"
echo "git push heroku main"