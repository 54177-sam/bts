import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager
import config

logger = logging.getLogger(__name__)


def get_db_connection():
    """Return an optimized sqlite3 connection with WAL and performance settings."""
    conn = sqlite3.connect(config.Config.DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    # Performance optimizations
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=10000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db_context():
    """Context manager for safe database connection handling with auto-commit."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.exception("Database error occurred")
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database with required tables and performance indexes."""
    try:
        with get_db_context() as conn:
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

            # Create performance indexes
            c.execute('''CREATE INDEX IF NOT EXISTS idx_sms_timestamp 
                         ON sms_history(timestamp DESC)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_subscribers_imsi 
                         ON subscribers(imsi)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_subscribers_msisdn 
                         ON subscribers(msisdn)''')

            # Insert sample data with ISO formatted timestamps
            c.execute('''INSERT OR IGNORE INTO subscribers (imsi, msisdn, status, last_seen) 
                         VALUES (?, ?, ?, ?)''',
                    ('001011234567890', '1234567890', 'active', datetime.now().isoformat()))

            c.execute('''INSERT OR IGNORE INTO subscribers (imsi, msisdn, status, last_seen) 
                         VALUES (?, ?, ?, ?)''',
                    ('001011234567891', '1234567891', 'active', datetime.now().isoformat()))

            logger.info("SIBERINDO database initialized successfully")

    except sqlite3.Error as e:
        logger.exception("Database initialization error")
        raise

def get_subscribers_count():
    """Get count of subscribers efficiently."""
    try:
        with get_db_context() as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM subscribers")
            count = c.fetchone()[0]
            return count
    except Exception:
        logger.exception("Error getting subscribers count")
        return 0


def get_subscribers(limit=100, offset=0):
    """Get list of subscribers with pagination."""
    try:
        with get_db_context() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM subscribers ORDER BY last_seen DESC LIMIT ? OFFSET ?",
                     (limit, offset))
            subscribers = c.fetchall()
            return subscribers
    except Exception:
        logger.exception("Error fetching subscribers")
        return []

def save_sms(sender, receiver, message, sms_type, status):
    """Save single SMS to database."""
    try:
        with get_db_context() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO sms_history (sender, receiver, message, type, status) VALUES (?, ?, ?, ?, ?)",
                      (sender, receiver, message, sms_type, status))
            return True
    except Exception:
        logger.exception("Error saving SMS")
        return False


def save_sms_batch(sms_list):
    """Save multiple SMS records efficiently using batch insert."""
    try:
        with get_db_context() as conn:
            c = conn.cursor()
            c.executemany(
                "INSERT INTO sms_history (sender, receiver, message, type, status) VALUES (?, ?, ?, ?, ?)",
                sms_list
            )
            return True
    except Exception:
        logger.exception("Error saving SMS batch")
        return False


def get_sms_history(limit=50, offset=0):
    """Get SMS history with pagination."""
    try:
        with get_db_context() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM sms_history ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                     (limit, offset))
            sms_list = c.fetchall()
            return sms_list
    except Exception:
        logger.exception("Error fetching SMS history")
        return []