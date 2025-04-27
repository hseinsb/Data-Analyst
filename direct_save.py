import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import json
import datetime
import streamlit as st
import os

# Initialize Firebase connection
def initialize_firebase():
    """Initialize Firebase"""
    try:
        # Log the attempt
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Attempting to initialize Firebase\n")
        
        # Check if Firebase app is already initialized
        try:
            firebase_admin.get_app()
            print("Firebase app already initialized")
            with open("save_attempts.log", "a") as log:
                log.write(f"{datetime.datetime.now().isoformat()} - Firebase app already initialized\n")
        except ValueError:
            # Check if credentials file exists
            if not os.path.exists('firebase_credentials.json'):
                error_msg = "ERROR: firebase_credentials.json not found!"
                print(error_msg)
                with open("save_attempts.log", "a") as log:
                    log.write(f"{datetime.datetime.now().isoformat()} - {error_msg}\n")
                return None
            
            # Initialize Firebase app with credentials
            try:
                cred = credentials.Certificate('firebase_credentials.json')
                firebase_admin.initialize_app(cred)
                print("Firebase initialized with credentials")
                with open("save_attempts.log", "a") as log:
                    log.write(f"{datetime.datetime.now().isoformat()} - Firebase initialized with credentials\n")
            except Exception as cred_error:
                error_msg = f"ERROR: Failed to initialize Firebase with credentials: {str(cred_error)}"
                print(error_msg)
                with open("save_attempts.log", "a") as log:
                    log.write(f"{datetime.datetime.now().isoformat()} - {error_msg}\n")
                return None
        
        # Get Firestore database
        try:
            db = firestore.client()
            with open("save_attempts.log", "a") as log:
                log.write(f"{datetime.datetime.now().isoformat()} - Successfully created Firestore client\n")
            return db
        except Exception as db_error:
            error_msg = f"ERROR: Failed to get Firestore client: {str(db_error)}"
            print(error_msg)
            with open("save_attempts.log", "a") as log:
                log.write(f"{datetime.datetime.now().isoformat()} - {error_msg}\n")
            return None
            
    except Exception as e:
        error_msg = f"Error initializing Firebase: {str(e)}"
        print(error_msg)
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - {error_msg}\n")
        return None

# Direct save function to be called from Streamlit
def direct_save_to_firestore(title, description, report_content, report_data):
    """
    Save report directly to Firestore
    
    Args:
        title (str): Report title
        description (str): Report description
        report_content (str): The actual report text
        report_data (dict): Additional report data
        
    Returns:
        str: Report ID if successful, None otherwise
    """
    try:
        # Log successful function entry
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Attempting to save report: {title}\n")
            
        # Initialize Firebase if needed
        db = initialize_firebase()
        if not db:
            return None
            
        # Generate a unique report ID
        report_id = str(uuid.uuid4())
        
        # Create the document in Firestore
        report_ref = db.collection('reports').document(report_id)
        
        # Prepare the document data
        doc_data = {
            'id': report_id,
            'title': title,
            'description': description,
            'query': json.dumps(report_data),
            'metrics': report_content,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        # Write log entry with document data
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Document data prepared for ID: {report_id}\n")
            log.write(f"Data sizes: title={len(title)}, description={len(description)}, query={len(json.dumps(report_data))}, metrics={len(report_content)}\n")
        
        # Save to Firestore
        report_ref.set(doc_data)
        
        # Verify the save
        verification = report_ref.get()
        if verification.exists:
            # Success - log it
            with open("save_attempts.log", "a") as log:
                log.write(f"{datetime.datetime.now().isoformat()} - SAVE SUCCESS for ID: {report_id}\n")
            print(f"Direct save successful - ID: {report_id}")
            # Add to session state
            if 'saved_reports' not in st.session_state:
                st.session_state.saved_reports = []
            st.session_state.saved_reports.append((report_id, title))
            return report_id
        else:
            # Verification failed - log it
            with open("save_attempts.log", "a") as log:
                log.write(f"{datetime.datetime.now().isoformat()} - VERIFICATION FAILED for ID: {report_id}\n")
            print(f"Direct save verification failed - ID: {report_id}")
            return None
    except Exception as e:
        # Log any exceptions
        import traceback
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - ERROR: {str(e)}\n")
            log.write(traceback.format_exc() + "\n")
        print(f"Error in direct save: {str(e)}")
        return None 

# Function to directly get all reports from Firestore
def direct_get_all_reports(limit=50):
    """
    Get all reports directly from Firestore
    
    Args:
        limit (int): Maximum number of reports to retrieve
        
    Returns:
        list: List of report dictionaries
    """
    try:
        # Log the attempt
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Attempting to get all reports (limit: {limit})\n")
        
        # Initialize Firebase if needed
        db = initialize_firebase()
        if not db:
            return []
        
        # Get reports from Firestore
        reports_ref = db.collection('reports').order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        
        # Convert to list of dictionaries
        reports = []
        for doc in reports_ref.stream():
            # Get the document data
            data = doc.to_dict()
            # Ensure the ID is included
            if 'id' not in data:
                data['id'] = doc.id
            # Add to list
            reports.append(data)
        
        # Log success
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Retrieved {len(reports)} reports from Firestore\n")
        
        return reports
    except Exception as e:
        # Log any error
        import traceback
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - ERROR getting reports: {str(e)}\n")
            log.write(traceback.format_exc() + "\n")
        print(f"Error getting reports: {str(e)}")
        return []

# Function to directly get a specific report from Firestore
def direct_get_report(report_id):
    """
    Get a specific report directly from Firestore
    
    Args:
        report_id (str): The ID of the report to retrieve
        
    Returns:
        dict: The report dictionary or None if not found
    """
    try:
        # Log the attempt
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Attempting to get report: {report_id}\n")
        
        # Initialize Firebase if needed
        db = initialize_firebase()
        if not db:
            return None
        
        # Get the document
        doc_ref = db.collection('reports').document(report_id)
        doc = doc_ref.get()
        
        if doc.exists:
            # Get the data
            data = doc.to_dict()
            # Ensure the ID is included
            if 'id' not in data:
                data['id'] = doc.id
                
            # Log success
            with open("save_attempts.log", "a") as log:
                log.write(f"{datetime.datetime.now().isoformat()} - Successfully retrieved report: {report_id}\n")
                
            return data
        else:
            # Log not found
            with open("save_attempts.log", "a") as log:
                log.write(f"{datetime.datetime.now().isoformat()} - Report not found: {report_id}\n")
                
            return None
    except Exception as e:
        # Log any error
        import traceback
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - ERROR getting report: {str(e)}\n")
            log.write(traceback.format_exc() + "\n")
        print(f"Error getting report: {str(e)}")
        return None

# Function to directly delete a report from Firestore
def direct_delete_report(report_id):
    """
    Delete a report directly from Firestore
    
    Args:
        report_id (str): The ID of the report to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Log the attempt
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Attempting to delete report: {report_id}\n")
        
        # Initialize Firebase if needed
        db = initialize_firebase()
        if not db:
            return False
        
        # Delete the document
        db.collection('reports').document(report_id).delete()
        
        # Log success
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - Successfully deleted report: {report_id}\n")
            
        return True
    except Exception as e:
        # Log any error
        import traceback
        with open("save_attempts.log", "a") as log:
            log.write(f"{datetime.datetime.now().isoformat()} - ERROR deleting report: {str(e)}\n")
            log.write(traceback.format_exc() + "\n")
        print(f"Error deleting report: {str(e)}")
        return False 