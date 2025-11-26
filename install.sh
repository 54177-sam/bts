#!/bin/bash
set -e

echo "=== SIBERINDO BTS GUI Installer ==="
echo "Installing system dependencies..."

# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3 python3-pip sqlite3

# Install HackRF if available (skip if fails)
if apt-cache show hackrf 2>/dev/null | grep -q Package; then
    echo "Installing HackRF tools..."
    sudo apt install -y hackrf || echo "HackRF installation failed, continuing without it..."
else
    echo "HackRF not available in repositories, skipping..."
fi

# Install Osmocom packages if available
if apt-cache show osmocom 2>/dev/null | grep -q Package; then
    echo "Installing Osmocom packages..."
    sudo apt install -y osmocom || echo "Osmocom installation failed, continuing without it..."
else
    echo "Osmocom packages not available in repositories, you may need to compile from source."
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv siberindo-venv

# Install Python packages
echo "Installing Python dependencies..."
source siberindo-venv/bin/activate
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python3 -c "import modules.database; modules.database.init_db()"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "To run the application:"
echo "  source siberindo-venv/bin/activate"
echo "  python3 run.py"
echo ""
echo "Or use the provided run script:"
echo "  ./start.sh"
echo ""
echo "Access: http://localhost:5000"
echo "Login: admin / admin"
echo "Company: SIBERINDO Technology"