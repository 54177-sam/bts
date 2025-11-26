import os
from pathlib import Path


class Config:
    """Application configuration with environment variable support."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'siberindo-bts-gui-secure-key-2024')
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'siberindo_bts.db')
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '5'))
    DB_MAX_OVERFLOW = int(os.environ.get('DB_MAX_OVERFLOW', '10'))
    
    # Session
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))
    PERMANENT_SESSION_LIFETIME = SESSION_TIMEOUT
    
    # Service Ports
    BTS_PORT = int(os.environ.get('BTS_PORT', '4242'))
    BSC_PORT = int(os.environ.get('BSC_PORT', '4241'))
    HLR_PORT = int(os.environ.get('HLR_PORT', '4258'))
    
    # HackRF Configuration
    HACKRF_SAMPLE_RATE = int(os.environ.get('HACKRF_SAMPLE_RATE', '2000000'))
    HACKRF_GAIN = int(os.environ.get('HACKRF_GAIN', '40'))
    HACKRF_TIMEOUT = int(os.environ.get('HACKRF_TIMEOUT', '10'))
    
    # SMS Configuration
    SMS_MAX_LENGTH = int(os.environ.get('SMS_MAX_LENGTH', '160'))
    SMS_BATCH_SIZE = int(os.environ.get('SMS_BATCH_SIZE', '100'))
    
    # Cache Settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Company Information
    COMPANY_NAME = "SIBERINDO"
    COMPANY_FULL_NAME = "SIBERINDO Technology"
    VERSION = "1.0.0"
    
    # Admin Credentials (override with environment variables in production)
    ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
    ADMIN_PASS = os.environ.get('ADMIN_PASS', 'admin')
    
    # Application Settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('FLASK_TESTING', 'False').lower() == 'true'
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = DEBUG