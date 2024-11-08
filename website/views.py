import os
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime
from .models import MemoPosts, NetworkPosts, Posts, QuestionPosts
from .firebase_config import db  # Firebase config file for Firestore instance
from google.cloud import firestore


views = Blueprint('views', __name__)

ADMIN_PASSWORD = 'admin123'
ADMIN_EMAIL = 'admin@easylink.ac.za'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@views.route('/', methods=['GET', 'POST'])
def home():
    name = "Ayanda!"
    return render_template("home.html", Hello='Welcome to EasyLink ' + name)


@views.route('/profile')
@login_required
def profile():
    user_data = db.collection('users').document(current_user.email).get()
    if user_data.exists:
        user = user_data.to_dict()
        return render_template("profile.html", user=user)
    else:
        flash("User profile not found.", category='error')
        return redirect(url_for('views.home'))


@views.route('/set_theme', methods=['POST'])
def set_theme():
    data = request.get_json()
    session['theme'] = data['theme']
    return '', 204


@views.route('/about')
def about():
    return render_template("about.html")


@views.route('/help')
def help():
    return render_template("help.html")


@views.route('/login')
def login():
    return render_template("login.html")


@views.route('/sign-up')
def sign_up():
    return render_template("sign-up.html")


@views.route('/admin-profile')
def admin_profile():
    return render_template('pick_profile_home.html')


@views.route('/admin_home')
def admin_home():
    # Ensure only logged-in admin can access this page
    if 'admin_logged_in' not in session:
        return redirect(url_for('views.adm_login'))
    return render_template('admin_home.html')


@views.route('/adm_login', methods=['GET', 'POST'])
def adm_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the input matches hardcoded admin details
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True  # Set session variable
            flash('Login successful!', 'success')
            return redirect(url_for('views.admin_home'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('views.adm_login'))

    return render_template('adm_login.html')


@views.route('/some_protected_page')
def some_protected_page():
    if 'admin_logged_in' not in session:
        flash('Please log in to access this page', 'error')
        return redirect(url_for('views.adm_login'))

    return render_template('protected_page.html')


@views.route('/admin_base', methods=['GET', 'POST'])
def admin_base():
    return render_template('admin_home.html')


@views.route('/admin_sign-up', methods=['GET', 'POST'])
def adminsignup():
    return render_template('admin_sign-up.html')


# Example of adding Firebase operations for DataPosts
@views.route('/create_post', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        post_content = request.form.get('content')
        post_data = {
            'user_id': current_user.email,
            'content': post_content,
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        db.collection('posts').add(post_data)
        flash('Post created successfully!', category='success')
        return redirect(url_for('views.home'))

# SECTOR A
@views.route('/manage_sectorA', methods=['GET', 'POST'])
def manage_sectorA():
    if request.method == 'POST':
        image_file = request.files['image']
        pdf_link = request.form['pdf']

        # Save the uploaded image
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
        image_file.save(image_path)

        # Save the post in Firestore
        new_post = Posts(image=image_file.filename, pdf=pdf_link, date_created=datetime.now())
        new_post.save_to_firestore()  # Save the post to Firestore

        return redirect(url_for('views.manage_sectorA'))

    # Retrieve all posts from Firestore
    posts = Posts.get_all()

    return render_template('manage_sectorA.html', posts=posts)

@views.route('/sectorA')
def sectorA():
    posts = Posts.get_all()
    posts.sort(key=lambda post: post.date_created, reverse=True)  # Sort by date_created descending
    return render_template("sectorA.html", posts=posts)

@views.route('/delete/<post_id>', methods=['POST'])
def delete_post(post_id):
    post = Posts.get_by_id(post_id)
    if post and post.image:
        image_path = os.path.join(current_app.root_path, 'static', 'uploads', post.image)
        if os.path.exists(image_path):  # Check if the image file exists
            os.remove(image_path)  # Remove the image file
    Posts.delete_from_firestore(post_id)  # Delete the post in Firestore
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('views.manage_sectorA'))


@views.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Posts.get_by_id(post_id)
    if request.method == 'POST':
        # Update post with new data
        post.pdf = request.form['pdf']
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                post.image = filename
        post.save_to_firestore()  # Save changes to Firestore
        flash('Post updated successfully!', 'success')
        return redirect(url_for('views.manage_sectorA'))
    return render_template('edit_post.html', post=post)

# SECTOR B
@views.route('/manage_sectorB', methods=['GET', 'POST'])
def manage_sectorB():
    if request.method == 'POST':
        image_file = request.files['image']
        pdf_link = request.form['pdf']

        # Save uploaded image
        if image_file:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(image_file.filename))
            image_file.save(image_path)
            image_filename = image_file.filename
        else:
            image_filename = None

        # Save the new post in Firestore
        new_post = NetworkPosts(image=image_filename, pdf=pdf_link)
        new_post.save_to_firestore()

        flash('New Sector B post created!', 'success')
        return redirect(url_for('views.manage_sectorB'))

    # Retrieve all Sector B posts
    posts = NetworkPosts.get_all()
    return render_template('manage_sectorB.html', posts=posts)

@views.route('/sectorB')
def sectorB():
    posts = NetworkPosts.get_all()
    posts.sort(key=lambda post: post.date_created, reverse=True)  # Sort by date_created descending
    return render_template("sectorB.html", posts=posts)

@views.route('/delete_sectorB/<post_id>', methods=['POST'])
def delete_sectorB_post(post_id):
    post = NetworkPosts.get_by_id(post_id)
    if post and post.image:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], post.image)
        if os.path.exists(image_path):
            os.remove(image_path)  # Remove the image file if it exists
    NetworkPosts.delete_from_firestore(post_id)
    flash('Sector B post deleted successfully!', 'success')
    return redirect(url_for('views.manage_sectorB'))

