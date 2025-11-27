"""API middleware dan utilities"""
from flask import request, jsonify
from functools import wraps
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class APIResponse:
    """Standardized API response format"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200, **kwargs):
        """Generate success response"""
        response = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message, status_code=400, error_code=None, **kwargs):
        """Generate error response"""
        response = {
            'success': False,
            'message': message,
            'error_code': error_code or status_code,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        return jsonify(response), status_code
    
    @staticmethod
    def paginated(items, total, page, limit, message="Success"):
        """Generate paginated response"""
        response = {
            'success': True,
            'message': message,
            'data': items,
            'pagination': {
                'total': total,
                'page': page,
                'limit': limit,
                'total_pages': (total + limit - 1) // limit
            },
            'timestamp': datetime.now().isoformat()
        }
        return jsonify(response), 200


def log_request(f):
    """Decorator to log API requests"""
    @wraps(f)
    def decorated(*args, **kwargs):
        start_time = time.time()
        
        # Log request
        logger.info(f"{request.method} {request.path} - IP: {request.remote_addr}")
        
        try:
            result = f(*args, **kwargs)
            
            # Log response
            duration = time.time() - start_time
            if isinstance(result, tuple):
                status_code = result[1] if len(result) > 1 else 200
            else:
                status_code = 200
            
            logger.info(f"Response: {status_code} - Duration: {duration:.2f}s")
            
            return result
        
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error in {request.path} after {duration:.2f}s: {e}")
            raise
    
    return decorated


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        # Simple API key validation (should be more sophisticated in production)
        if not api_key or not api_key.startswith('sk-'):
            return APIResponse.error("Invalid or missing API key", 401, "AUTH_FAILED")
        
        return f(*args, **kwargs)
    
    return decorated


def require_content_type(content_type):
    """Decorator to require specific content type"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.content_type and content_type not in request.content_type:
                return APIResponse.error(
                    f"Content-Type must be {content_type}",
                    400,
                    "INVALID_CONTENT_TYPE"
                )
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator


class RequestContext:
    """Context for tracking request metadata"""
    
    def __init__(self):
        self.request_id = None
        self.user_id = None
        self.start_time = None
        self.data = {}
    
    def set_user(self, user_id):
        """Set user ID"""
        self.user_id = user_id
    
    def set_data(self, key, value):
        """Store arbitrary data"""
        self.data[key] = value
    
    def get_data(self, key, default=None):
        """Retrieve stored data"""
        return self.data.get(key, default)
    
    def get_duration(self):
        """Get request duration"""
        if self.start_time:
            return time.time() - self.start_time
        return None


# Thread-local context
_request_context = None

def get_request_context():
    """Get current request context"""
    global _request_context
    return _request_context

def set_request_context(context):
    """Set request context"""
    global _request_context
    _request_context = context


def init_request_context():
    """Initialize request context before request"""
    context = RequestContext()
    context.start_time = time.time()
    set_request_context(context)


def cleanup_request_context():
    """Cleanup request context after request"""
    set_request_context(None)
