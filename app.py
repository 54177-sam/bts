#!/usr/bin/env python3
"""
SIBERINDO BTS GUI - Modular GSM Network Management Interface
Main application file - ENHANCED VERSION
"""

import logging
import sys
import os
from flask import Flask, session

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bts_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'siberindo-bts-secret-key-2024-enhanced'
app.config['SESSION_TYPE'] = 'filesystem'

# Import and register blueprints with comprehensive error handling
def register_blueprints():
    """Dynamically register all blueprints with proper error handling"""
    blueprints_config = [
        {
            'module': 'modules.dashboard',
            'blueprint': 'dashboard_bp',
            'url_prefix': '/dashboard'
        },
        {
            'module': 'modules.auth', 
            'blueprint': 'auth_bp',
            'url_prefix': '/auth'
        },
        {
            'module': 'modules.subscribers',
            'blueprint': 'subscribers_bp', 
            'url_prefix': '/subscribers'
        },
        {
            'module': 'modules.sms_manager',
            'blueprint': 'sms_bp',
            'url_prefix': '/sms'
        },
        {
            'module': 'modules.bts_scanner',
            'blueprint': 'scanner_bp',
            'url_prefix': '/scanner'
        }
    ]
    
    registered_count = 0
    for config in blueprints_config:
        try:
            # Dynamic import
            module = __import__(config['module'], fromlist=[config['blueprint']])
            bp = getattr(module, config['blueprint'])
            app.register_blueprint(bp, url_prefix=config.get('url_prefix'))
            logger.info(f"✓ Successfully registered {config['blueprint']}")
            registered_count += 1
        except ImportError as e:
            logger.warning(f"✗ Module {config['module']} not found: {e}")
        except AttributeError as e:
            logger.warning(f"✗ Blueprint {config['blueprint']} not found in {config['module']}: {e}")
        except Exception as e:
            logger.error(f"✗ Error registering {config['blueprint']}: {e}")
    
    return registered_count

# Register blueprints
registered_bps = register_blueprints()
logger.info(f"Registered {registered_bps} blueprints successfully")

@app.route('/')
def index():
    """Main entry point"""
    from flask import redirect, url_for
    # Simple session management for development
    session['logged_in'] = True
    session['username'] = 'admin'
    session['role'] = 'administrator'
    return redirect(url_for('dashboard.dashboard'))

@app.route('/health')
def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        'status': 'healthy',
        'service': 'SIBERINDO BTS GUI',
        'version': '2.0.0',
        'registered_blueprints': registered_bps,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    return health_status

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found', 'status': 404}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error', 'status': 500}, 500

if __name__ == '__main__':
    logger.info("🚀 Starting SIBERINDO BTS GUI - ENHANCED VERSION")
    print("=" * 50)
    print("SIBERINDO BTS GSM Management System")
    print("Version: 2.0.0 - Enhanced")
    print("Access URL: http://localhost:5000")
    print("Health check: http://localhost:5000/health")
    print("Default login: admin / admin")
    print("=" * 50)
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)