# SIBERINDO BTS GUI - Complete Setup Guide

## 📋 Prerequisites Checklist

Sebelum memulai instalasi, pastikan sistem Anda memenuhi persyaratan berikut:

- [ ] Python 3.8 atau lebih tinggi terinstall
- [ ] pip (Python package manager) terinstall
- [ ] Virtual environment (venv) tersedia
- [ ] SQLite3 database support
- [ ] Terminal/Command line access
- [ ] Minimal 100MB disk space
- [ ] Port 5000 tersedia untuk Flask (atau gunakan PORT env variable)

## 🚀 Step-by-Step Installation

### Step 1: Verify Python Installation

```bash
# Check Python version
python3 --version

# Should output: Python 3.8.x or higher
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/54177-sam/bts.git
cd bts

# List directory to verify files
ls -la
```

### Step 3: Run Installation Script

```bash
# Make script executable
chmod +x install.sh

# Run installation
./install.sh
```

**Alternative Manual Installation:**

```bash
# Create virtual environment
python3 -m venv siberindo-venv

# Activate virtual environment
source siberindo-venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from modules import database; database.init_db()"

# Create necessary directories
mkdir -p data logs
```

### Step 4: Verify Installation

```bash
# Activate venv if not already
source siberindo-venv/bin/activate

# Run verification
python3 -c "
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    import app
    from modules import database, auth, dashboard
    print('✓ Installation successful!')
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
"
```

## ▶️ Running the Application

### Start the Application

```bash
# Activate virtual environment
source siberindo-venv/bin/activate

# Run application with default settings
python3 app.py

# Or with custom port
PORT=8080 python3 app.py

# Or with debug mode
DEBUG=True python3 app.py
```

### Access the Application

Once running, open your browser and navigate to:

```
http://localhost:5000
```

**Default Credentials:**
- Username: `admin`
- Password: `password123`

## 🧪 Running Tests

### Full Test Suite

```bash
# Activate virtual environment
source siberindo-venv/bin/activate

# Run all tests
python3 -m pytest tests/test_suite.py -v

# Expected: 28 tests passing
```

### Specific Test Classes

```bash
# Test database operations
python3 -m pytest tests/test_suite.py::TestDatabaseOperations -v

# Test validation
python3 -m pytest tests/test_suite.py::TestDataValidation -v

# Test Flask routes
python3 -m pytest tests/test_suite.py::TestFlaskRoutes -v

# Test API responses
python3 -m pytest tests/test_suite.py::TestAPIResponses -v
```

### Test Coverage Report

```bash
# Generate coverage report
python3 -m pytest tests/test_suite.py --cov=modules --cov-report=html

# Open report in browser
open htmlcov/index.html
```

## 🔧 Configuration

### Environment Variables

Customize aplikasi dengan environment variables:

```bash
# Database path
export DB_PATH="data/bts_database.db"

# Server settings
export HOST="0.0.0.0"
export PORT="5000"
export DEBUG="False"

# Cache settings
export CACHE_TYPE="simple"
export CACHE_TIMEOUT="300"

# Database performance
export DB_POOL_SIZE="10"
export DB_MAX_OVERFLOW="20"
```

### config.py Settings

Edit `config.py` untuk persistent configuration:

```python
# Database configuration
DATABASE_PATH = os.getenv('DB_PATH', 'data/bts_database.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

# Server configuration
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Cache configuration
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 300))

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
```

## 📁 Directory Structure

Setelah setup, struktur direktori seharusnya:

```
siberindo-bts-gui/
├── app.py                      # Main application
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── install.sh                  # Installation script
├── start.sh                    # Start script
│
├── modules/
│   ├── __init__.py
│   ├── auth.py                 # Authentication
│   ├── dashboard.py            # Dashboard
│   ├── database.py             # Database layer
│   ├── helpers.py              # Utilities
│   ├── sms_manager.py          # SMS operations
│   ├── subscribers.py          # Subscribers
│   ├── bts_scanner.py          # BTS scanning
│   ├── service_manager.py      # Services
│   ├── hackrf_manager.py       # HackRF handling
│   ├── validators.py           # Validation
│   ├── middleware.py           # API middleware
│   └── __pycache__/
│
├── templates/
│   ├── base.html               # Base template
│   ├── dashboard.html
│   ├── subscribers.html
│   ├── send_sms.html
│   ├── send_silent_sms.html
│   ├── sms_history.html
│   ├── bts_scanner.html
│   ├── login.html
│   └── error.html
│
├── static/
│   ├── css/                    # Stylesheets
│   └── js/                     # JavaScript
│
├── data/                       # Data directory
│   └── bts_database.db         # SQLite database
│
├── logs/                       # Log files
│   └── bts_system.log          # System log
│
├── tests/
│   └── test_suite.py           # Test suite
│
├── siberindo-venv/             # Python virtual environment
└── README.md                   # Documentation
```

