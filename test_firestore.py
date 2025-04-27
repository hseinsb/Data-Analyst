import os
import json
from firestore_helper import firestore_db

def test_firestore_connection():
    """Test connection to Firestore"""
    print("Testing Firestore connection...")
    print(f"Connected: {firestore_db.connected}")
    
    # If not connected, check if the credentials file exists
    if not firestore_db.connected:
        if os.path.exists('firebase_credentials.json'):
            print("Credentials file exists, but connection failed.")
            # Check if the credentials file is valid
            try:
                with open('firebase_credentials.json', 'r') as f:
                    creds = json.load(f)
                if 'your-project-id' in creds.get('project_id', ''):
                    print("Credentials file contains placeholder values. Please update with your actual credentials.")
            except Exception as e:
                print(f"Error reading credentials file: {str(e)}")
        else:
            print("Credentials file not found.")
    
    return firestore_db.connected

def test_save_report():
    """Test saving a report to Firestore"""
    if not firestore_db.connected:
        print("Cannot save report: Firestore not connected")
        return None
        
    print("Testing saving a report to Firestore...")
    
    # Test data
    test_data = {
        'title': 'Test Report',
        'description': 'This is a test report',
        'image_path': '',
        'query': json.dumps({'test': True, 'params': {'views': 1000, 'likes': 100}}),
        'metrics': 'This is test metrics data'
    }
    
    # Save report
    report_id = firestore_db.save_report(
        test_data['title'],
        test_data['description'],
        test_data['image_path'],
        test_data['query'],
        test_data['metrics']
    )
    
    if report_id:
        print(f"Successfully saved test report with ID: {report_id}")
    else:
        print("Failed to save test report")
    
    return report_id

def test_get_reports():
    """Test getting reports from Firestore"""
    if not firestore_db.connected:
        print("Cannot get reports: Firestore not connected")
        return
        
    print("Testing getting reports from Firestore...")
    
    # Get all reports
    reports = firestore_db.get_all_reports()
    
    if reports:
        print(f"Retrieved {len(reports)} reports")
        # Print the first report
        if len(reports) > 0:
            print("First report:")
            print(f"  ID: {reports[0].get('id')}")
            print(f"  Title: {reports[0].get('title')}")
            print(f"  Description: {reports[0].get('description')[:50]}...")
    else:
        print("No reports found or error retrieving reports")
    
    return reports

if __name__ == "__main__":
    # Test connection
    connected = test_firestore_connection()
    
    if connected:
        # Save a test report
        report_id = test_save_report()
        
        # Get all reports
        reports = test_get_reports()
        
        # If we saved a report and there are reports, test deleting the report we just saved
        if report_id and reports:
            print(f"Testing deleting report with ID: {report_id}")
            success = firestore_db.delete_report(report_id)
            
            if success:
                print(f"Successfully deleted report with ID: {report_id}")
            else:
                print(f"Failed to delete report with ID: {report_id}")
    else:
        print("Firestore connection failed, skipping further tests") 