import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
import json
import datetime
import os

def save_test_report():
    """Save a test report directly to Firestore"""
    print("Starting test report save to Firestore...")
    
    # Initialize Firebase if not already initialized
    try:
        app = firebase_admin.get_app()
        print("Firebase already initialized")
    except ValueError:
        # Initialize Firebase with credentials
        if os.path.exists('firebase_credentials.json'):
            cred = credentials.Certificate('firebase_credentials.json')
            firebase_admin.initialize_app(cred)
            print("Firebase initialized with credentials from firebase_credentials.json")
        else:
            print("ERROR: firebase_credentials.json not found!")
            return False
    
    # Get Firestore client
    db = firestore.client()
    
    # Create test report data
    report_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    
    test_data = {
        'id': report_id,
        'title': f"Test Report {timestamp}",
        'description': "This is a test report created directly",
        'image_path': "",
        'query': json.dumps({'test': True, 'views': 1000, 'likes': 100}),
        'metrics': "Test metrics content for this report",
        'created_at': firestore.SERVER_TIMESTAMP
    }
    
    print(f"Prepared test report data with ID: {report_id}")
    
    try:
        # Save to Firestore
        db.collection('reports').document(report_id).set(test_data)
        print(f"Test report saved with ID: {report_id}")
        
        # Verify it was saved
        doc = db.collection('reports').document(report_id).get()
        if doc.exists:
            print("Verification successful - document exists in Firestore")
            print(f"Document data: {doc.to_dict()}")
            return True
        else:
            print("ERROR: Verification failed - document does not exist in Firestore")
            return False
    except Exception as e:
        print(f"ERROR saving test report: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = save_test_report()
    if success:
        print("\nTEST PASSED: Successfully saved report to Firestore")
    else:
        print("\nTEST FAILED: Could not save report to Firestore") 