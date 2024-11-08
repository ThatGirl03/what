from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .firebase_config import db  # Import Firestore instance from firebase_config
from .models import Admin

admin_auth = Blueprint('admin_auth', __name__)

@admin_auth.route('/admin_home', methods=['GET'])
@login_required
def admin_home():
    admins_ref = db.collection('admins')
    admins = [admin.to_dict() for admin in admins_ref.stream()]
    return render_template('admin_home.html', admins=admins)

@admin_auth.route('/adm_login', methods=['GET', 'POST'])
def adm_login():
    if request.method == 'POST':
        contact_email = request.form.get('email')
        password = request.form.get('password')

        admins_ref = db.collection('admins').where('contact_email', '==', contact_email).stream()
        admin_doc = next(admins_ref, None)

        if admin_doc:
            admin_data = admin_doc.to_dict()
            admin = Admin.from_firestore(admin_doc.id, admin_data)
            if admin.check_password(password):
                flash('Welcome to Admin Dashboard!', category='success')
                login_user(admin)
                session['admin_logged_in'] = True
                return redirect(url_for('admin_auth.admin_home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("adm_login.html", admin=current_user)

@admin_auth.route('/adm-logout')
@login_required
def adm_logout():
    logout_user()
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_auth.adm_login'))

@admin_auth.route('/admin_sign-up', methods=['GET', 'POST'])
def adm_signUp():
    if request.method == 'POST':
        contact_email = request.form.get('contact_email')
        admin_name = request.form.get('staff_name')
        staff = request.form.get('staff')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Check if the email or staff number is already registered
        existing_user = db.collection('admins').where('contact_email', '==', contact_email).stream()
        if next(existing_user, None):
            flash('Email address already in use. Please use a different email.', category='error')
            return redirect(url_for('admin_auth.adm_signUp'))

        existing_registration = db.collection('admins').where('staff', '==', staff).stream()
        if next(existing_registration, None):
            flash('Staff number already in use. Please use a different staff number.', category='error')
            return redirect(url_for('admin_auth.adm_signUp'))

        if password1 != password2:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('admin_auth.adm_signUp'))

        new_admin = Admin(name=admin_name, staff=staff, contact_email=contact_email, password=password1)
        new_admin.save_to_firestore()

        flash('Account created!', category='success')
        login_user(new_admin)
        session['admin_logged_in'] = True
        return redirect(url_for('admin_auth.admin_home'))

    return render_template("admin_sign-up.html", admin=current_user)
