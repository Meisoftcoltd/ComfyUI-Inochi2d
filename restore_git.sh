#!/bin/bash

# ComfyUI-Inochi2D Git Restoration Script
# Use this script if you downloaded the repository as a ZIP and want to enable Git updates.

REPO_URL="https://github.com/Meisoftcoltd/ComfyUI-Inochi2d"

if [ -d .git ]; then
    echo "Git repository already exists."
    exit 0
fi

echo "Initializing Git repository..."
git init

echo "WARNING: This script will perform a forced checkout which will overwrite any local changes to tracked files."
echo "Press Ctrl+C to cancel or wait 5 seconds to continue..."
sleep 5

echo "Adding remote origin: $REPO_URL"
git remote add origin "$REPO_URL"

echo "Fetching from origin..."
git fetch

echo "Setting up main branch..."
git checkout -t origin/main -f

echo "Git repository successfully restored. You can now update using 'git pull' or ComfyUI-Manager."
