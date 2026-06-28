from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.blueprints.auth import auth_bp
from urllib.parse import urlparse

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = 'remember' in request.form
        
        user = User.query.filter((User.email == email) | (User.username == email)).first()
        if user is None or not user.check_password(password):
            flash('Invalid username/email or password', 'danger')
            return render_template('auth/login.html')
        
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('events.dashboard')
        return redirect(next_page)
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('events.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username is already taken', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email is already registered', 'danger')
            return render_template('auth/register.html')
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please sign in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('events.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '')
        
        user = User.query.filter((User.email == email) | (User.username == email)).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash('Password reset successful! Please sign in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or Email address not found.', 'danger')
            
    return render_template('auth/forgot_password.html')
