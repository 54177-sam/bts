from flask import Blueprint, render_template, request, jsonify
from modules.helpers import login_required
from modules.database import save_sms, save_sms_batch, get_sms_history as db_get_sms_history
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)
sms_bp = Blueprint('sms', __name__)

# Cache timeout configuration
CACHE_TIMEOUT_SMS = 15  # 15 seconds for SMS history


def cache_with_timeout(timeout):
    """Decorator to cache function results with timeout."""
    def decorator(f):
        cache = {}
        cache_time = {}
        
        @wraps(f)
        def decorated(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            
            if key in cache and (now - cache_time[key]) < timeout:
                return cache[key]
            
            result = f(*args, **kwargs)
            cache[key] = result
            cache_time[key] = now
            return result
        
        return decorated
    return decorator


class SMSManager:
    """Optimized SMS operations with caching and batch processing."""
    
    @staticmethod
    def send_sms_batch(sms_list):
        """Send batch SMS with efficient database operations."""
        try:
            return save_sms_batch(sms_list)
        except Exception as e:
            logger.exception("Error sending SMS batch")
            return False
    
    @staticmethod
    def send_sms(sender, receiver, message, sms_type='STANDARD'):
        """Send single SMS."""
        try:
            return save_sms(sender, receiver, message, sms_type, 'SENT')
        except Exception as e:
            logger.exception("Error sending SMS")
            return False
    
    @staticmethod
    @cache_with_timeout(CACHE_TIMEOUT_SMS)
    def get_sms_history(limit=50, offset=0):
        """Get cached SMS history with pagination."""
        try:
            return db_get_sms_history(limit=limit, offset=offset)
        except Exception as e:
            logger.exception("Error fetching SMS history")
            return []
    
    @staticmethod
    def get_sms_count():
        """Get total SMS count."""
        try:
            history = SMSManager.get_sms_history(limit=10000)
            return len(history) if history else 0
        except Exception:
            logger.exception("Error getting SMS count")
            return 0


@sms_bp.route('/send_silent_sms', methods=['GET', 'POST'])
@login_required
def send_silent_sms():
    """Send silent SMS form and handler."""
    if request.method == 'POST':
        sender = request.form.get('sender', '').strip()
        receiver = request.form.get('receiver', '').strip()
        message = request.form.get('message', '').strip()
        
        if not all([sender, receiver, message]):
            return render_template('send_silent_sms.html', 
                                 error='Please fill all fields!',
                                 company='SIBERINDO')
        
        try:
            sms_manager = SMSManager()
            success = sms_manager.send_sms(sender, receiver, message, 'SILENT')
            
            if success:
                return render_template('send_silent_sms.html',
                                     success='Silent SMS sent successfully!',
                                     company='SIBERINDO')
            else:
                return render_template('send_silent_sms.html',
                                     error='Failed to send SMS',
                                     company='SIBERINDO')
        except Exception as e:
            logger.exception("Error in send_silent_sms")
            return render_template('send_silent_sms.html',
                                 error=f'Error: {str(e)}',
                                 company='SIBERINDO'), 500
    
    return render_template('send_silent_sms.html', company='SIBERINDO')


@sms_bp.route('/send_sms', methods=['GET', 'POST'])
@login_required
def send_sms():
    """Send standard SMS form."""
    if request.method == 'POST':
        sender = request.form.get('sender', '').strip()
        receiver = request.form.get('receiver', '').strip()
        message = request.form.get('message', '').strip()
        
        if not all([sender, receiver, message]):
            return render_template('send_sms.html',
                                 error='Please fill all fields!',
                                 company='SIBERINDO')
        
        try:
            sms_manager = SMSManager()
            success = sms_manager.send_sms(sender, receiver, message, 'STANDARD')
            
            if success:
                return render_template('send_sms.html',
                                     success='SMS sent successfully!',
                                     company='SIBERINDO')
            else:
                return render_template('send_sms.html',
                                     error='Failed to send SMS',
                                     company='SIBERINDO')
        except Exception as e:
            logger.exception("Error in send_sms")
            return render_template('send_sms.html',
                                 error=f'Error: {str(e)}',
                                 company='SIBERINDO'), 500
    
    return render_template('send_sms.html', company='SIBERINDO')


@sms_bp.route('/sms_history', methods=['GET'])
@login_required
def sms_history():
    """SMS history view with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = (page - 1) * limit
        
        sms_manager = SMSManager()
        sms_list = sms_manager.get_sms_history(limit=limit, offset=offset)
        total_count = sms_manager.get_sms_count()
        
        return render_template('sms_history.html',
                             sms_list=sms_list,
                             total_count=total_count,
                             page=page,
                             limit=limit,
                             company='SIBERINDO')
    except Exception as e:
        logger.exception("Error loading SMS history")
        return render_template('error.html',
                             error_message=f'Error loading SMS history: {str(e)}',
                             company='SIBERINDO'), 500


@sms_bp.route('/api/sms/send', methods=['POST'])
@login_required
def api_send_sms():
    """API endpoint for sending SMS."""
    try:
        data = request.get_json() or {}
        sender = data.get('sender', '').strip()
        receiver = data.get('receiver', '').strip()
        message = data.get('message', '').strip()
        sms_type = data.get('type', 'STANDARD')
        
        if not all([sender, receiver, message]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        sms_manager = SMSManager()
        success = sms_manager.send_sms(sender, receiver, message, sms_type)
        
        return jsonify({
            'success': success,
            'message': 'SMS sent successfully' if success else 'Failed to send SMS'
        })
    except Exception as e:
        logger.exception("Error in API send SMS")
        return jsonify({'success': False, 'message': str(e)}), 500


@sms_bp.route('/api/sms/batch', methods=['POST'])
@login_required
def api_send_sms_batch():
    """API endpoint for batch SMS sending."""
    try:
        data = request.get_json() or {}
        sms_list = data.get('sms_list', [])
        
        if not sms_list or not isinstance(sms_list, list):
            return jsonify({'success': False, 'message': 'Invalid SMS list'}), 400
        
        # Prepare SMS data
        prepared_sms = []
        for sms in sms_list:
            prepared_sms.append((
                sms.get('sender', ''),
                sms.get('receiver', ''),
                sms.get('message', ''),
                sms.get('type', 'STANDARD'),
                'SENT'
            ))
        
        sms_manager = SMSManager()
        success = sms_manager.send_sms_batch(prepared_sms)
        
        return jsonify({
            'success': success,
            'count': len(prepared_sms) if success else 0,
            'message': f'{len(prepared_sms)} SMS sent' if success else 'Batch send failed'
        })
    except Exception as e:
        logger.exception("Error in API batch send SMS")
        return jsonify({'success': False, 'message': str(e)}), 500


@sms_bp.route('/api/sms/history', methods=['GET'])
@login_required
def api_sms_history():
    """API endpoint for SMS history with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = (page - 1) * limit
        
        sms_manager = SMSManager()
        sms_list = sms_manager.get_sms_history(limit=limit, offset=offset)
        total_count = sms_manager.get_sms_count()
        
        from datetime import datetime
        return jsonify({
            'success': True,
            'sms_list': [dict(sms) if hasattr(sms, 'keys') else sms for sms in sms_list],
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error in API SMS history")
        return jsonify({'success': False, 'message': str(e)}), 500