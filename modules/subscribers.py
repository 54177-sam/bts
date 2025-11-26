from flask import Blueprint, render_template, session
from modules.helpers import login_required

subscribers_bp = Blueprint('subscribers', __name__)

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