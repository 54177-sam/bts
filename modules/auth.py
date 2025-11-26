from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
import os
import jwt
from datetime import datetime, timedelta
import secrets

auth_bp = Blueprint('auth', __name__)

# Enhanced user database with roles and permissions
users_db = {
    'admin': {
        'password': '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',  # sha256('admin')
        'role': 'administrator',
        'full_name': 'System Administrator',
        'email': 'admin@siberindo.com',
        'created_at': '2024-01-01 00:00:00',
        'last_login': None,
        'is_active': True,
        'permissions': ['all']
    },
    'operator': {
        'password': '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',  # sha256('admin')
        'role': 'operator', 
        'full_name': 'System Operator',
        'email': 'operator@siberindo.com',
        'created_at': '2024-01-01 00:00:00',
        'last_login': None,
        'is_active': True,
        'permissions': ['dashboard', 'subscribers', 'sms_manager']
    }
}

# JWT secret key
JWT_SECRET = 'siberindo-bts-jwt-secret-2024-enhanced'
JWT_ALGORITHM = 'HS256'

def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = "siberindo-salt-2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_token(username):
    """Generate JWT token for authenticated user"""
    payload = {
        'username': username,
        'role': users_db[username]['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """Enhanced login required decorator with JWT verification"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session first
        if not session.get('logged_in'):
            # Check for JWT token
            token = request.headers.get('Authorization')
            if token and token.startswith('Bearer '):
                token = token[7:]
                payload = verify_token(token)
                if payload:
                    session['logged_in'] = True
                    session['username'] = payload['username']
                    session['role'] = payload['role']
                    return f(*args, **kwargs)
            
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """Role-based access control decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('auth.login'))
            
            if session.get('role') not in roles and 'all' not in users_db.get(session['username'], {}).get('permissions', []):
                flash('Access denied: Insufficient permissions', 'danger')
                return redirect(url_for('dashboard.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Enhanced login page with security features"""
    # Redirect if already logged in
    if session.get('logged_in'):
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        next_page = request.form.get('next') or url_for('dashboard.dashboard')
        
        # Basic validation
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html', username=username, next=next_page)
        
        # Check user credentials
        user = users_db.get(username)
        if user and user['is_active'] and user['password'] == hash_password(password):
            # Update last login
            user['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Set session
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            session['permissions'] = user.get('permissions', [])
            
            # Generate JWT token
            session['token'] = generate_token(username)
            
            # Set session permanence
            if remember_me:
                session.permanent = True
            else:
                session.permanent = False
            
            # Log login activity
            log_security_event('login_success', username, f'User {username} logged in successfully')
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(next_page)
        else:
            # Log failed attempt
            log_security_event('login_failed', username, f'Failed login attempt for user {username}')
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', next=request.args.get('next', ''))

@auth_bp.route('/logout')
def logout():
    """Enhanced logout with security logging"""
    username = session.get('username')
    
    # Log logout activity
    if username:
        log_security_event('logout', username, f'User {username} logged out')
    
    # Clear session
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    username = session.get('username')
    user = users_db.get(username, {})
    
    profile_data = {
        'username': username,
        'full_name': user.get('full_name', ''),
        'email': user.get('email', ''),
        'role': user.get('role', ''),
        'last_login': user.get('last_login', 'Never'),
        'created_at': user.get('created_at', 'Unknown')
    }
    
    return render_template('profile.html', profile=profile_data)

@auth_bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """API endpoint for password change"""
    username = session.get('username')
    data = request.get_json()
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    # Validation
    if not all([current_password, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'})
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
    
    # Verify current password
    user = users_db.get(username)
    if not user or user['password'] != hash_password(current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    # Update password
    user['password'] = hash_password(new_password)
    
    # Log password change
    log_security_event('password_change', username, 'Password changed successfully')
    
    return jsonify({'success': True, 'message': 'Password updated successfully'})

@auth_bp.route('/api/session/check')
def check_session():
    """API endpoint to check session status"""
    if session.get('logged_in'):
        return jsonify({
            'logged_in': True,
            'username': session.get('username'),
            'role': session.get('role'),
            'full_name': session.get('full_name')
        })
    else:
        return jsonify({'logged_in': False})

def log_security_event(event_type, username, description):
    """Log security-related events"""
    from modules.database import log_system_event
    log_system_event('SECURITY', event_type.upper(), f'{username}: {description}')

# API Authentication endpoints
@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for programmatic login"""
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    user = users_db.get(username)
    if user and user['is_active'] and user['password'] == hash_password(password):
        token = generate_token(username)
        
        # Update last login
        user['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_security_event('api_login_success', username, 'API login successful')
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'username': username,
                'role': user['role'],
                'full_name': user['full_name']
            }
        })
    else:
        log_security_event('api_login_failed', username, 'API login failed')
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/api/auth/verify')
def api_verify():
    """API endpoint to verify token"""
    token = request.headers.get('Authorization', '')
    if token.startswith('Bearer '):
        token = token[7:]
    
    payload = verify_token(token)
    if payload:
        return jsonify({'valid': True, 'user': payload})
    else:
        return jsonify({'valid': False}), 401