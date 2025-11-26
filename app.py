#!/usr/bin/env python3
"""
SIBERINDO BTS GUI - Modular GSM Network Management Interface
Main application file - OPTIMIZED VERSION
"""

import logging
import sys
import os
from flask import Flask

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'siberindo-bts-secret-key-2024'  # Simple secret key for development

# Import and register blueprints with error handling
def register_blueprints():
    """Dynamically register all blueprints with fallback"""
    blueprints = [
        ('modules.dashboard', 'dashboard_bp'),
        ('modules.auth', 'auth_bp'),
        ('modules.subscribers', 'subscribers_bp'), 
        ('modules.sms_manager', 'sms_bp'),
        ('modules.bts_scanner', 'scanner_bp')
    ]
    
    for module_name, bp_name in blueprints:
        try:
            module = __import__(module_name, fromlist=[bp_name])
            bp = getattr(module, bp_name)
            app.register_blueprint(bp)
            logger.info(f"Successfully registered {bp_name}")
        except ImportError as e:
            logger.warning(f"Module {module_name} not found: {e}")
        except AttributeError as e:
            logger.warning(f"Blueprint {bp_name} not found in {module_name}: {e}")

register_blueprints()

@app.route('/')
def index():
    from flask import session, redirect, url_for
    # Simple session check - always go to dashboard for now
    return redirect(url_for('dashboard.dashboard'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'SIBERINDO BTS GUI'}

if __name__ == '__main__':
    logger.info("Starting SIBERINDO BTS GUI - OPTIMIZED VERSION")
    print("Access URL: http://localhost:5000")
    print("Health check: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)