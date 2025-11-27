import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'siberindo-secret-key-2024'
    DB_PATH = os.environ.get('DB_PATH') or 'data/siberindo_bts.db'
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    
    # BTS Scanner config
    BTS_SCANNER_MOCK = os.environ.get('BTS_SCANNER_MOCK', 'True').lower() == 'true'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

config = DevelopmentConfig if os.environ.get('FLASK_ENV') == 'development' else ProductionConfig