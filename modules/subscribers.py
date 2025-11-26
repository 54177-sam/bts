from flask import Blueprint, render_template, session
from functools import wraps

subscribers_bp = Blueprint('subscribers', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@subscribers_bp.route('/subscribers')
@login_required
def subscribers():
    try:
        from modules.database import get_subscribers
        subscribers_list = get_subscribers()
        return render_template('subscribers.html', 
                             subscribers=subscribers_list,
                             company='SIBERINDO')
    except Exception as e:
        return f"Error loading subscribers: {e}", 500