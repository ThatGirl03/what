# website/firebase_config.py
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Get the Firebase credentials from environment variables
firebase_credentials_json = os.getenv("FIREBASE_CREDENTIALS")

if firebase_credentials_json:
    with open(firebase_credentials_json, "r") as f:
        # Load the JSON string into a dictionary
        firebase_credentials = json.load(f)

    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

else:
    raise ValueError("Firebase credentials not found in environment variables")

# Set up Firestore client
db = firestore.client()
