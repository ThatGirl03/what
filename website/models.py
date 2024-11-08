import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from website.firebase_config import db  # Import Firestore instance from firebase_config

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from website.firebase_config import db  # Import Firestore instance from firebase_config

class User(UserMixin):
    def __init__(self, firstname, lastname, email, password, profile=None, hashed=False, user_id=None):
        self.id = user_id  # Store the Firestore document ID as the user ID
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        # Hash the password only if it’s not already hashed
        self.password = generate_password_hash(password) if not hashed else password
        self.profile = profile

    @classmethod
    def from_firestore(cls, doc_id, data):
        """Initialize a User instance from Firestore data."""
        return cls(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            email=data.get('email'),
            password=data.get('password'),  # Assume this is already a hashed password
            profile=data.get('profile'),
            hashed=True,  # Indicate that the password is already hashed
            user_id=doc_id
        )

    def save_to_firestore(self):
        """Save a user to Firestore."""
        user_data = {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'password': self.password,  # Store hashed password in Firestore
            'profile': self.profile
        }
        db.collection('users').document(self.email).set(user_data)

    def check_password(self, password):
        """Check the hashed password."""
        return check_password_hash(self.password, password)

    def get_id(self):
        """Return the unique identifier for Flask-Login."""
        return self.id or self.email

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True if self.email else False

    @property
    def is_anonymous(self):
        return False


class Admin(UserMixin):
    def __init__(self, name, staff, contact_email, password, hashed=False, admin_id=None):
        self.id = admin_id 
        self.name = name
        self.staff = staff
        self.contact_email = contact_email
        self.password = generate_password_hash(password) if not hashed else password
        

    @classmethod
    def from_firestore(cls, doc_id, data):
        """Initialize an Admin instance from Firestore data."""
        return cls(
            name=data.get('name'),
            staff=data.get('staff'),
            contact_email=data.get('contact_email'),
            password=data.get('password'),  # Ensure this is a hashed password
            admin_id=doc_id
        )

    def save_to_firestore(self):
        """Save an admin to Firestore."""
        admin_data = {
            'name': self.name,
            'staff': self.staff,
            'contact_email': self.contact_email,
            'password': self.password
        }
        db.collection('admins').document(self.contact_email).set(admin_data)

    @staticmethod
    def get_by_email(contact_email):
        """Retrieve an admin from Firestore by contact email."""
        doc = db.collection('admins').document(contact_email).get()
        if doc.exists:
            return Admin.from_firestore(doc.id, doc.to_dict())
        return None

    def check_password(self, password):
        """Check the hashed password."""
        return check_password_hash(self.password, password)

    def get_id(self):
        """Return the unique identifier for Flask-Login."""
        return self.contact_email

    @property
    def is_active(self):
        """Admin is always active in this context."""
        return True

    @property
    def is_authenticated(self):
        """Admin is authenticated if they have a contact_email."""
        return True if self.contact_email else False

    @property
    def is_anonymous(self):
        """This should return False as we don't allow anonymous users."""
        return False

class Posts:
    def __init__(self, image, pdf, date_created=None, post_id=None):
        self.id = post_id
        self.image = image
        self.pdf = pdf
        self.date_created = date_created or datetime.now()

    @classmethod
    def from_firestore(cls, doc_id, data):
        """Initialize a Posts instance from Firestore data."""
        return cls(
            image=data.get('image'),
            pdf=data.get('pdf'),
            date_created=data.get('date_created'),
            post_id=doc_id
        )

    def save_to_firestore(self):
        """Save a post to Firestore."""
        post_data = {
            'image': self.image,
            'pdf': self.pdf,
            'date_created': self.date_created
        }
        if self.id:
            db.collection('posts').document(self.id).set(post_data)
        else:
            new_post_ref = db.collection('posts').add(post_data)
            self.id = new_post_ref[1].id  # Save generated document ID

    @staticmethod
    def get_by_id(post_id):
        """Retrieve a post from Firestore by post_id."""
        doc = db.collection('posts').document(post_id).get()
        if doc.exists:
            return Posts.from_firestore(doc.id, doc.to_dict())
        return None

    @staticmethod
    def get_all():
        """Retrieve all posts from Firestore."""
        docs = db.collection('posts').stream()
        return [Posts.from_firestore(doc.id, doc.to_dict()) for doc in docs]
    
    @staticmethod
    def delete_from_firestore(post_id):
        """Delete a post from Firestore."""
        db.collection('posts').document(post_id).delete()

    def __repr__(self):
        return f'<Post {self.id}>'
    

