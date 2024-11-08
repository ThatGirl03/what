# website/firebase_config.py
import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Get the Firebase credentials from environment variables
firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

if firebase_credentials:
    decoded_json = base64.b64decode(firebase_credentials.encode("ascii")).decode("ascii")
    creds = json.loads(decoded_json)
    cred = credentials.Certificate(creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET')
    })

else:
    raise ValueError("Firebase credentials not found in environment variables")

# Set up Firestore client
db = firestore.client()

# Set up Firebase Storage client
bucket = storage.bucket()
