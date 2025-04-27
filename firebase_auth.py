import os
import pyrebase
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseAuth:
    """Firebase Authentication for Streamlit app"""
    
    def __init__(self):
        """Initialize Firebase Authentication"""
        # Firebase configuration
        self.firebase_config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID"),
            "databaseURL": ""  # Required by pyrebase but not used
        }
        
        # Initialize Firebase
        try:
            self.firebase = pyrebase.initialize_app(self.firebase_config)
            self.auth = self.firebase.auth()
            print("Firebase Authentication initialized")
        except Exception as e:
            print(f"Error initializing Firebase Authentication: {str(e)}")
            self.auth = None
    
    def is_initialized(self):
        """Check if Firebase Authentication is initialized"""
        return self.auth is not None
    
    def login(self, email, password):
        """
        Login with email and password
        
        Args:
            email (str): User email
            password (str): User password
            
        Returns:
            dict: User info if successful, None otherwise
        """
        if not self.is_initialized():
            return None, "Firebase Authentication not initialized"
        
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            return user, None
        except Exception as e:
            error_message = str(e)
            return None, error_message
    
    def get_account_info(self, id_token):
        """
        Get account info for a user
        
        Args:
            id_token (str): User ID token
            
        Returns:
            dict: User account info if successful, None otherwise
        """
        if not self.is_initialized():
            return None
        
        try:
            account_info = self.auth.get_account_info(id_token)
            return account_info
        except Exception as e:
            print(f"Error getting account info: {str(e)}")
            return None
    
    def check_admin_access(self, id_token, admin_uid):
        """
        Check if the user has admin access
        
        Args:
            id_token (str): User ID token
            admin_uid (str): Admin UID to check against
            
        Returns:
            bool: True if user has admin access, False otherwise
        """
        if not self.is_initialized():
            return False
        
        try:
            account_info = self.get_account_info(id_token)
            if account_info and 'users' in account_info:
                user_uid = account_info['users'][0]['localId']
                return user_uid == admin_uid
            return False
        except Exception as e:
            print(f"Error checking admin access: {str(e)}")
            return False 