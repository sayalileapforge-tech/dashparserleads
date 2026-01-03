#!/bin/bash
set -o errexit

pip install -r requirements.txt

# Initialize database if needed
python -c "from app import app; print('App loaded successfully')"

echo "Build complete!"
