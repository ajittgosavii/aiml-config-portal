"""
Firebase Authentication Module
Handles user authentication, registration, and admin management
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
import os
from datetime import datetime
from typing import Optional, Dict, List

# Initialize Firebase Admin SDK
def init_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            # Try to load from Streamlit secrets (production)
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
            else:
                # Load from local file (development)
                cred = credentials.Certificate("firebase-admin-key.json")
            
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully")
        except Exception as e:
            st.error(f"❌ Firebase initialization failed: {str(e)}")
            raise

# Get Firestore client
def get_firestore_client():
    """Get Firestore database client"""
    init_firebase()
    return firestore.client()

# User Authentication Functions
def create_user(email: str, password: str, display_name: str = None, is_admin: bool = False) -> Optional[Dict]:
    """Create a new user in Firebase Authentication"""
    try:
        init_firebase()
        
        # Create user in Firebase Auth
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name or email.split('@')[0],
            email_verified=False
        )
        
        # Set custom claims for admin users
        if is_admin:
            auth.set_custom_user_claims(user.uid, {'admin': True})
        
        # Create user profile in Firestore
        db = get_firestore_client()
        db.collection('users').document(user.uid).set({
            'email': email,
            'display_name': display_name or email.split('@')[0],
            'is_admin': is_admin,
            'created_at': datetime.now(),
            'last_login': None,
            'status': 'active'
        })
        
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'is_admin': is_admin
        }
    
    except auth.EmailAlreadyExistsError:
        st.error("❌ Email already exists")
        return None
    except Exception as e:
        st.error(f"❌ User creation failed: {str(e)}")
        return None

def verify_user(email: str, password: str) -> Optional[Dict]:
    """Verify user credentials and get their info"""
    try:
        init_firebase()
        
        # Get user by email
        user = auth.get_user_by_email(email)
        
        # Get user profile from Firestore
        db = get_firestore_client()
        user_doc = db.collection('users').document(user.uid).get()
        
        if user_doc.exists:
            user_data = user_doc.to_dict()
            
            # Update last login
            db.collection('users').document(user.uid).update({
                'last_login': datetime.now()
            })
            
            # Get custom claims
            user_record = auth.get_user(user.uid)
            custom_claims = user_record.custom_claims or {}
            
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user_data.get('display_name'),
                'is_admin': custom_claims.get('admin', False),
                'status': user_data.get('status', 'active')
            }
        
        return None
    
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        st.error(f"❌ Verification failed: {str(e)}")
        return None

def get_all_users() -> List[Dict]:
    """Get all users from Firebase (Admin only)"""
    try:
        init_firebase()
        db = get_firestore_client()
        
        users = []
        users_ref = db.collection('users')
        docs = users_ref.stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data['uid'] = doc.id
            users.append(user_data)
        
        return users
    
    except Exception as e:
        st.error(f"❌ Failed to get users: {str(e)}")
        return []

def delete_user(uid: str) -> bool:
    """Delete user from Firebase Authentication and Firestore"""
    try:
        init_firebase()
        auth.delete_user(uid)
        
        db = get_firestore_client()
        db.collection('users').document(uid).delete()
        
        return True
    
    except Exception as e:
        st.error(f"❌ User deletion failed: {str(e)}")
        return False

def make_admin(uid: str) -> bool:
    """Grant admin privileges to a user"""
    try:
        init_firebase()
        auth.set_custom_user_claims(uid, {'admin': True})
        
        db = get_firestore_client()
        db.collection('users').document(uid).update({
            'is_admin': True,
            'admin_since': datetime.now()
        })
        
        return True
    
    except Exception as e:
        st.error(f"❌ Failed to grant admin privileges: {str(e)}")
        return False

def revoke_admin(uid: str) -> bool:
    """Revoke admin privileges from a user"""
    try:
        init_firebase()
        auth.set_custom_user_claims(uid, {'admin': False})
        
        db = get_firestore_client()
        db.collection('users').document(uid).update({
            'is_admin': False
        })
        
        return True
    
    except Exception as e:
        st.error(f"❌ Failed to revoke admin privileges: {str(e)}")
        return False

def send_password_reset_email(email: str) -> bool:
    """Send password reset email"""
    try:
        init_firebase()
        link = auth.generate_password_reset_link(email)
        return True
    
    except Exception as e:
        st.error(f"❌ Password reset failed: {str(e)}")
        return False

# Session Management
def init_session_state():
    """Initialize session state variables for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

def login_user(user_info: Dict):
    """Set session state when user logs in"""
    st.session_state.authenticated = True
    st.session_state.user = user_info
    st.session_state.is_admin = user_info.get('is_admin', False)

def logout_user():
    """Clear session state when user logs out"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.is_admin = False

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def is_admin() -> bool:
    """Check if current user is admin"""
    return st.session_state.get('is_admin', False)

def get_current_user() -> Optional[Dict]:
    """Get current user info"""
    return st.session_state.get('user')

# Initialize admin user on first run
def initialize_admin():
    """Create initial admin user if doesn't exist"""
    try:
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@company.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123!')
        
        try:
            auth.get_user_by_email(admin_email)
            print(f"✅ Admin user already exists: {admin_email}")
        except auth.UserNotFoundError:
            result = create_user(
                email=admin_email,
                password=admin_password,
                display_name="System Administrator",
                is_admin=True
            )
            if result:
                print(f"✅ Admin user created: {admin_email}")
                print(f"   Password: {admin_password}")
                print("   ⚠️  Please change this password after first login!")
    
    except Exception as e:
        print(f"❌ Admin initialization failed: {str(e)}")
