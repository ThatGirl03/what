import os
from flask import Flask
from flask_login import LoginManager, current_user

import __magic__

from models import User
from firebase_config import db

# Import Blueprints
from views import views
from auth import auth
from admin_auth import admin_auth

login_manager = LoginManager()

app = Flask(__name__)

# Set secret key and other configurations
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["ALLOWED_EXTENSIONS"] = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "mp4",
    "avi",
    "mov",
}


app.register_blueprint(views, url_prefix="/")
app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(admin_auth, url_prefix="/")

# Initialize Flask-Login
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection("users").document(user_id).get()
    if user_doc.exists:
        return User.from_firestore(
            user_doc.id, user_doc.to_dict()
        )  # Return a User instance
    return None


# Add current_user context processor for templates
@app.context_processor
def inject_user():
    return dict(user=current_user)


# Create upload folder if it doesn't exist
upload_folder = app.config["UPLOAD_FOLDER"]
if not os.path.exists(upload_folder):
    os.makedirs(upload_folder)
    print(f"Created upload folder at {upload_folder}")

app.run(host="0.0.0.0", port=3000, debug=True)
