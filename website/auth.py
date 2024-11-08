from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .firebase_config import db  # Import Firestore instance from firebase_config
from .models import User
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query Firestore for user by email
        user_docs = db.collection('users').where('email', '==', email).stream()
        user_doc = next(user_docs, None)  # Get the first match or None if not found

        if user_doc:
            user_data = user_doc.to_dict()  # Convert to dictionary
            user = User.from_firestore(user_doc.id, user_data)  # Create User instance

            # Check if the password is correct
            if user.check_password(password):
                flash('Welcome to Easy Link!', category='success')
                login_user(user)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        lastname = request.form.get('lastname')
        firstname = request.form.get('firstname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not all([email, lastname, firstname, password1, password2]):
            flash('All fields are required!', category='error')
            return redirect(url_for('auth.sign_up'))

        existing_user = db.collection('users').where('email', '==', email).stream()
        if next(existing_user, None):
            flash('Email address already in use. Please use a different email.', category='error')
            return redirect(url_for('auth.sign_up'))

        if password1 != password2:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('auth.sign_up'))

        # Create new user with hashed password
        new_user = User(firstname=firstname, lastname=lastname, email=email, password=password1)
        new_user.save_to_firestore()

        flash('Account created!', category='success')
        login_user(new_user)
        return redirect(url_for('views.home'))

    return render_template("sign-up.html", user=current_user)
