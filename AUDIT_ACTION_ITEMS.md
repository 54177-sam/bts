# 🔧 AUDIT ACTION ITEMS & REMEDIATION GUIDE
## SIBERINDO BTS GUI - Step-by-Step Fix Instructions

---

## 🔴 CRITICAL FIXES (Do Today - ~90 minutes)

### ✅ Fix #1: Move JWT_SECRET to Environment (5 min)
**Status:** 🔴 CRITICAL - Security Vulnerability  
**File:** `modules/auth.py`  
**Current Location:** Line 35

**BEFORE:**
```python
JWT_SECRET = 'siberindo-bts-jwt-secret-2024-enhanced'
JWT_ALGORITHM = 'HS256'
```

**AFTER:**
```python
import os

JWT_SECRET = os.environ.get('JWT_SECRET') or 'dev-secret-only-for-development'
JWT_ALGORITHM = 'HS256'

# Add validation for production
if not os.environ.get('JWT_SECRET') and os.environ.get('FLASK_ENV') == 'production':
    raise ValueError("JWT_SECRET environment variable must be set in production!")
```

**Testing:**
```bash
# Test with env var set
JWT_SECRET=my-super-secret-key python app.py

# Test without (should warn)
python app.py  # Will show warning
```

---

### ✅ Fix #2: Move PASSWORD_SALT to Environment (5 min)
**Status:** 🔴 CRITICAL - Security Vulnerability  
**File:** `modules/auth.py`  
**Current Location:** Line 39

**BEFORE:**
```python
def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = "siberindo-salt-2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()
```

**AFTER:**
```python
def hash_password(password):
    """Hash password using SHA-256 with salt"""
    salt = os.environ.get('PASSWORD_SALT') or 'dev-salt-only-for-development'
    return hashlib.sha256((password + salt).encode()).hexdigest()
```

---

### ✅ Fix #3: Move FLASK_SECRET_KEY to Environment (5 min)
**Status:** 🔴 CRITICAL - Security Vulnerability  
**File:** `app.py`  
**Current Location:** Line 24

**BEFORE:**
```python
app.secret_key = app.config.get('SECRET_KEY', 'siberindo-bts-secret-key-2024-enhanced')
```

**AFTER:**
```python
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
if not app.secret_key and os.environ.get('FLASK_ENV') == 'production':
    raise ValueError("FLASK_SECRET_KEY environment variable must be set!")
if not app.secret_key:
    app.secret_key = 'dev-key-only-for-development'
```

---

### ✅ Fix #4: Remove Hardcoded Default Credentials (5 min)
**Status:** 🔴 CRITICAL - Security Vulnerability  
**File:** `app.py`  
**Current Location:** Line 127

**BEFORE:**
```python
print("=" * 50)
print("SIBERINDO BTS GSM Management System")
print("Version: 2.0.0 - Enhanced")
print(f"Access URL: http://{app.config.get('HOST','0.0.0.0')}:{app.config.get('PORT',5000)}")
print(f"Health check: http://{app.config.get('HOST','0.0.0.0')}:{app.config.get('PORT',5000)}/health")
print("Default login: admin / admin")  # ❌ REMOVE THIS
print("=" * 50)
```

**AFTER:**
```python
print("=" * 50)
print("SIBERINDO BTS GSM Management System")
print("Version: 2.0.0 - Enhanced")
print(f"Access URL: http://{app.config.get('HOST','0.0.0.0')}:{app.config.get('PORT',5000)}")
print(f"Health check: http://{app.config.get('HOST','0.0.0.0')}:{app.config.get('PORT',5000)}/health")
print("Default credentials in .env file (see .env.example)")
print("=" * 50)
```

---

### ✅ Fix #5: Fix Authentication Hash Mismatch (10 min)
**Status:** 🔴 CRITICAL - Authentication Broken  
**File:** `modules/auth.py`  
**Current Location:** Lines 11-31, 38-40

**PROBLEM:**
The hardcoded hash doesn't match what hash_password() produces because:
- Hardcoded hash: `sha256('admin')` 
- hash_password produces: `sha256('admin' + 'siberindo-salt-2024')`
- They don't match = login fails!

**SOLUTION:**
Compute correct hashes:

```python
#!/usr/bin/env python3
"""Helper to generate correct password hashes"""
import hashlib

def hash_password(password, salt="siberindo-salt-2024"):
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Generate correct hashes:
admin_hash = hash_password('admin')
operator_hash = hash_password('operator123')

print(f"admin: {admin_hash}")
print(f"operator1/2: {operator_hash}")
```

