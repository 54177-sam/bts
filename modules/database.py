import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_db_connection():
    return sqlite3.connect('siberindo_bts.db')

def init_db():
    """Initialize database with required tables"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Subscribers table
        c.execute('''CREATE TABLE IF NOT EXISTS subscribers
                     (id INTEGER PRIMARY KEY, 
                      imsi TEXT UNIQUE, 
                      msisdn TEXT, 
                      status TEXT DEFAULT 'active',
                      last_seen TIMESTAMP,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # SMS history table
        c.execute('''CREATE TABLE IF NOT EXISTS sms_history
                     (id INTEGER PRIMARY KEY, 
                      sender TEXT, 
                      receiver TEXT, 
                      message TEXT, 
                      type TEXT,
                      status TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Insert sample data
        c.execute('''INSERT OR IGNORE INTO subscribers (imsi, msisdn, status, last_seen) 
                     VALUES (?, ?, ?, ?)''',
                ('001011234567890', '1234567890', 'active', datetime.now()))
        
        c.execute('''INSERT OR IGNORE INTO subscribers (imsi, msisdn, status, last_seen) 
                     VALUES (?, ?, ?, ?)''',
                ('001011234567891', '1234567891', 'active', datetime.now()))
        
        conn.commit()
        print("SIBERINDO database initialized successfully")
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

def get_subscribers_count():
    """Get count of subscribers"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM subscribers")
        count = c.fetchone()[0]
        return count
    except:
        return 2  # Return 2 for sample data
    finally:
        conn.close()

def get_subscribers():
    """Get list of subscribers"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM subscribers ORDER BY last_seen DESC")
        subscribers = c.fetchall()
        return subscribers
    except:
        return []
    finally:
        conn.close()

def save_sms(sender, receiver, message, sms_type, status):
    """Save SMS to database"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO sms_history (sender, receiver, message, type, status) VALUES (?, ?, ?, ?, ?)",
                  (sender, receiver, message, sms_type, status))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_sms_history():
    """Get SMS history"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM sms_history ORDER BY timestamp DESC LIMIT 50")
        sms_list = c.fetchall()
        return sms_list
    except:
        return []
    finally:
        conn.close()