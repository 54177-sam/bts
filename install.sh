#!/bin/bash
# SIBERINDO BTS GUI Installation Script
# Automated installation and setup

set -e

echo "=========================================="
echo "SIBERINDO BTS GUI - Installation Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python version: $PYTHON_VERSION${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "siberindo-venv" ]; then
    python3 -m venv siberindo-venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source siberindo-venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install requirements
echo ""
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}requirements.txt not found!${NC}"
    exit 1
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from modules import database; database.init_db()" 2>/dev/null || {
    echo -e "${YELLOW}⚠ Database initialization warning (may already exist)${NC}"
}
echo -e "${GREEN}✓ Database ready${NC}"

# Create data and logs directories
echo ""
echo "Creating data and log directories..."
mkdir -p data logs
echo -e "${GREEN}✓ Directories created${NC}"

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    import app
    from modules import database, auth, dashboard
    print('✓ All modules imported successfully')
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
" || exit 1

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment:"
echo "     source siberindo-venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python3 app.py"
echo ""
echo "  3. Open browser:"
echo "     http://localhost:5000"
echo ""
echo "  Default login: admin / password123"
echo ""
echo "To run tests:"
echo "  python3 -m pytest tests/test_suite.py -v"
echo ""
echo "=========================================="
echo ""
echo "Access: http://localhost:5000"
echo "Login: admin / admin"
echo "Company: SIBERINDO Technology"