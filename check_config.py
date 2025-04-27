import os
import json
import sys

def check_firebase_credentials():
    """Check if firebase_credentials.json exists and has valid content"""
    print("Checking Firebase credentials...")
    
    # Check if file exists
    if not os.path.exists('firebase_credentials.json'):
        print("ERROR: firebase_credentials.json file not found!")
        print("Please follow the steps in SETUP_FIRESTORE.md to create and download this file.")
        return False
    
    # Try to read and parse the file
    try:
        with open('firebase_credentials.json', 'r') as f:
            creds = json.load(f)
        
        # Check if it contains placeholder values
        if 'your-project-id' in creds.get('project_id', ''):
            print("ERROR: firebase_credentials.json contains placeholder values!")
            print("Please replace with your actual Firebase credentials.")
            return False
        
        # Check if it has the required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"ERROR: firebase_credentials.json is missing required fields: {', '.join(missing_fields)}")
            return False
        
        # Basic validation passed
        print("✅ firebase_credentials.json exists and appears to be valid.")
        print(f"Project ID: {creds.get('project_id')}")
        print(f"Client Email: {creds.get('client_email')}")
        return True
    
    except json.JSONDecodeError:
        print("ERROR: firebase_credentials.json is not valid JSON!")
        return False
    except Exception as e:
        print(f"ERROR reading firebase_credentials.json: {str(e)}")
        return False

def list_project_files():
    """List important project files"""
    print("\nChecking project files...")
    
    key_files = [
        'app.py',
        'firestore_helper.py',
        'test_firestore.py',
        'firebase_credentials.json',
        'SETUP_FIRESTORE.md'
    ]
    
    for file in key_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
    
    # List all .py files in the directory
    print("\nAll Python files in directory:")
    for file in os.listdir('.'):
        if file.endswith('.py'):
            print(f"- {file}")

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    check_firebase_credentials()
    list_project_files()
    
    print("\nIf there are any errors, please follow the instructions in SETUP_FIRESTORE.md.")
    print("If all checks pass but the app still doesn't work, try running 'py test_firestore.py' directly.") 