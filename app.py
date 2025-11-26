#!/usr/bin/env python3
"""
SIBERINDO BTS GUI - Modular GSM Network Management Interface
Main application file
"""

import logging
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from flask import Flask
app = Flask(__name__)
app.config.from_object('config.Config')

# Import and register blueprints
try:
    from modules.auth import auth_bp
    from modules.dashboard import dashboard_bp
    from modules.subscribers import subscribers_bp
    from modules.sms_manager import sms_bp
    from modules.bts_scanner import scanner_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(subscribers_bp)
    app.register_blueprint(sms_bp)
    app.register_blueprint(scanner_bp)
    
    logger.info("All blueprints registered successfully")
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    print(f"Import error: {e}")

@app.route('/')
def index():
    from flask import session, redirect, url_for
    if session.get('logged_in'):
        return redirect(url_for('dashboard.dashboard'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    logger.info("Starting SIBERINDO BTS GUI...")
    print("Access URL: http://localhost:5000")
    print("Default login: admin / admin")
    app.run(host='0.0.0.0', port=5000, debug=True)