import os
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime
import uuid
import traceback

class FirestoreHelper:
    """Helper class for Firestore database operations"""
    
    def __init__(self):
        """Initialize the Firestore connection"""
        self.db = None
        self.connected = False
        
        try:
            # Check if Firebase app is already initialized
            try:
                firebase_admin.get_app()
                print("Firebase app already initialized")
            except ValueError:
                # Initialize Firebase app with credentials
                # Use the service account file if it exists, otherwise use default credentials
                if os.path.exists('firebase_credentials.json'):
                    cred = credentials.Certificate('firebase_credentials.json')
                    firebase_admin.initialize_app(cred)
                    print("Firebase app initialized with service account from firebase_credentials.json")
                else:
                    # Use default credentials (for testing)
                    firebase_admin.initialize_app()
                    print("Firebase app initialized with default credentials")
            
            # Get Firestore database
            self.db = firestore.client()
            self.connected = True
            print("Firestore connected successfully")
            
            # Test connection
            self._test_connection()
        except Exception as e:
            print(f"Error connecting to Firestore: {str(e)}")
            self.connected = False
    
    def _test_connection(self):
        """Test the Firestore connection by writing and reading a test document"""
        try:
            # Create a test collection
            test_ref = self.db.collection('test').document('connection-test')
            
            # Write test data
            test_data = {
                'timestamp': firestore.SERVER_TIMESTAMP,
                'test': True
            }
            test_ref.set(test_data)
            
            # Read it back to confirm
            test_doc = test_ref.get()
            if test_doc.exists:
                print("Firestore connection test successful")
            else:
                print("Firestore connection test failed - couldn't read test document")
        except Exception as e:
            print(f"Error testing Firestore connection: {str(e)}")
    
    def save_report(self, title, description, image_path, query, metrics):
        """
        Save a report to Firestore
        
        Args:
            title (str): Report title
            description (str): Report description
            image_path (str): Path to report image (optional)
            query (str): JSON string of query parameters
            metrics (str): Analysis metrics text
            
        Returns:
            str: Report ID if successful, None otherwise
        """
        if not self.connected:
            print("Firestore not connected")
            return None
        
        try:
            # Create a new document in the reports collection
            reports_ref = self.db.collection('reports')
            
            # Debug info
            print(f"Preparing to save report with title: {title}")
            print(f"Title length: {len(title)}")
            print(f"Description length: {len(description)}")
            print(f"Query length: {len(query)}")
            print(f"Metrics length: {len(metrics)}")
            
            # Prepare the document data
            doc_data = {
                'title': title,
                'description': description,
                'image_path': image_path,
                'query': query,
                'metrics': metrics,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            # Add the document to Firestore - using the set method with auto ID
            doc_id = str(uuid.uuid4())
            doc_ref = reports_ref.document(doc_id)
            doc_ref.set(doc_data)
            
            # Verify the document was saved
            verification = doc_ref.get()
            if verification.exists:
                print(f"Report saved and verified successfully with ID: {doc_id}")
                return doc_id
            else:
                print("Failed to verify saved document")
                return None
        except Exception as e:
            print(f"Error saving report to Firestore: {str(e)}")
            traceback.print_exc()
            return None
    
    def get_report(self, report_id):
        """
        Get a report from Firestore
        
        Args:
            report_id (str): Report ID
            
        Returns:
            dict: Report data if successful, None otherwise
        """
        if not self.connected:
            print("Firestore not connected")
            return None
        
        try:
            # Get document from Firestore
            doc_ref = self.db.collection('reports').document(report_id)
            doc = doc_ref.get()
            
            if doc.exists:
                # Convert Firestore document to dict
                report_data = doc.to_dict()
                # Add the ID to the report data
                report_data['id'] = doc.id
                
                print(f"Report retrieved successfully with ID: {doc.id}")
                return report_data
            else:
                print(f"Report with ID {report_id} not found")
                return None
        except Exception as e:
            print(f"Error getting report from Firestore: {str(e)}")
            return None
    
    def get_all_reports(self, limit=50):
        """
        Get all reports from Firestore
        
        Args:
            limit (int): Maximum number of reports to retrieve
            
        Returns:
            list: List of reports if successful, empty list otherwise
        """
        if not self.connected:
            print("Firestore not connected")
            return []
        
        try:
            # Get all documents from reports collection
            reports_ref = self.db.collection('reports').order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            docs = reports_ref.stream()
            
            # Convert Firestore documents to list of dicts
            reports = []
            for doc in docs:
                report_data = doc.to_dict()
                # Add the ID to the report data
                report_data['id'] = doc.id
                reports.append(report_data)
            
            print(f"Retrieved {len(reports)} reports from Firestore")
            return reports
        except Exception as e:
            print(f"Error getting reports from Firestore: {str(e)}")
            return []
    
    def delete_report(self, report_id):
        """
        Delete a report from Firestore
        
        Args:
            report_id (str): Report ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            print("Firestore not connected")
            return False
        
        try:
            # Delete document from Firestore
            self.db.collection('reports').document(report_id).delete()
            
            print(f"Report deleted successfully with ID: {report_id}")
            return True
        except Exception as e:
            print(f"Error deleting report from Firestore: {str(e)}")
            return False
            
# Create a singleton instance
firestore_db = FirestoreHelper() 