@views.route('/edit_sectorB/<post_id>', methods=['GET', 'POST'])
def edit_sectorB_post(post_id):
    post = NetworkPosts.get_by_id(post_id)
    if request.method == 'POST':
        # Update post with new data
        post.pdf = request.form['pdf']
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                post.image = filename
        post.save_to_firestore()
        flash('Sector B post updated successfully!', 'success')
        return redirect(url_for('views.manage_sectorB'))
    return render_template('edit_sectorB_post.html', post=post)


@views.route('/manage_sectorC')
def manage_sectorC():
    return render_template('manage_sectorC.html')

@views.route('/sectorC')
def sectorC():
    return render_template("sectorC.html")

@views.route('/sectorD')
def sectorD():
    return render_template("sectorD.html")

@views.route('/manage_sectorD')
def manage_sectorD():
    return render_template('manage_sectorD.html')

@views.route('/manage_sectorE')
def manage_sectorE():
    return render_template('manage_sectorE.html')

@views.route('/sectorE')
def sectorE():
    return render_template("sectorE.html")

@views.route('/sectorF')
def sectorF():
    return render_template("sectorF.html")

@views.route('/manage_sectorF')
def manage_sectorF():
    return render_template('manage_sectorF.html')

@views.route('/manage_sectorG')
def manage_sectorG():
    return render_template('manage_sectorG.html')

@views.route('/sectorG')
def sectorG():
    return render_template("sectorG.html")

@views.route('/nex')
def nex():
    return render_template('nex.html')

@views.route('/nexus')
def nexus():
    return render_template('nexus.html')

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_image_locally(image_file):
    if image_file:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        return filename
    return None

# QUESTIONS
@views.route('/manage_questions', methods=['GET', 'POST'])
def manage_questions():
    if request.method == 'POST':
        image_file = request.files['image']
        pdf_link = request.form['pdf']

        # Save image locally
        image_filename = save_image_locally(image_file)

        # Save post in Firestore
        new_post = QuestionPosts(image=image_filename, pdf=pdf_link, date_created=datetime.now())
        new_post.save_to_firestore()

        flash('New Question post created!', 'success')
        return redirect(url_for('views.manage_questions'))

    posts = QuestionPosts.get_all()
    return render_template('manage_questions.html', posts=posts)

@views.route('/questions')
def questions():
    posts = QuestionPosts.get_all()
    posts.sort(key=lambda post: post.date_created, reverse=True)
    return render_template("questions.html", posts=posts)

