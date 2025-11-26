import os
from datetime import timedelta

class Config:
    """Application configuration"""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'siberindo-bts-enhanced-secret-2024'
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Application
    DEBUG = True
    TESTING = False
    
    # BTS Configuration
    BTS_MCC = '001'  # Mobile Country Code
    BTS_MNC = '01'   # Mobile Network Code  
    BTS_LAC = '1001' # Location Area Code
    BTS_CID = '1'    # Cell ID
    
    # HackRF Configuration
    HACKRF_SIMULATION_MODE = True  # Set to False for real hardware
    HACKRF_SAMPLE_RATE = 1000000   # 1 MHz
    HACKRF_FREQUENCY = 942000000   # 942 MHz
    
    # Services Configuration
    SERVICES = {
        'osmo_bts': {'port': 4238, 'enabled': True},
        'osmo_bsc': {'port': 4240, 'enabled': True},
        'osmo_msc': {'port': 4242, 'enabled': True},
        'osmo_hlr': {'port': 4243, 'enabled': False},
        'osmo_sgsn': {'port': 4244, 'enabled': False},
        'osmo_ggsn': {'port': 4245, 'enabled': False}
    }
    
    # Database
    DATABASE_PATH = 'data/bts_database.db'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/bts_system.log'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    HACKRF_SIMULATION_MODE = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class TestingConfig(Config):
    TESTING = True
    HACKRF_SIMULATION_MODE = True