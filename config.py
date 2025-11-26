import os
from pathlib import Path

class Config:
    SECRET_KEY = 'siberindo-bts-gui-secure-key-2024'
    DATABASE_PATH = 'siberindo_bts.db'
    SESSION_TIMEOUT = 3600  # 1 hour
    
    # Service configurations
    BTS_PORT = 4242
    BSC_PORT = 4241
    HLR_PORT = 4258
    
    # HackRF settings
    HACKRF_SAMPLE_RATE = 2000000
    HACKRF_GAIN = 40
    
    # SMS settings
    SMS_MAX_LENGTH = 160
    
    # Company Information
    COMPANY_NAME = "SIBERINDO"
    COMPANY_FULL_NAME = "SIBERINDO Technology"
    VERSION = "1.0.0"
    # Admin credentials (override with environment variables in production)
    ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
    ADMIN_PASS = os.environ.get('ADMIN_PASS', 'admin')