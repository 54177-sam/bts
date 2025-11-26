from flask import Blueprint, render_template, request, flash, session
from modules.helpers import login_required

sms_bp = Blueprint('sms', __name__)

@sms_bp.route('/send_silent_sms', methods=['GET', 'POST'])
@login_required
def send_silent_sms():
    if request.method == 'POST':
        sender = request.form.get('sender')
        receiver = request.form.get('receiver')
        message = request.form.get('message')
        
        if sender and receiver and message:
            try:
                from modules.database import save_sms
                save_sms(sender, receiver, message, 'SILENT', 'SENT')
                flash('SIBERINDO - Silent SMS sent successfully!', 'success')
            except Exception as e:
                flash(f'Error sending SMS: {e}', 'error')
        else:
            flash('Please fill all fields!', 'error')
    
    return render_template('send_silent_sms.html', company='SIBERINDO')

@sms_bp.route('/send_sms')
@login_required
def send_sms():
    return render_template('send_sms.html', company='SIBERINDO')

@sms_bp.route('/sms_history')
@login_required
def sms_history():
    try:
        from modules.database import get_sms_history
        sms_list = get_sms_history()
        return render_template('sms_history.html', 
                             sms_list=sms_list,
                             company='SIBERINDO')
    except Exception as e:
        return f"Error loading SMS history: {e}", 500