@views.route('/delete_question/<post_id>', methods=['POST'])
def delete_question_post(post_id):
    post = QuestionPosts.get_by_id(post_id)
    if post and post.image:
        image_path = os.path.join(UPLOAD_FOLDER, post.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    QuestionPosts.delete_from_firestore(post_id)
    flash('Question post deleted successfully!', 'success')
    return redirect(url_for('views.manage_questions'))

@views.route('/edit_question/<post_id>', methods=['GET', 'POST'])
def edit_question_post(post_id):
    post = QuestionPosts.get_by_id(post_id)
    if request.method == 'POST':
        post.pdf = request.form['pdf']

        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                post.image = save_image_locally(file)
        post.save_to_firestore()
        flash('Question post updated successfully!', 'success')
        return redirect(url_for('views.manage_questions'))

    return render_template('edit_question_post.html', post=post)

# MEMOS
@views.route('/manage_memo', methods=['GET', 'POST'])
def manage_memo():
    if request.method == 'POST':
        image_file = request.files['image']
        pdf_link = request.form['pdf']

        # Save image locally
        image_filename = save_image_locally(image_file)

        new_post = MemoPosts(image=image_filename, pdf=pdf_link, date_created=datetime.now())
        new_post.save_to_firestore()

        flash('New Memo post created!', 'success')
        return redirect(url_for('views.manage_memo'))

    posts = MemoPosts.get_all()
    return render_template('manage_memo.html', posts=posts)

@views.route('/memo')
def memo():
    posts = MemoPosts.get_all()
    posts.sort(key=lambda post: post.date_created, reverse=True)
    return render_template("memo.html", posts=posts)

@views.route('/delete_memo/<post_id>', methods=['POST'])
def delete_memo_post(post_id):
    post = MemoPosts.get_by_id(post_id)
    if post and post.image:
        image_path = os.path.join(UPLOAD_FOLDER, post.image)
        if os.path.exists(image_path):
            os.remove(image_path)

    MemoPosts.delete_from_firestore(post_id)
    flash('Memo post deleted successfully!', 'success')
    return redirect(url_for('views.manage_memo'))

@views.route('/edit_memo/<post_id>', methods=['GET', 'POST'])
def edit_memo_post(post_id):
    post = MemoPosts.get_by_id(post_id)
    if request.method == 'POST':
        post.pdf = request.form['pdf']

        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                post.image = save_image_locally(file)
        post.save_to_firestore()
        flash('Memo post updated successfully!', 'success')
        return redirect(url_for('views.manage_memo'))

    return render_template('edit_memo_post.html', post=post)


@views.route('/engineer')
def engineer():
    return render_template('engineer.html')

@views.route('/robotics')
def robotics():
    return render_template('robotics.html')

@views.route('/physics')
def physics():
    return render_template('physics.html')

@views.route('/iot')
def iot():
    return render_template('iot.html')

@views.route('/math')
def math():
    return render_template('math.html')

@views.route('/accounting')
def accounting():
    return render_template('accounting.html')

@views.route('/entrepreneurship')
def entrepreneurship():
    return render_template('entrepreneurship.html')

@views.route('/agric')
def agric():
    return render_template("agric.html")

@views.route('/networks')
def networks():
    return render_template('networks.html')

@views.route('/numbers')
def numbers():
    return render_template('numbers.html')

@views.route('/science')
def science():
    return render_template('science.html')

@views.route('/code')
def code():
    return render_template('code.html')

@views.route('/ict')
def ict():
    return render_template('ict.html')

@views.route('/kca')
def kca():
    return render_template('kca.html')


@views.route('/manage_learners')
def manage_learners():
    # Retrieve all users from Firestore, excluding passwords
    users_docs = db.collection('users').stream()
    users = []
    for doc in users_docs:
        user_data = doc.to_dict()
        
        # Retrieve and format the last_used field, with a fallback if it's missing or invalid
        last_used = user_data.get('last_used')
        if isinstance(last_used, datetime):  # Check if last_used is a datetime
            last_used = last_used.strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_used = 'No recent activity'  # Default message if missing or invalid
        
        users.append({
            'firstname': user_data.get('firstname'),
            'lastname': user_data.get('lastname'),
            'email': user_data.get('email'),
            'last_used': last_used,
            'is_active': user_data.get('is_active', False)
        })

    return render_template('manage_learners.html', users=users)


@views.route('/manage_nexus')
def manage_nexus():
    return render_template('manage_nexus.html')


@views.route('/get_messages')
def get_messages():
    # Retrieve all messages from Firestore, ordered by timestamp
    messages_ref = db.collection('nexus_messages').order_by('timestamp')
    messages_docs = messages_ref.stream()

    messages = [
        {
            'id': doc.id,
            'sender': doc.to_dict().get('sender'),
            'content': doc.to_dict().get('content'),
            'timestamp': doc.to_dict().get('timestamp').strftime('%Y-%m-%d %H:%M:%S'),
            'user_type': doc.to_dict().get('user_type'),
            'seen': doc.to_dict().get('seen', False)
        }
        for doc in messages_docs
    ]

    return jsonify(messages)


@views.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    content = data.get('content')
    
    if current_user.is_authenticated:
        user_type = 'admin' if getattr(current_user, 'is_admin', False) else 'learner'
        sender = f"{current_user.firstname} {current_user.lastname}"
    else:
        return jsonify({'error': 'User not authenticated'}), 401
    
    # Add the message to Firestore with 'seen' status as False
    db.collection('nexus_messages').add({
        'sender': sender,
        'content': content,
        'timestamp': datetime.now(),
        'user_type': user_type,
        'seen': False
    })

    return jsonify({'status': 'Message sent'})


@views.route('/mark_message_seen', methods=['POST'])
def mark_message_seen():
    data = request.get_json()
    message_id = data.get('message_id')
    
    try:
        message_ref = db.collection('nexus_messages').document(message_id)
        message_ref.update({'seen': True})
        return jsonify({'status': 'Message marked as seen'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500