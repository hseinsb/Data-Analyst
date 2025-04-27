import datetime
import os
import json
import pyrebase
from dotenv import load_dotenv
import uuid
import traceback
import random
import string
import time
import requests

# Load environment variables
load_dotenv()

# Local storage path
LOCAL_STORAGE_PATH = "reports_data.json"

class FirebaseAPI:
    """Firebase API for storing and retrieving TikTok analysis reports"""
    
    def __init__(self):
        """Initialize Firebase connection"""
        self.connected = False
        self.db = None
        self.using_local_storage = False
        
        try:
            # Configure Firebase with complete configuration
            firebase_config = {
                "apiKey": os.getenv("FIREBASE_API_KEY", "AIzaSyCS8oRXqvcdimyq78rhcA4qqP3teJCHdD8"),
                "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "data-analyst-70798.firebaseapp.com"),
                "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "https://data-analyst-70798-default-rtdb.firebaseio.com"),
                "projectId": os.getenv("FIREBASE_PROJECT_ID", "data-analyst-70798"),
                "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "data-analyst-70798.firebasestorage.app"),
                "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "121511955321"),
                "appId": os.getenv("FIREBASE_APP_ID", "1:121511955321:web:ef19591062b1ba9f223da8")
            }
            
            # Ensure the database URL is set
            if not firebase_config["databaseURL"]:
                print("WARNING: databaseURL is not set in config, using default")
                firebase_config["databaseURL"] = "https://data-analyst-70798-default-rtdb.firebaseio.com"
            
            print(f"Connecting to Firebase database at: {firebase_config['databaseURL']}")
            
            # Initialize Firebase
            self.firebase = pyrebase.initialize_app(firebase_config)
            self.auth = self.firebase.auth()
            
            # Try authenticating anonymously if supported, otherwise proceed without authentication
            try:
                print("Attempting to sign in anonymously to Firebase...")
                # Anonymous sign-in (if your project has it enabled)
                # If this fails, we'll still try to use the database
                anonymous_user = self.auth.sign_in_anonymous()
                print(f"Anonymous sign-in successful: {anonymous_user}")
            except Exception as auth_error:
                print(f"Anonymous authentication failed: {str(auth_error)}")
                print("Will attempt to access database without authentication...")
            
            # Use database method for Realtime Database
            self.db = self.firebase.database()
            
            # Verify database connection by using REST API directly with auth=None to bypass authentication
            try:
                # Create a test node
                test_path = "test_connection"
                test_data = {"timestamp": time.time()}
                
                print("Testing database connection with direct write...")
                db_url = f"{firebase_config['databaseURL']}/{test_path}.json"
                response = requests.put(db_url, json=test_data)
                
                if response.status_code == 200:
                    print(f"Database connection test successful with direct REST API: {response.json()}")
                    self.connected = True
                    print("Firebase database successfully connected and tested")
                else:
                    print(f"Database connection test failed: {response.status_code} - {response.text}")
                    raise Exception(f"Database REST API test failed: {response.status_code} - {response.text}")
            except Exception as test_error:
                print(f"Database connection test failed: {str(test_error)}")
                raise test_error
                
        except Exception as e:
            print(f"Error connecting to Firebase database: {str(e)}")
            print("Falling back to local storage")
            self.using_local_storage = True
            self._initialize_local_storage()
            self.connected = True
    
    def _initialize_local_storage(self):
        """Initialize local storage for reports"""
        try:
            # Convert to absolute path to avoid path issues
            abs_path = os.path.abspath(LOCAL_STORAGE_PATH)
            directory = os.path.dirname(abs_path)
            
            # Check if directory exists, create if it doesn't
            if directory and not os.path.exists(directory):
                print(f"Creating directory: {directory}")
                try:
                    os.makedirs(directory, exist_ok=True)
                    print(f"Directory created successfully: {directory}")
                except PermissionError:
                    print(f"ERROR: Permission denied creating directory: {directory}")
                    print("Please check that you have write access to this location")
                    return False
            
            # Always create saved_reports directory for local file storage
            saved_reports_dir = "saved_reports"
            if not os.path.exists(saved_reports_dir):
                print(f"Creating saved_reports directory")
                try:
                    os.makedirs(saved_reports_dir, exist_ok=True)
                    print(f"saved_reports directory created successfully")
                except Exception as dir_error:
                    print(f"Error creating saved_reports directory: {str(dir_error)}")
            
            # Check if the file exists, create it if it doesn't
            if not os.path.exists(abs_path):
                print(f"Creating local storage file: {abs_path}")
                try:
                    with open(abs_path, 'w') as f:
                        json.dump({"reports": {}}, f, indent=2)
                    print(f"Local storage file created successfully")
                except PermissionError:
                    print(f"ERROR: Permission denied creating file: {abs_path}")
                    print("Please check that you have write access to this location")
                    return False
            
            # Verify read/write access
            try:
                # Test read access
                with open(abs_path, 'r') as f:
                    data = json.load(f)
                
                # Make sure reports key exists
                if "reports" not in data:
                    data["reports"] = {}
                
                # Test write access by writing the same data back
                with open(abs_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"Local storage is properly initialized with read/write access at: {abs_path}")
                return True
            except PermissionError as pe:
                print(f"Permission error accessing local storage: {str(pe)}")
                print(f"Please check file permissions for: {abs_path}")
                return False
            except json.JSONDecodeError as je:
                print(f"Error reading local storage JSON: {str(je)}")
                print(f"Reinitializing local storage with empty structure")
                try:
                    with open(abs_path, 'w') as f:
                        json.dump({"reports": {}}, f, indent=2)
                    return True
                except Exception as write_error:
                    print(f"Failed to reinitialize local storage: {str(write_error)}")
                    return False
        except Exception as e:
            print(f"Error initializing local storage: {str(e)}")
            traceback.print_exc()
            return False
    
    def _load_local_data(self):
        """Load data from local storage"""
        try:
            with open(LOCAL_STORAGE_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading local data: {str(e)}")
            return {"reports": {}}
    
    def _save_local_data(self, data):
        """Save data to local storage"""
        try:
            with open(LOCAL_STORAGE_PATH, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving local data: {str(e)}")
    
    def is_connected(self):
        """Check if Firebase is connected"""
        return self.connected
    
    def save_report(self, title, description, image_path, query, metrics):
        """Save a report to Firebase or local storage as fallback"""
        print(f"Attempting to save report: {title}")
        
        try:
            # First, ensure we have a properly initialized database connection
            if not self.db:
                print("ERROR: Database connection is not initialized")
                # Try to reinitialize the connection
                self.db = self.firebase.database()
                if not self.db:
                    raise Exception("Database connection failed, even after reinitialization")
            
            # Prepare the document data
            doc_id = str(uuid.uuid4())
            doc_data = {
                'title': title,
                'description': description,
                'image_path': image_path,
                'query': query,
                'metrics': metrics,
                'created_at': time.time(),
                'id': doc_id
            }
            
            print(f"Document data prepared: {doc_id}")
            print(f"Data size: title={len(title)}, description={len(description)}, query={len(query)}, metrics={len(metrics)}")
            
            # Try multiple approaches to save the data
            
            # Approach 1: Using the Pyrebase library
            try:
                print("Attempting write using Pyrebase...")
                # First create 'reports' node if it doesn't exist
                self.db.child("reports").child("initialized").set(True)
                
                # Then write the report data
                result = self.db.child("reports").child(doc_id).set(doc_data)
                print(f"Pyrebase write result: {result}")
                
                # Verify the write worked by trying to read back the data
                verify = self.db.child("reports").child(doc_id).get()
                verify_data = verify.val()
                if verify_data:
                    print("Verification successful - data was saved correctly using Pyrebase")
                    return doc_id
                else:
                    print("WARNING: Verification failed - could not read back saved data")
                    raise Exception("Verification failed for Pyrebase write")
            except Exception as pyrebase_error:
                print(f"Pyrebase write failed: {str(pyrebase_error)}")
                print("Trying alternate method...")
            
            # Approach 2: Using REST API directly
            try:
                print("Attempting write using direct REST API...")
                import requests
                
                # Get database URL from the configuration
                db_url = self.firebase._db_url
                
                # First, ensure the reports node exists
                reports_init_url = f"{db_url}/reports/initialized.json"
                init_response = requests.put(reports_init_url, json=True)
                
                if init_response.status_code != 200:
                    print(f"Failed to initialize reports node: {init_response.status_code} - {init_response.text}")
                
                # Save the report data
                save_url = f"{db_url}/reports/{doc_id}.json"
                response = requests.put(save_url, json=doc_data)
                
                if response.status_code == 200:
                    print(f"REST API write successful: {response.json()}")
                    
                    # Verify by reading back
                    verify_url = f"{db_url}/reports/{doc_id}.json"
                    verify_response = requests.get(verify_url)
                    
                    if verify_response.status_code == 200 and verify_response.json():
                        print("Verification successful - data was saved correctly using REST API")
                        return doc_id
                    else:
                        print(f"REST API verification failed: {verify_response.status_code} - {verify_response.text}")
                        raise Exception("Verification failed for REST API write")
                else:
                    print(f"REST API write failed: {response.status_code} - {response.text}")
                    raise Exception(f"REST API write failed: {response.status_code} - {response.text}")
            except Exception as rest_error:
                print(f"REST API write failed: {str(rest_error)}")
                raise rest_error
                
        except Exception as e:
            # Log the error
            print(f"Error saving to Firebase: {str(e)}")
            print(f"Error type: {type(e)}")
            traceback.print_exc()
            
            # Fall back to local storage
            print("Falling back to local storage...")
            try:
                # Check if reports_data.json file exists and can be accessed
                print(f"TEST: Checking if {LOCAL_STORAGE_PATH} exists")
                file_exists = os.path.exists(LOCAL_STORAGE_PATH)
                print(f"TEST: File exists: {file_exists}")
                
                # Try to write a test file to the same directory
                test_file_path = "test_write_access.txt"
                try:
                    with open(test_file_path, 'w') as f:
                        f.write(f"Test write at {datetime.datetime.now()}")
                    print(f"TEST: Successfully wrote to test file: {test_file_path}")
                    os.remove(test_file_path)  # Clean up
                    print(f"TEST: Successfully cleaned up test file")
                except Exception as test_write_error:
                    print(f"TEST: Failed to write test file: {str(test_write_error)}")
                
                # Load existing data
                if not os.path.exists(LOCAL_STORAGE_PATH):
                    print("TEST: Local storage file doesn't exist, initializing it")
                    self._initialize_local_storage()
                else:
                    print("TEST: Local storage file exists, loading it")
                    
                with open(LOCAL_STORAGE_PATH, 'r') as f:
                    try:
                        data = json.load(f)
                        print(f"TEST: Successfully loaded JSON data: {json.dumps(data)[:100]}...")
                    except json.JSONDecodeError:
                        print("Error parsing local storage JSON, reinitializing...")
                        data = {"reports": {}}
                
                # Add the report
                if 'reports' not in data:
                    print("TEST: 'reports' key not found in data, adding it")
                    data['reports'] = {}
                    
                data['reports'][doc_id] = doc_data
                print(f"TEST: Added report with ID: {doc_id}")
                
                # Save back to file
                print(f"TEST: Saving updated data back to {LOCAL_STORAGE_PATH}")
                with open(LOCAL_STORAGE_PATH, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"Report saved successfully to local storage with ID: {doc_id}")
                
                # Verify the save worked
                try:
                    with open(LOCAL_STORAGE_PATH, 'r') as f:
                        verify_data = json.load(f)
                    
                    if doc_id in verify_data.get('reports', {}):
                        print(f"TEST: Verification successful - report found in local storage")
                    else:
                        print(f"TEST: Verification failed - report not found in local storage")
                except Exception as verify_error:
                    print(f"TEST: Verification failed with error: {str(verify_error)}")
                
                return doc_id
            except Exception as local_error:
                print(f"Error saving to local storage: {str(local_error)}")
                traceback.print_exc()
                return None
    
    def get_report(self, report_id):
        """
        Get a report from Firebase
        
        Args:
            report_id (str): Report ID
            
        Returns:
            dict: Report data if successful, None otherwise
        """
        if not self.is_connected():
            print("Firebase not connected")
            return None
        
        try:
            # If using local storage
            if self.using_local_storage:
                return self._get_report_local(report_id)
                
            print(f"Attempting to get report with ID: {report_id}")
            
            # Approach 1: Try using Pyrebase
            try:
                # Get the document
                result = self.db.child("reports").child(report_id).get()
                data = result.val()
                
                if data:
                    print(f"Successfully retrieved report using Pyrebase: {report_id}")
                    return data
                else:
                    print(f"Report with ID {report_id} not found using Pyrebase")
                    # Try REST API approach
                    raise Exception(f"Report not found or authentication issue")
            except Exception as pyrebase_error:
                print(f"Error getting report with Pyrebase: {str(pyrebase_error)}")
                print("Trying REST API method...")
            
            # Approach 2: Try using REST API directly
            try:
                import requests
                
                # Get database URL
                db_url = self.firebase._db_url
                report_url = f"{db_url}/reports/{report_id}.json"
                
                response = requests.get(report_url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        print(f"Successfully retrieved report using REST API: {report_id}")
                        return data
                    else:
                        print(f"Report with ID {report_id} not found using REST API")
                        return None
                else:
                    print(f"Error getting report with REST API: {response.status_code} - {response.text}")
                    # Fallback to local storage
                    return self._get_report_local(report_id)
            except Exception as rest_error:
                print(f"Error getting report with REST API: {str(rest_error)}")
                # Fallback to local storage
                return self._get_report_local(report_id)
                
        except Exception as e:
            print(f"Error getting report from Firebase: {str(e)}")
            traceback.print_exc()
            
            # Fallback to local storage
            return self._get_report_local(report_id)
    
    def _get_report_local(self, report_id):
        """Get report from local storage"""
        try:
            # Load data
            data = self._load_local_data()
            
            # Get the report
            report = data["reports"].get(report_id)
            
            if report:
                return report
            else:
                print(f"Report with ID {report_id} not found in local storage")
                return None
        except Exception as e:
            print(f"Error getting report from local storage: {str(e)}")
            traceback.print_exc()
            return None
    
    def get_all_reports(self, limit=50):
        """
        Get all reports from Firebase
        
        Args:
            limit (int): Maximum number of reports to retrieve
            
        Returns:
            list: List of reports if successful, empty list otherwise
        """
        if not self.is_connected():
            print("Firebase not connected")
            return []
        
        try:
            # If using local storage
            if self.using_local_storage:
                return self._get_all_reports_local(limit)
                
            print("Attempting to get all reports from Firebase")
            
            # Approach 1: Try using Pyrebase first
            try:
                # Get all reports
                results = self.db.child("reports").get()
                reports = []
                
                # Check if we got any results
                if results.val() is None:
                    print("No reports found in database using Pyrebase")
                    # This might be due to authentication issues, try REST API instead
                    raise Exception("No reports found or authentication issue")
                    
                # Convert to list of dictionaries with ID
                if results.each():
                    for report in results.each():
                        if report.val() and isinstance(report.val(), dict) and report.key() != "initialized":
                            report_data = report.val()
                            report_data['id'] = report.key()  # Ensure ID is included
                            reports.append(report_data)
                
                print(f"Found {len(reports)} reports in Firebase using Pyrebase")
                
                # Sort by created_at (descending)
                reports.sort(key=lambda x: x.get("created_at", 0), reverse=True)
                
                # Apply limit
                return reports[:limit]
            except Exception as pyrebase_error:
                print(f"Error getting reports with Pyrebase: {str(pyrebase_error)}")
                print("Trying REST API method...")
            
            # Approach 2: Try using REST API directly
            try:
                import requests
                
                # Get database URL
                db_url = self.firebase._db_url
                reports_url = f"{db_url}/reports.json"
                
                response = requests.get(reports_url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, dict):
                        # Remove the 'initialized' node if present
                        if "initialized" in data:
                            del data["initialized"]
                        
                        # Convert to list
                        reports = []
                        for report_id, report_data in data.items():
                            if isinstance(report_data, dict):
                                # Ensure ID is included in the report data
                                report_data['id'] = report_id
                                reports.append(report_data)
                        
                        print(f"Found {len(reports)} reports in Firebase using REST API")
                        
                        # Sort by created_at (descending)
                        reports.sort(key=lambda x: x.get("created_at", 0), reverse=True)
                        
                        # Apply limit
                        return reports[:limit]
                    else:
                        print("No reports found or invalid data structure from REST API")
                        return []
                else:
                    print(f"Error getting reports with REST API: {response.status_code} - {response.text}")
                    # Fallback to local storage
                    return self._get_all_reports_local(limit)
            except Exception as rest_error:
                print(f"Error getting reports with REST API: {str(rest_error)}")
                # Fallback to local storage
                return self._get_all_reports_local(limit)
        except Exception as e:
            print(f"Error getting reports from Firebase: {str(e)}")
            traceback.print_exc()
            
            # Fallback to local storage
            return self._get_all_reports_local(limit)
    
    def _get_all_reports_local(self, limit=50):
        """Get all reports from local storage"""
        try:
            # Load data
            data = self._load_local_data()
            
            # Convert to list of dictionaries with ID
            reports = []
            for report_id, report_data in data["reports"].items():
                report_data['id'] = report_id  # Ensure ID is included
                reports.append(report_data)
            
            print(f"Found {len(reports)} reports in local storage")
            
            # Sort by created_at (descending)
            reports.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            
            # Apply limit
            return reports[:limit]
        except Exception as e:
            print(f"Error getting reports from local storage: {str(e)}")
            traceback.print_exc()
            return []
    
    def delete_report(self, report_id):
        """
        Delete a report from Firebase
        
        Args:
            report_id (str): Report ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            print("Firebase not connected")
            return False
        
        try:
            # If using local storage
            if self.using_local_storage:
                return self._delete_report_local(report_id)
                
            print(f"Attempting to delete report with ID: {report_id}")
            
            # Approach 1: Try using Pyrebase
            try:
                # Delete the document
                self.db.child("reports").child(report_id).remove()
                print(f"Successfully deleted report with Pyrebase: {report_id}")
                return True
            except Exception as pyrebase_error:
                print(f"Error deleting report with Pyrebase: {str(pyrebase_error)}")
                print("Trying REST API method...")
            
            # Approach 2: Try using REST API directly
            try:
                import requests
                
                # Get database URL
                db_url = self.firebase._db_url
                delete_url = f"{db_url}/reports/{report_id}.json"
                
                response = requests.delete(delete_url)
                
                if response.status_code == 200:
                    print(f"Successfully deleted report with REST API: {report_id}")
                    return True
                else:
                    print(f"Error deleting report with REST API: {response.status_code} - {response.text}")
                    # Fallback to local storage
                    return self._delete_report_local(report_id)
            except Exception as rest_error:
                print(f"Error deleting report with REST API: {str(rest_error)}")
                # Fallback to local storage
                return self._delete_report_local(report_id)
                
        except Exception as e:
            print(f"Error deleting report from Firebase: {str(e)}")
            traceback.print_exc()
            
            # Fallback to local storage
            return self._delete_report_local(report_id)
    
    def _delete_report_local(self, report_id):
        """Delete report from local storage"""
        try:
            # Load data
            data = self._load_local_data()
            
            # Check if report exists
            if report_id not in data["reports"]:
                print(f"Report with ID {report_id} not found in local storage")
                return False
            
            # Delete the report
            del data["reports"][report_id]
            
            # Save the updated data
            self._save_local_data(data)
            
            print(f"Successfully deleted report from local storage with ID: {report_id}")
            return True
        except Exception as e:
            print(f"Error deleting report from local storage: {str(e)}")
            traceback.print_exc()
            return False 