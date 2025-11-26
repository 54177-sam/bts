from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import config

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Use configured admin credentials (override with env vars in production)
        if username == config.Config.ADMIN_USER and password == config.Config.ADMIN_PASS:
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