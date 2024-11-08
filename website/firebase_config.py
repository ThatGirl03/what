# website/firebase_config.py
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# Get the Firebase credentials from environment variables
firebase_credentials_json = os.getenv('FIREBASE_CREDENTIALS')
if firebase_credentials_json:
    firebase_credentials = json.loads(firebase_credentials_json)  # Load the JSON string into a dictionary
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("Firebase credentials not found in environment variables")

# Set up Firestore client
db = firestore.client()
