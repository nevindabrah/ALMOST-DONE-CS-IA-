from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist. Please sign up for an account.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

    
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and request.form:
        email = request.form.get('email')
        fullname = request.form.get('fullname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.', category='error')
            return redirect(url_for('auth.signup'))

        if not role or role not in ['student', 'teacher']:
            flash('Invalid role selected.', category='error')
            return render_template("signup.html")

        # Existing validation and user creation logic
        if not email or len(email) < 4:
            flash('Email must be greater than 4 characters', category='error')
        elif not fullname or len(fullname) < 2: 
            flash('Full name must be greater than 2 characters', category='error')
        elif not password1 or not password2 or password1 != password2:
            flash('Passwords do not match', category='error')
        elif not password1 or len(password1) < 7: 
            flash('Password must be at least 7 characters', category='error')
        else:
            new_user = User(
                email=email,
                fullname=fullname,
                password=generate_password_hash(password1, method='pbkdf2:sha256'),
                role=role
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Welcome to LetsPlan!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)
