import sqlite3
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BTSDatabase:
    """Enhanced database management for BTS system"""
    
    def __init__(self, db_path='data/bts_database.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Create a database connection"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = self.get_connection()
        
        try:
            # Subscribers table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS subscribers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imsi TEXT UNIQUE NOT NULL,
                    msisdn TEXT,
                    name TEXT,
                    location TEXT,
                    status TEXT DEFAULT 'active',
                    network TEXT DEFAULT 'GSM',
                    last_seen DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # SMS messages table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sms_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    imsi TEXT NOT NULL,
                    msisdn TEXT,
                    message TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    status TEXT DEFAULT 'sent',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    delivered_at DATETIME
                )
            ''')
            
            # System logs table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    module TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # BTS configuration table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS bts_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mcc TEXT NOT NULL DEFAULT '001',
                    mnc TEXT NOT NULL DEFAULT '01',
                    lac TEXT NOT NULL DEFAULT '1001',
                    cell_id TEXT NOT NULL DEFAULT '1',
                    arfcn TEXT NOT NULL DEFAULT '975',
                    power TEXT NOT NULL DEFAULT '10',
                    band TEXT NOT NULL DEFAULT 'GSM-900',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Network events table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS network_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    imsi TEXT,
                    cell_id TEXT,
                    lac TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default BTS configuration if not exists
            conn.execute('''
                INSERT OR IGNORE INTO bts_config (mcc, mnc, lac, cell_id, arfcn, power, band)
                VALUES ('001', '01', '1001', '1', '975', '10', 'GSM-900')
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    # Subscribers management
    def add_subscriber(self, imsi, msisdn=None, name=None, location=None, network='GSM'):
        """Add a new subscriber"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO subscribers (imsi, msisdn, name, location, network, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (imsi, msisdn, name, location, network, datetime.now()))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_subscribers(self, status=None, network=None, limit=100):
        """Get subscribers with filtering"""
        conn = self.get_connection()
        try:
            query = 'SELECT * FROM subscribers WHERE 1=1'
            params = []
            
            if status and status != 'all':
                query += ' AND status = ?'
                params.append(status)
            
            if network and network != 'all':
                query += ' AND network = ?'
                params.append(network)
            
            query += ' ORDER BY last_seen DESC LIMIT ?'
            params.append(limit)
            
            subscribers = conn.execute(query, params).fetchall()
            return [dict(sub) for sub in subscribers]
        finally:
            conn.close()
    
    def get_subscribers_count(self):
        """Get total number of subscribers"""
        conn = self.get_connection()
        try:
            count = conn.execute('SELECT COUNT(*) FROM subscribers').fetchone()[0]
            return count
        finally:
            conn.close()
    
    def update_subscriber_status(self, imsi, status):
        """Update subscriber status"""
        conn = self.get_connection()
        try:
            conn.execute('''
                UPDATE subscribers 
                SET status = ?, last_seen = ?
                WHERE imsi = ?
            ''', (status, datetime.now(), imsi))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
    
    # SMS management
    def add_sms_message(self, imsi, message, direction, msisdn=None, status='sent'):
        """Add SMS message to database"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO sms_messages (imsi, msisdn, message, direction, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (imsi, msisdn, message, direction, status))
            conn.commit()
            return True
        finally:
            conn.close()
    
    def get_sms_history(self, direction=None, limit=100):
        """Get SMS history with filtering"""
        conn = self.get_connection()
        try:
            query = 'SELECT * FROM sms_messages WHERE 1=1'
            params = []
            
            if direction and direction != 'all':
                query += ' AND direction = ?'
                params.append(direction)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            messages = conn.execute(query, params).fetchall()
            return [dict(msg) for msg in messages]
        finally:
            conn.close()
    
    # System logging
    def log_system_event(self, level, module, message):
        """Log system event to database"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO system_logs (level, module, message)
                VALUES (?, ?, ?)
            ''', (level, module, message))
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging system event: {e}")
        finally:
            conn.close()
    
    def get_system_logs(self, level=None, module=None, limit=100):
        """Get system logs with filtering"""
        conn = self.get_connection()
        try:
            query = 'SELECT * FROM system_logs WHERE 1=1'
            params = []
            
            if level and level != 'all':
                query += ' AND level = ?'
                params.append(level)
            
            if module and module != 'all':
                query += ' AND module = ?'
                params.append(module)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            logs = conn.execute(query, params).fetchall()
            return [dict(log) for log in logs]
        finally:
            conn.close()
    
    # BTS Configuration
    def get_bts_config(self):
        """Get current BTS configuration"""
        conn = self.get_connection()
        try:
            config = conn.execute('SELECT * FROM bts_config ORDER BY id DESC LIMIT 1').fetchone()
            return dict(config) if config else None
        finally:
            conn.close()
    
    def update_bts_config(self, mcc, mnc, lac, cell_id, arfcn, power, band):
        """Update BTS configuration"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO bts_config (mcc, mnc, lac, cell_id, arfcn, power, band)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (mcc, mnc, lac, cell_id, arfcn, power, band))
            conn.commit()
            return True
        finally:
            conn.close()
    
    # Network events
    def log_network_event(self, event_type, imsi=None, cell_id=None, lac=None, details=None):
        """Log network event"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO network_events (event_type, imsi, cell_id, lac, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (event_type, imsi, cell_id, lac, json.dumps(details) if details else None))
            conn.commit()
        finally:
            conn.close()
    
    def get_network_events(self, event_type=None, limit=100):
        """Get network events with filtering"""
        conn = self.get_connection()
        try:
            query = 'SELECT * FROM network_events WHERE 1=1'
            params = []
            
            if event_type and event_type != 'all':
                query += ' AND event_type = ?'
                params.append(event_type)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            events = conn.execute(query, params).fetchall()
            return [dict(event) for event in events]
        finally:
            conn.close()

# Global database instance
db = BTSDatabase()

# Convenience functions for backward compatibility & new API
def init_db():
    """Initialize database (calls constructor which already does this)"""
    return db.init_database()

def get_db_connection():
    """Get a database connection"""
    return db.get_connection()

def get_subscribers_count():
    """Get count of subscribers"""
    return db.get_subscribers_count()

def get_subscribers(limit=100, offset=0):
    """Get subscribers with pagination"""
    conn = db.get_connection()
    try:
        query = 'SELECT * FROM subscribers ORDER BY last_seen DESC LIMIT ? OFFSET ?'
        rows = conn.execute(query, (limit, offset)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def save_sms(sender, receiver, message, sms_type, status='sent'):
    """Save single SMS message"""
    return db.add_sms_message(sender, receiver, message, 'sent', sms_type)

def save_sms_batch(sms_list):
    """Save multiple SMS messages in batch"""
    conn = db.get_connection()
    try:
        for sms in sms_list:
            sender, receiver, message, sms_type, status = sms
            conn.execute('''
                INSERT INTO sms_messages (imsi, msisdn, message, direction, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender, receiver, message, 'sent', status))
        conn.commit()
        return True
    except Exception as e:
        logger.exception(f"Error in batch SMS: {e}")
        return False
    finally:
        conn.close()

def get_sms_history(limit=50, offset=0):
    """Get SMS history with pagination"""
    return db.get_sms_history(limit=limit)

def log_system_event(level, module, message):
    """Log system event"""
    db.log_system_event(level, module, message)

def get_bts_config():
    """Get BTS configuration"""
    return db.get_bts_config()

def add_subscriber(imsi, msisdn=None, name=None, location=None, network='GSM'):
    """Add new subscriber"""
    return db.add_subscriber(imsi, msisdn, name, location, network)