**Run it:**
```bash
python generate_hashes.py
```

**Then update auth.py:**
```python
users_db = {
    'admin': {
        'password': hash_password('admin'),  # ✓ Computed correctly
        'role': 'administrator',
        # ... rest of fields
    },
    'operator': {
        'password': hash_password('operator123'),  # ✓ Computed correctly
        'role': 'operator',
        # ... rest of fields
    }
}
```

---

### ✅ Fix #6: Create Missing Template - profile.html (10 min)
**Status:** 🔴 CRITICAL - 500 Error  
**File:** `templates/profile.html` (NEW FILE)

**Create this file:**
```html
{% extends "base.html" %}

{% block title %}User Profile - SIBERINDO BTS{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h1>User Profile</h1>
            <div class="card">
                <div class="card-body">
                    {% if profile %}
                    <div class="form-group">
                        <label><strong>Username:</strong></label>
                        <p>{{ profile.username }}</p>
                    </div>
                    
                    <div class="form-group">
                        <label><strong>Full Name:</strong></label>
                        <p>{{ profile.full_name }}</p>
                    </div>
                    
                    <div class="form-group">
                        <label><strong>Email:</strong></label>
                        <p>{{ profile.email }}</p>
                    </div>
                    
                    <div class="form-group">
                        <label><strong>Role:</strong></label>
                        <p>{{ profile.role }}</p>
                    </div>
                    
                    <div class="form-group">
                        <label><strong>Member Since:</strong></label>
                        <p>{{ profile.created_at }}</p>
                    </div>
                    
                    <a href="{{ url_for('auth.change_password') }}" class="btn btn-primary">Change Password</a>
                    {% else %}
                    <p>Profile not available</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Verify:** 
```bash
# Navigate to http://localhost:5000/auth/profile
# Should display profile without 500 error
```

---

### ✅ Fix #7: Create Missing Template - services.html (10 min)
**Status:** 🔴 CRITICAL - 500 Error  
**File:** `templates/services.html` (NEW FILE)

**Create this file:**
```html
{% extends "base.html" %}

{% block title %}Services Management - SIBERINDO BTS{% endblock %}

{% block content %}
<div class="container mt-5">
    <h1>Services Management</h1>
    
    <div class="alert alert-info">
        <strong>Note:</strong> Service management requires proper system integration.
    </div>
    
    <table class="table table-striped">
        <thead>
            <tr>
                <th>Service Name</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% if services %}
                {% for service in services %}
                <tr>
                    <td>{{ service.name }}</td>
                    <td>
                        <span class="badge {% if service.status == 'running' %}badge-success{% else %}badge-danger{% endif %}">
                            {{ service.status }}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="startService('{{ service.name }}')">Start</button>
                        <button class="btn btn-sm btn-warning" onclick="stopService('{{ service.name }}')">Stop</button>
                        <button class="btn btn-sm btn-info" onclick="restartService('{{ service.name }}')">Restart</button>
                    </td>
                </tr>
                {% endfor %}
            {% else %}
            <tr>
                <td colspan="3" class="text-center">No services available</td>
            </tr>
            {% endif %}
        </tbody>
    </table>
</div>

<script>
function startService(name) {
    // Implement service start
}

function stopService(name) {
    // Implement service stop
}

