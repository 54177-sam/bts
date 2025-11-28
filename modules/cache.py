"""
Centralized caching utilities for SIBERINDO BTS GUI
Provides common decorators and cache management
"""

from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


def cache_with_timeout(timeout):
    """
    Decorator to cache function results with timeout.
    
    Args:
        timeout (int): Cache timeout in seconds
        
    Returns:
        decorator: Function decorator for caching
        
    Example:
        @cache_with_timeout(30)
        def expensive_operation(param1, param2):
            return result
    """
    def decorator(f):
        cache = {}
        cache_time = {}
        
        @wraps(f)
        def decorated(*args, **kwargs):
            # Create cache key from function arguments
            cache_key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            
            # Return cached result if not expired
            if cache_key in cache and (now - cache_time[cache_key]) < timeout:
                return cache[cache_key]
            
            # Compute new result and cache it
            result = f(*args, **kwargs)
            cache[cache_key] = result
            cache_time[cache_key] = now
            
            return result
        
        return decorated
    return decorator


class CacheManager:
    """Centralized cache management for all modules"""
    
    # Cache timeout constants (in seconds)
    TIMEOUT_SMS_HISTORY = 15      # 15 seconds for SMS history
    TIMEOUT_SUBSCRIBERS = 30       # 30 seconds for subscriber list
    TIMEOUT_SYSTEM_STATS = 10      # 10 seconds for system statistics
    TIMEOUT_SERVICE_STATUS = 5     # 5 seconds for service status
    
    @staticmethod
    def get_timeout(cache_type):
        """Get timeout for a specific cache type"""
        timeouts = {
            'sms_history': CacheManager.TIMEOUT_SMS_HISTORY,
            'subscribers': CacheManager.TIMEOUT_SUBSCRIBERS,
            'system_stats': CacheManager.TIMEOUT_SYSTEM_STATS,
            'service_status': CacheManager.TIMEOUT_SERVICE_STATUS,
        }
        return timeouts.get(cache_type, 30)
    
    @staticmethod
    def clear_all_caches():
        """Clear all application caches (call on critical updates)"""
        logger.info("Clearing all application caches")
        # Decorator instances maintain their own caches,
        # this is a placeholder for future global cache management
        pass
