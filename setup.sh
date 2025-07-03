#!/bin/bash

# Setup script for Streamlit Web Scraping Tool
# This script is optional and can be used for additional setup if needed

echo "🚀 Setting up Streamlit Web Scraping Tool..."

# Update system packages (if running on Linux)
if command -v apt-get &> /dev/null; then
    echo "📦 Updating system packages..."
    sudo apt-get update
fi

# Install Python dependencies
echo "📋 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p output

# Set permissions
echo "🔐 Setting permissions..."
chmod +x setup.sh

# Verify installation
echo "✅ Verifying installation..."
python -c "import streamlit; print(f'Streamlit version: {streamlit.__version__}')"
python -c "import requests; print(f'Requests version: {requests.__version__}')"
python -c "import pandas; print(f'Pandas version: {pandas.__version__}')"
python -c "import bs4; print(f'BeautifulSoup version: {bs4.__version__}')"

echo "🎉 Setup completed successfully!"
echo ""
echo "To run the application:"
echo "  streamlit run streamlit_app.py"
echo ""
echo "To deploy to Streamlit Cloud:"
echo "  1. Push your code to GitHub"
echo "  2. Go to https://share.streamlit.io/"
echo "  3. Connect your GitHub repository"
echo "  4. Deploy!"
