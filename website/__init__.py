# website/__init__.py

import os
from flask import Flask
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
from website.models import User
from .firebase_config import db  # Import the Firestore db from firebase_config

# Load environment variables from the .env file
load_dotenv()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Set secret key and other configurations
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov'}

    # Import Blueprints
    from .views import views
    from .auth import auth
    from .admin_auth import admin_auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin_auth, url_prefix='/')

    # Initialize Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            return User.from_firestore(user_doc.id, user_doc.to_dict())  # Return a User instance
        return None

    # Add current_user context processor for templates
    @app.context_processor
    def inject_user():
        return dict(user=current_user)

    # Create upload folder if it doesn't exist
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f'Created upload folder at {upload_folder}')

    return app
