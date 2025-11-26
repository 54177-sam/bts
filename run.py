#!/usr/bin/env python3
"""
Runner script for SIBERINDO BTS GUI
"""

import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    # Initialize database
    try:
        import modules.database as db
        db.init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
    
    # Start application
    print("SIBERINDO BTS GUI Starting...")
    print("Access URL: http://localhost:5000")
    print("Default login: admin / admin")
    app.run(host='0.0.0.0', port=5000, debug=True)