class NetworkPosts:
    def __init__(self, image, pdf, date_created=None, post_id=None):
        self.id = post_id  # Firestore document ID
        self.image = image
        self.pdf = pdf
        self.date_created = date_created or datetime.now()  # Default to current time if not provided

    @classmethod
    def from_firestore(cls, doc_id, data):
        """Initialize a NetworkPosts instance from Firestore data."""
        return cls(
            image=data.get('image'),
            pdf=data.get('pdf'),
            date_created=data.get('date_created'),
            post_id=doc_id
        )

    def save_to_firestore(self):
        """Save a NetworkPost instance to Firestore."""
        post_data = {
            'image': self.image,
            'pdf': self.pdf,
            'date_created': self.date_created
        }
        if self.id:
            db.collection('network_posts').document(self.id).set(post_data)
        else:
            new_post_ref = db.collection('network_posts').add(post_data)
            self.id = new_post_ref[1].id  # Capture generated document ID

    @staticmethod
    def get_by_id(post_id):
        """Retrieve a NetworkPost from Firestore by post_id."""
        doc = db.collection('network_posts').document(post_id).get()
        if doc.exists:
            return NetworkPosts.from_firestore(doc.id, doc.to_dict())
        return None

    @staticmethod
    def get_all():
        """Retrieve all NetworkPosts from Firestore."""
        docs = db.collection('network_posts').stream()
        return [NetworkPosts.from_firestore(doc.id, doc.to_dict()) for doc in docs]

    def __repr__(self):
        return f"<NetworkPosts {self.id}>"
    
class QuestionPosts:
    def __init__(self, image, pdf, date_created=None, post_id=None):
        self.id = post_id  # Firestore document ID
        self.image = image
        self.pdf = pdf
        self.date_created = date_created or datetime.now()  # Default to current time if not provided

    @classmethod
    def from_firestore(cls, doc_id, data):
        """Initialize a QuestionPosts instance from Firestore data."""
        return cls(
            image=data.get('image'),
            pdf=data.get('pdf'),
            date_created=data.get('date_created'),
            post_id=doc_id
        )

    def save_to_firestore(self):
        """Save a QuestionPost instance to Firestore."""
        post_data = {
            'image': self.image,
            'pdf': self.pdf,
            'date_created': self.date_created
        }
        if self.id:
            db.collection('question_posts').document(self.id).set(post_data)
        else:
            new_post_ref = db.collection('question_posts').add(post_data)
            self.id = new_post_ref[1].id  # Capture generated document ID

    @staticmethod
    def get_by_id(post_id):
        """Retrieve a QuestionPost from Firestore by post_id."""
        doc = db.collection('question_posts').document(post_id).get()
        if doc.exists:
            return QuestionPosts.from_firestore(doc.id, doc.to_dict())
        return None

    @staticmethod
    def get_all():
        """Retrieve all QuestionPosts from Firestore."""
        docs = db.collection('question_posts').stream()
        return [QuestionPosts.from_firestore(doc.id, doc.to_dict()) for doc in docs]

    @staticmethod
    def delete_from_firestore(post_id):
        """Delete a QuestionPost by ID in Firestore."""
        db.collection('question_posts').document(post_id).delete()

    def __repr__(self):
        return f"<QuestionPosts {self.id}>"   
    
class MemoPosts:
    def __init__(self, image, pdf, date_created=None, post_id=None):
        self.id = post_id  # Firestore document ID
        self.image = image
        self.pdf = pdf
        self.date_created = date_created or datetime.now()  # Default to current time if not provided

    @classmethod
    def from_firestore(cls, doc_id, data):
        """Initialize a MemoPosts instance from Firestore data."""
        return cls(
            image=data.get('image'),
            pdf=data.get('pdf'),
            date_created=data.get('date_created'),
            post_id=doc_id
        )

    def save_to_firestore(self):
        """Save a MemoPost instance to Firestore."""
        post_data = {
            'image': self.image,
            'pdf': self.pdf,
            'date_created': self.date_created
        }
        if self.id:
            db.collection('memo_posts').document(self.id).set(post_data)
        else:
            new_post_ref = db.collection('memo_posts').add(post_data)
            self.id = new_post_ref[1].id  # Capture generated document ID

    @staticmethod
    def get_by_id(post_id):
        """Retrieve a MemoPost from Firestore by post_id."""
        doc = db.collection('memo_posts').document(post_id).get()
        if doc.exists:
            return MemoPosts.from_firestore(doc.id, doc.to_dict())
        return None

    @staticmethod
    def get_all():
        """Retrieve all MemoPosts from Firestore."""
        docs = db.collection('memo_posts').stream()
        return [MemoPosts.from_firestore(doc.id, doc.to_dict()) for doc in docs]

    @staticmethod
    def delete_from_firestore(post_id):
        """Delete a MemoPost by ID in Firestore."""
        db.collection('memo_posts').document(post_id).delete()

    def __repr__(self):
        return f"<MemoPosts {self.id}>"
    
    