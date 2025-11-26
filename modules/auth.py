from flask import Blueprint, render_template, request, session, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html', company='SIBERINDO', full_company='SIBERINDO Technology')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))