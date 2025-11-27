#!/usr/bin/env python3
"""
Database initialization script for SIBERINDO BTS GUI
Creates schema, migrations, and sample data
"""

import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = 'data/siberindo_bts.db'
DATA_DIR = 'data'

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def ensure_directory():
    """Ensure data directory exists"""
    Path(DATA_DIR).mkdir(exist_ok=True)
    print(f"✓ Data directory created/exists: {DATA_DIR}")

def create_schema(conn):
    """Create database schema"""
    cursor = conn.cursor()
    
    # Drop existing tables if doing fresh install (optional)
    # cursor.execute("DROP TABLE IF EXISTS users")
    # cursor.execute("DROP TABLE IF EXISTS subscribers")
    # cursor.execute("DROP TABLE IF EXISTS sms_history")
    # cursor.execute("DROP TABLE IF EXISTS bts_scans")
    # cursor.execute("DROP TABLE IF EXISTS services_log")
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE,
        full_name TEXT,
        role TEXT DEFAULT 'operator' CHECK(role IN ('administrator', 'operator', 'viewer')),
        enabled BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Subscribers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imsi TEXT UNIQUE NOT NULL,
        msisdn TEXT UNIQUE,
        name TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'suspended', 'blocked')),
        network_type TEXT DEFAULT 'GSM' CHECK(network_type IN ('GSM', '3G', '4G', 'LTE')),
        location TEXT,
        operator TEXT DEFAULT 'Siberindo',
        balance REAL DEFAULT 0.0,
        last_activity TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # SMS History table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sms_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_subscriber TEXT,
        to_subscriber TEXT,
        message_text TEXT,
        message_type TEXT DEFAULT 'standard' CHECK(message_type IN ('standard', 'silent', 'flash')),
        status TEXT DEFAULT 'delivered' CHECK(status IN ('pending', 'sent', 'delivered', 'failed')),
        error_code TEXT,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # BTS Scans table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bts_scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        band TEXT,
        frequency INTEGER,
        mcc TEXT,
        mnc TEXT,
        lac TEXT,
        cell_id TEXT,
        signal_strength INTEGER,
        signal_quality TEXT DEFAULT 'fair' CHECK(signal_quality IN ('excellent', 'good', 'fair', 'poor')),
        operator_name TEXT,
        scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Services log table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT,
        service_key TEXT,
        status TEXT DEFAULT 'running' CHECK(status IN ('running', 'stopped', 'error', 'maintenance')),
        cpu_usage REAL,
        memory_usage REAL,
        uptime INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscribers_imsi ON subscribers(imsi)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscribers_msisdn ON subscribers(msisdn)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscribers_status ON subscribers(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sms_created ON sms_history(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sms_status ON sms_history(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bts_scans_timestamp ON bts_scans(scan_timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_log_timestamp ON services_log(timestamp)')
    
    conn.commit()
    print("✓ Database schema created successfully")

def seed_data(conn):
    """Seed database with initial data"""
    cursor = conn.cursor()
    
    # Check if admin user exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] > 0:
        print("✓ Admin user already exists, skipping seed")
        return
    
    # Add admin user
    admin_password_hash = hash_password('password123')
    cursor.execute('''
    INSERT INTO users (username, password_hash, email, full_name, role, enabled)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ('admin', admin_password_hash, 'admin@siberindo.local', 'Administrator', 'administrator', 1))
    
    # Add sample operators
    operator_password_hash = hash_password('operator123')
    cursor.execute('''
    INSERT INTO users (username, password_hash, email, full_name, role, enabled)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ('operator1', operator_password_hash, 'operator1@siberindo.local', 'Operator 1', 'operator', 1))
    
    cursor.execute('''
    INSERT INTO users (username, password_hash, email, full_name, role, enabled)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ('operator2', operator_password_hash, 'operator2@siberindo.local', 'Operator 2', 'operator', 1))
    
    # Add sample subscribers
    sample_subscribers = [
        ('621234567890123', '+6281234567890', 'John Doe', 'active', 'GSM', 'Jakarta', 'Siberindo', 150000.0),
        ('621234567890124', '+6281234567891', 'Jane Smith', 'active', 'GSM', 'Bandung', 'Siberindo', 200000.0),
        ('621234567890125', '+6281234567892', 'Budi Santoso', 'active', '4G', 'Surabaya', 'Siberindo', 175000.0),
        ('621234567890126', '+6281234567893', 'Siti Nurhaliza', 'active', 'GSM', 'Medan', 'Siberindo', 225000.0),
        ('621234567890127', '+6281234567894', 'Ahmad Rahman', 'suspended', 'GSM', 'Makassar', 'Siberindo', 0.0),
        ('621234567890128', '+6281234567895', 'Maria Garcia', 'active', 'LTE', 'Jakarta', 'Siberindo', 300000.0),
        ('621234567890129', '+6281234567896', 'Eko Prianto', 'inactive', 'GSM', 'Yogyakarta', 'Siberindo', 50000.0),
        ('621234567890130', '+6281234567897', 'Lisa Wang', 'active', '3G', 'Bogor', 'Siberindo', 125000.0),
    ]
    
    for imsi, msisdn, name, status, network_type, location, operator, balance in sample_subscribers:
        cursor.execute('''
        INSERT INTO subscribers (imsi, msisdn, name, status, network_type, location, operator, balance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (imsi, msisdn, name, status, network_type, location, operator, balance))
    
    # Add sample SMS history
    current_time = datetime.now()
    sample_sms = [
        ('621234567890123', '621234567890124', 'Hello, how are you?', 'standard', 'delivered', None),
        ('621234567890124', '621234567890123', 'Good, thanks!', 'standard', 'delivered', None),
        ('621234567890125', '621234567890126', 'Silent message test', 'silent', 'sent', None),
        ('621234567890126', '621234567890125', 'Flash message', 'flash', 'delivered', None),
        ('621234567890127', '621234567890128', 'Test message', 'standard', 'failed', 'SUBSCRIBER_SUSPENDED'),
    ]
    
    for from_sub, to_sub, message, msg_type, status, error in sample_sms:
        cursor.execute('''
        INSERT INTO sms_history (from_subscriber, to_subscriber, message_text, message_type, status, error_code)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (from_sub, to_sub, message, msg_type, status, error))
    
    # Add sample BTS scan results
    sample_scans = [
        ('GSM900', 890000, '510', '89', 'A1B2', 'C3D4', -80, 'excellent', 'PT Siberindo'),
        ('GSM1800', 1800000, '510', '89', 'A1B2', 'C3D5', -85, 'good', 'PT Siberindo'),
        ('GSM850', 850000, '510', '89', 'A1B3', 'C3D6', -95, 'fair', 'PT Siberindo'),
        ('GSM1900', 1900000, '510', '89', 'A1B4', 'C3D7', -105, 'poor', 'PT Siberindo'),
    ]
    
    for band, freq, mcc, mnc, lac, cell_id, signal, quality, operator in sample_scans:
        cursor.execute('''
        INSERT INTO bts_scans (band, frequency, mcc, mnc, lac, cell_id, signal_strength, signal_quality, operator_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (band, freq, mcc, mnc, lac, cell_id, signal, quality, operator))
    
    conn.commit()
    print("✓ Sample data seeded successfully")
    print(f"  - 1 admin user (admin/password123)")
    print(f"  - 2 operator users (operator1/operator123, operator2/operator123)")
    print(f"  - 8 sample subscribers")
    print(f"  - 5 sample SMS history entries")
    print(f"  - 4 sample BTS scan results")

def enable_pragmas(conn):
    """Enable performance pragmas"""
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode = WAL")
    cursor.execute("PRAGMA synchronous = NORMAL")
    cursor.execute("PRAGMA cache_size = -64000")  # 64MB
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    print("✓ Performance pragmas enabled")

def main():
    """Main initialization function"""
    print("=" * 60)
    print("SIBERINDO BTS GUI - Database Initialization")
    print("=" * 60)
    
    try:
        # Ensure directory
        ensure_directory()
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        print(f"✓ Database connection established: {DB_PATH}")
        
        # Enable pragmas
        enable_pragmas(conn)
        
        # Create schema
        create_schema(conn)
        
        # Seed data
        seed_data(conn)
        
        # Close connection
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database initialization completed successfully!")
        print("=" * 60)
        print("\nDatabase ready for use.")
        print(f"Location: {DB_PATH}")
        print("\nAdmin credentials:")
        print("  Username: admin")
        print("  Password: password123")
        print("\nOperator credentials:")
        print("  Username: operator1")
        print("  Password: operator123")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
