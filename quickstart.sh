#!/bin/bash
# SIBERINDO BTS GUI - Quick Start Script
# This script demonstrates how to run the application

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  SIBERINDO BTS GUI - Quick Start                              ║"
echo "║  Complete Full-Stack GSM Management System                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

echo -e "${BLUE}1. Checking prerequisites...${NC}"
python3 --version

echo ""
echo -e "${BLUE}2. Creating virtual environment...${NC}"
if [ ! -d "siberindo-venv" ]; then
    python3 -m venv siberindo-venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo -e "${BLUE}3. Activating virtual environment...${NC}"
source siberindo-venv/bin/activate || . siberindo-venv/Scripts/activate
echo "✓ Virtual environment activated"

echo ""
echo -e "${BLUE}4. Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo -e "${BLUE}5. Initializing database...${NC}"
if [ ! -f "data/siberindo_bts.db" ]; then
    python scripts/init_db.py
    echo "✓ Database initialized"
else
    echo "✓ Database already exists"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Setup Complete! Starting application...                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Access the application at: http://localhost:5000${NC}"
echo -e "${GREEN}Default credentials:${NC}"
echo "  Username: admin"
echo "  Password: password123"
echo ""
echo "Alternative operators:"
echo "  Username: operator1"
echo "  Password: operator123"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the application
python app.py