function restartService(name) {
    // Implement service restart
}
</script>
{% endblock %}
```

---

### ✅ Fix #8: Register Missing Blueprint (2 min)
**Status:** 🔴 CRITICAL - Routes Not Found  
**File:** `app.py`  
**Current Location:** Lines 55-87

**BEFORE:**
```python
blueprints_config = [
    {
        'module': 'modules.dashboard',
        'blueprint': 'dashboard_bp',
        'url_prefix': '/dashboard'
    },
    {
        'module': 'modules.auth', 
        'blueprint': 'auth_bp',
        'url_prefix': '/auth'
    },
    # ... other blueprints ...
    {
        'module': 'modules.bts_scanner',
        'blueprint': 'scanner_bp',
        'url_prefix': '/scanner'
    }
    # ❌ service_bp missing!
]
```

**AFTER:**
```python
blueprints_config = [
    {
        'module': 'modules.dashboard',
        'blueprint': 'dashboard_bp',
        'url_prefix': '/dashboard'
    },
    {
        'module': 'modules.auth', 
        'blueprint': 'auth_bp',
        'url_prefix': '/auth'
    },
    {
        'module': 'modules.subscribers',
        'blueprint': 'subscribers_bp', 
        'url_prefix': '/subscribers'
    },
    {
        'module': 'modules.sms_manager',
        'blueprint': 'sms_bp',
        'url_prefix': '/sms'
    },
    {
        'module': 'modules.bts_scanner',
        'blueprint': 'scanner_bp',
        'url_prefix': '/scanner'
    },
    {
        'module': 'modules.service_manager',  # ✅ ADD THIS
        'blueprint': 'service_bp',
        'url_prefix': '/services'
    }
]
```

---

### ✅ Fix #9: Move Users DB to Database (20 min)
**Status:** 🔴 CRITICAL - Credentials in Source  
**File:** Multiple changes

**Step 1: Update `modules/database.py`**

Add after init_database():
```python
def init_users():
    """Initialize default users in database if not exists"""
    conn = self.get_connection()
    try:
        # Create users table if not exists
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'operator',
                full_name TEXT,
                email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create default users only if none exist
        existing = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        if existing == 0:
            from modules.auth import hash_password
            
            # Create default admin and operators
            conn.execute('''
                INSERT INTO users (username, password, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', hash_password('admin'), 'administrator', 
                  'System Administrator', 'admin@siberindo.com'))
            
            conn.execute('''
                INSERT INTO users (username, password, role, full_name, email)
                VALUES (?, ?, ?, ?, ?)
            ''', ('operator1', hash_password('operator123'), 'operator',
                  'System Operator', 'operator@siberindo.com'))
        
        conn.commit()
    finally:
        conn.close()

def get_user(self, username):
    """Get user by username"""
    conn = self.get_connection()
    try:
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', 
            (username,)
        ).fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def verify_user_password(self, username, password):
    """Verify user credentials"""
    from modules.auth import hash_password
    user = self.get_user(username)
    if not user:
        return False
    return user['password'] == hash_password(password)
```

**Step 2: Update `modules/auth.py`**

Replace users_db and functions:
```python
from modules.database import BTSDatabase

# Remove hardcoded users_db
# Remove hash_password function

# Add:
db = BTSDatabase()

def hash_password(password):
    """Hash password - now imported from elsewhere or use bcrypt"""
    import hashlib
    import os
    salt = os.environ.get('PASSWORD_SALT', 'dev-salt')
    return hashlib.sha256((password + salt).encode()).hexdigest()

# Update login route to use database
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Use database instead of hardcoded users_db
        if db.verify_user_password(username, password):
            user = db.get_user(username)
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
```

---

## 🟠 HIGH PRIORITY FIXES (This Week - ~2 hours)

### Fix #10: Consolidate login_required Decorator (30 min)
**Status:** 🟠 HIGH - Code Duplication

**PLAN:**
1. Keep enhanced version from auth.py in helpers.py
2. Remove from auth.py
3. Import in all modules

**File:** `modules/helpers.py`

**BEFORE:**
```python
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```

**AFTER:**
```python
from functools import wraps
from flask import session, redirect, url_for, request
import jwt

JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret')
JWT_ALGORITHM = 'HS256'

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
            
            user_role = session.get('role')
            if user_role not in roles:
                from flask import flash, jsonify
                flash('Access denied: Insufficient permissions', 'danger')
                return redirect(url_for('dashboard.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

**Then update `modules/auth.py`:**
- Remove login_required and role_required definitions
- Import: `from modules.helpers import login_required, role_required`
- Remove JWT functions (move to helpers or keep in auth)

**Verify all modules import correctly:**
```bash
grep -r "from modules.helpers import login_required" modules/
# Should appear in: sms_manager.py, subscribers.py, bts_scanner.py
```

---

### Fix #11: Add Input Validation to Critical Routes (45 min)
**Status:** 🟠 HIGH - Security

**Example fix for `modules/sms_manager.py`:**

```python
from modules.validators import DataValidator

@sms_bp.route('/send_sms', methods=['GET', 'POST'])
@login_required
def send_sms():
    if request.method == 'POST':
        sender = request.form.get('sender', '').strip()
        receiver = request.form.get('receiver', '').strip()
        message = request.form.get('message', '').strip()
        
        # ADD VALIDATION
        validator = DataValidator()
        
        # Validate MSISDN format
        if not validator.validate_msisdn(receiver):
            flash('Invalid receiver phone number format', 'danger')
            return render_template('send_sms.html', error='Invalid receiver')
        
        if not validator.validate_msisdn(sender):
            flash('Invalid sender phone number format', 'danger')
            return render_template('send_sms.html', error='Invalid sender')
        
        if not validator.validate_text(message, min_length=1, max_length=160):
            flash('Message must be 1-160 characters', 'danger')
            return render_template('send_sms.html', error='Invalid message')
        
        # Now safe to process
        try:
            sms_manager = SMSManager()
            success = sms_manager.send_sms(sender, receiver, message)
            if success:
                flash('SMS sent successfully!', 'success')
            else:
                flash('Failed to send SMS', 'danger')
        except Exception as e:
            logger.exception("Error sending SMS")
            flash('Error sending SMS', 'danger')
        
        return redirect(url_for('sms.sms_history'))
```

---

### Fix #12: Fix N+1 Query Problem (45 min)
**Status:** 🟠 HIGH - Performance

**Location:** `modules/subscribers.py`

**BEFORE (N+1 Problem):**
```python
@subscribers_bp.route('/subscribers')
@login_required
def subscribers():
    subs = db_get_subscribers(limit=100)  # Query 1
    
    for sub in subs:
        # This query runs for EACH subscriber = N queries!
        events = db.execute(
            'SELECT * FROM network_events WHERE imsi = ?',
            (sub['imsi'],)
        ).fetchall()
        sub['events'] = events
    
    return render_template('subscribers.html', subscribers=subs)
```

**AFTER (Fixed):**
```python
@subscribers_bp.route('/subscribers')
@login_required
def subscribers():
    # Single optimized query with JOIN
    query = '''
        SELECT 
            s.*,
            COUNT(ne.id) as event_count
        FROM subscribers s
        LEFT JOIN network_events ne ON s.imsi = ne.imsi
        GROUP BY s.id
        ORDER BY s.last_seen DESC
        LIMIT 100
    '''
    
    conn = get_connection()
    subs = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('subscribers.html', subscribers=subs)
```

---

## 🟡 MEDIUM PRIORITY FIXES (Next Week - ~3 hours)

### Fix #13: Add CSRF Protection (45 min)
**Status:** 🟡 MEDIUM - Security

**Install:** 
```bash
pip install Flask-WTF
```

**Update `app.py`:**
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

**Update templates:**
```html
<!-- Add to all forms -->
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

---

### Fix #14: Implement Rate Limiting (30 min)
**Status:** 🟡 MEDIUM - Security

**Install:**
```bash
pip install Flask-Limiter
```

**Update `app.py`:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Add to login route
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    # ... existing code
```

---

## ✅ TESTING CHECKLIST

After implementing all fixes, verify:

**Security Tests:**
- [ ] Login works with correct credentials
- [ ] Login fails with wrong credentials
- [ ] Profile page loads without 500 error
- [ ] Services page loads without 500 error
- [ ] No secrets in logs or error messages
- [ ] CSRF tokens validate on POST
- [ ] Rate limiting blocks after 5 login attempts

**Functional Tests:**
- [ ] All 28 existing tests still pass
- [ ] `pytest tests/test_suite.py -v` shows 100%
- [ ] No 404 errors for valid routes
- [ ] SMS sending works
- [ ] Subscriber list loads

**Code Quality:**
- [ ] No hardcoded secrets remaining
- [ ] No duplicate decorators
- [ ] All imports at module level
- [ ] Consistent error handling

---

## 🚀 DEPLOYMENT STEPS

1. **Local Testing:**
   ```bash
   # Set environment variables
   export FLASK_SECRET_KEY="generated-random-key"
   export JWT_SECRET="generated-random-key"
   export PASSWORD_SALT="generated-random-salt"
   
   # Run tests
   python -m pytest tests/ -v
   
   # Start app
   python app.py
   
   # Verify at http://localhost:5000
   ```

2. **Staging Deployment:**
   ```bash
   # Deploy to staging
   # Set .env with production values
   # Run tests again
   ```

3. **Production Deployment:**
   ```bash
   # Set all environment variables on production server
   # Run migrations if any
   # Start with production WSGI server (gunicorn)
   ```

---

## 📊 PROGRESS TRACKING

- [ ] Fixes 1-5: Security (25 min) ✅ **CRITICAL**
- [ ] Fixes 6-7: Templates (20 min) ✅ **CRITICAL**
- [ ] Fix 8: Blueprint (2 min) ✅ **CRITICAL**
- [ ] Fix 9: User DB (20 min) ✅ **CRITICAL**
- [ ] Fix 10: Decorators (30 min) 🟠 **HIGH**
- [ ] Fix 11: Validation (45 min) 🟠 **HIGH**
- [ ] Fix 12: N+1 Queries (45 min) 🟠 **HIGH**
- [ ] Fixes 13-14: Security hardening (75 min) 🟡 **MEDIUM**

**Total Time: 5-8 hours for production-ready application**

---

End of Action Items Guide
