"""Data validation and sanitization utilities"""
import re
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation exception"""
    pass


class DataValidator:
    """Comprehensive data validation"""
    
    # IMSI format: 15 digits
    IMSI_PATTERN = re.compile(r'^\d{15}$')
    
    # MSISDN format: 10-15 digits
    MSISDN_PATTERN = re.compile(r'^\d{10,15}$')
    
    # Email format
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Username format: alphanumeric + underscore, 3-20 chars
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    
    @staticmethod
    def validate_imsi(imsi):
        """Validate IMSI format"""
        if not isinstance(imsi, str):
            raise ValidationError("IMSI must be string")
        
        if not DataValidator.IMSI_PATTERN.match(imsi):
            raise ValidationError("IMSI must be 15 digits")
        
        return imsi
    
    @staticmethod
    def validate_msisdn(msisdn):
        """Validate MSISDN format"""
        if not isinstance(msisdn, str):
            raise ValidationError("MSISDN must be string")
        
        if not DataValidator.MSISDN_PATTERN.match(msisdn):
            raise ValidationError("MSISDN must be 10-15 digits")
        
        return msisdn
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not isinstance(email, str):
            raise ValidationError("Email must be string")
        
        if not DataValidator.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format")
        
        return email.lower()
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not isinstance(username, str):
            raise ValidationError("Username must be string")
        
        if not DataValidator.USERNAME_PATTERN.match(username):
            raise ValidationError("Username must be 3-20 alphanumeric characters")
        
        return username.lower()
    
    @staticmethod
    def validate_string(value, min_len=1, max_len=500, allow_empty=False):
        """Validate string with length constraints"""
        if not isinstance(value, str):
            raise ValidationError("Value must be string")
        
        if len(value) == 0 and not allow_empty:
            raise ValidationError(f"Value cannot be empty")
        
        if len(value) < min_len:
            raise ValidationError(f"Value too short (minimum {min_len} characters)")
        
        if len(value) > max_len:
            raise ValidationError(f"Value too long (maximum {max_len} characters)")
        
        return value.strip()
    
    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        """Validate integer with range constraints"""
        try:
            val = int(value)
        except (ValueError, TypeError):
            raise ValidationError("Value must be integer")
        
        if min_val is not None and val < min_val:
            raise ValidationError(f"Value must be >= {min_val}")
        
        if max_val is not None and val > max_val:
            raise ValidationError(f"Value must be <= {max_val}")
        
        return val
    
    @staticmethod
    def sanitize_string(value):
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Strip whitespace
        value = value.strip()
        
        return value


class RateLimiter:
    """Rate limiting utility"""
    
    _requests = {}
    
    @classmethod
    def check_rate_limit(cls, key, max_requests=100, window=60):
        """Check if request exceeds rate limit"""
        import time
        
        now = time.time()
        
        if key not in cls._requests:
            cls._requests[key] = []
        
        # Remove old requests outside window
        cls._requests[key] = [req_time for req_time in cls._requests[key] 
                             if now - req_time < window]
        
        if len(cls._requests[key]) >= max_requests:
            return False
        
        cls._requests[key].append(now)
        return True


def validate_request_json(schema=None):
    """Decorator to validate JSON requests"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                if not request.is_json:
                    return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
                
                data = request.get_json()
                
                if data is None:
                    return jsonify({'success': False, 'error': 'Invalid JSON'}), 400
                
                if schema:
                    for field, validator in schema.items():
                        if field not in data:
                            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
                        
                        try:
                            data[field] = validator(data[field])
                        except ValidationError as e:
                            return jsonify({'success': False, 'error': str(e)}), 400
                
                return f(*args, **kwargs)
            
            except Exception as e:
                logger.exception("Validation error")
                return jsonify({'success': False, 'error': 'Validation failed'}), 400
        
        return decorated
    return decorator


def validate_request_form(schema=None):
    """Decorator to validate form requests"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                if schema:
                    for field, validator in schema.items():
                        value = request.form.get(field)
                        
                        if value is None:
                            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
                        
                        try:
                            validator(value)
                        except ValidationError as e:
                            return jsonify({'success': False, 'error': str(e)}), 400
                
                return f(*args, **kwargs)
            
            except Exception as e:
                logger.exception("Form validation error")
                return jsonify({'success': False, 'error': 'Validation failed'}), 400
        
        return decorated
    return decorator