## 🐛 Troubleshooting

### Issue: Port 5000 Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use different port
PORT=8080 python3 app.py
```

### Issue: Module Import Error

**Error**: `ModuleNotFoundError: No module named 'modules'`

**Solution**:
```bash
# Ensure virtual environment is activated
source siberindo-venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Verify imports
python3 -c "import modules"
```

### Issue: Database Locked

**Error**: `database is locked`

**Solution**:
```bash
# Remove lock files
rm -f data/bts_database.db-wal
rm -f data/bts_database.db-shm

# Reinitialize database
python3 -c "from modules import database; database.init_db()"
```

### Issue: Permission Denied on install.sh

**Error**: `Permission denied`

**Solution**:
```bash
# Make script executable
chmod +x install.sh

# Run it again
./install.sh
```

### Issue: Tests Failing

**Error**: Multiple test failures

**Solution**:
```bash
# Activate virtual environment
source siberindo-venv/bin/activate

# Run single test with verbose output
python3 -m pytest tests/test_suite.py::TestDatabaseOperations::test_get_subscribers_count -vv

# Check logs
tail -50 logs/bts_system.log
```

## 📊 Verification Checklist

Setelah instalasi, verifikasi dengan checklist berikut:

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (check: `pip list`)
- [ ] Database initialized (check: `ls -la data/bts_database.db`)
- [ ] Test suite passing (check: `pytest tests/test_suite.py -v`)
- [ ] Application starts without errors
- [ ] Dashboard accessible at `http://localhost:5000`
- [ ] Login works with default credentials
- [ ] Subscribers page loads successfully
- [ ] SMS management page accessible
- [ ] BTS Scanner page accessible
- [ ] All routes return valid responses

### Run Complete Verification

```bash
#!/bin/bash
source siberindo-venv/bin/activate

echo "Running verification..."
echo ""

echo "1. Checking Python version..."
python3 --version

echo ""
echo "2. Checking database..."
if [ -f "data/bts_database.db" ]; then
    echo "✓ Database exists"
else
    echo "✗ Database missing"
fi

echo ""
echo "3. Running tests..."
python3 -m pytest tests/test_suite.py -v --tb=no | tail -5

echo ""
echo "Verification complete!"
```

## 🚀 Production Deployment

### Pre-Deployment Checklist

```bash
# 1. Update configuration
# Edit config.py with production settings

# 2. Set environment variables
export DEBUG="False"
export SECRET_KEY="your-secure-random-key"

# 3. Update database settings
export DB_PATH="/var/lib/siberindo/database.db"

# 4. Run tests
python3 -m pytest tests/test_suite.py -v

# 5. Test application start
timeout 5 python3 app.py || true
```

### Using Gunicorn (Production WSGI Server)

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with logging
gunicorn -w 4 -b 0.0.0.0:5000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  app:app
```

### Using Systemd Service

Create `/etc/systemd/system/siberindo-bts.service`:

```ini
[Unit]
Description=SIBERINDO BTS GUI
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/siberindo-bts-gui
Environment="PATH=/opt/siberindo-bts-gui/siberindo-venv/bin"
ExecStart=/opt/siberindo-bts-gui/siberindo-venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start siberindo-bts
sudo systemctl enable siberindo-bts
```

## 📝 Logs

### View Application Logs

```bash
# View latest logs
tail -100 logs/bts_system.log

# Follow logs in real-time
tail -f logs/bts_system.log

# Search in logs
grep "ERROR" logs/bts_system.log
```

## 🤝 Support & Help

- Check README.md for general documentation
- Review logs/ directory for error details
- Run tests to diagnose issues
- Consult troubleshooting section above

---

**Version**: 2.0.0  
**Last Updated**: November 26, 2024  
**Status**: Production Ready
