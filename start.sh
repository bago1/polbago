#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display messages
function info {
    echo "[INFO] $1"
}

# Update package list and install python3-venv if not already installed
info "Updating package list and installing python3-venv..."
sudo apt update || true
sudo apt install -y python3-venv

# Remove existing virtual environment if any
info "Removing existing virtual environment (if any)..."
rm -rf .venv

# Create a new virtual environment
info "Creating a new virtual environment..."
python3 -m venv .venv

# Activate the virtual environment
info "Activating the virtual environment..."
source .venv/bin/activate

# Upgrade pip
info "Upgrading pip..."
pip install --upgrade pip

# Check if requirements.txt exists and install, else install manually
if [ -f requirements.txt ]; then
    info "Installing packages from requirements.txt..."
    # Remove sqlite3 from requirements.txt if it exists
    sed -i '/sqlite/d' requirements.txt
    pip install -r requirements.txt
else
    info "Installing Flask, pymongo, and python-daemon manually..."
    pip install Flask pymongo python-daemon
fi

# Ensure python-daemon and pymongo are installed if they weren't in requirements.txt
info "Ensuring python-daemon and pymongo are installed..."
pip install python-daemon pymongo

# Verify installation
info "Verifying installed packages..."
pip list

# Run the application
info "Running the application..."
python app.py
