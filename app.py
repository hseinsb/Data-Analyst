import streamlit as st
import pandas as pd
import os
from sheets_api import SheetsAPI
from openai_api import OpenAIAPI
from analyzer import TikTokAnalyzer
from firebase_auth import FirebaseAuth
# Import Firestore helper instead of Firebase API
from firestore_helper import firestore_db
import utils
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
# Import the direct save and retrieve functions
from direct_save import direct_save_to_firestore, direct_get_all_reports, direct_get_report, direct_delete_report
import time
import uuid

# Set up logging to a file
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Application started")

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="TikTok Content Performance Analyst",
    page_icon="🧠",
    layout="wide"
)

# Admin UID - Only this user will be allowed to access the app
ADMIN_UID = "c88yBt47V0Taddds4nkmzL4Da1i1"

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize session state for saved reports
if 'saved_reports' not in st.session_state:
    st.session_state.saved_reports = []

# Initialize session state for active tab
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Google Sheets Analysis"

def initialize_apis():
    """Initialize API connections and return status"""
    # Initialize Google Sheets API
    sheets_api = SheetsAPI()
    sheets_connected = sheets_api.is_connected()
    
    # Initialize OpenAI API
    openai_api = OpenAIAPI()
    openai_connected = openai_api.is_connected()
    
    # Initialize Firebase Authentication
    firebase_auth = FirebaseAuth()
    auth_initialized = firebase_auth.is_initialized()
    
    # Check Firestore connection status
    firestore_connected = firestore_db.connected
    
    # Create analyzer if both APIs are connected
    analyzer = None
    if sheets_connected and openai_connected:
        analyzer = TikTokAnalyzer(sheets_api, openai_api)
        
    return sheets_connected, openai_connected, auth_initialized, firestore_connected, sheets_api, openai_api, firebase_auth, firestore_db, analyzer

def render_login():
    """Render login form"""
    st.title("🧠 TikTok Content Performance Analyst")
    st.markdown("---")
    st.subheader("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password")
                return
            
            with st.spinner("Logging in..."):
                user, error = firebase_auth.login(email, password)
                
                if user:
                    # Check if user has admin access
                    if firebase_auth.check_admin_access(user['idToken'], ADMIN_UID):
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("You don't have access to this application")
                else:
                    st.error(f"Login failed: {error}")

def render_sidebar():
    """Render sidebar content"""
    st.sidebar.title("🧠 TikTok Content Analyst")
    st.sidebar.markdown("---")
    
    # User info
    if st.session_state.authenticated and st.session_state.user:
        st.sidebar.success("✅ Logged in")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # Credentials status
    st.sidebar.subheader("API Status")
    
    if sheets_connected:
        st.sidebar.success("✅ Google Sheets API Connected")
    else:
        st.sidebar.error("❌ Google Sheets API Not Connected")
        st.sidebar.markdown("""
        Please ensure:
        1. `credentials.json` exists in project root
        2. Google Sheets API is enabled in Google Cloud
        """)
    
    if openai_connected:
        st.sidebar.success("✅ OpenAI API Connected")
    else:
        st.sidebar.error("❌ OpenAI API Not Connected")
        st.sidebar.markdown("""
        Please ensure:
        1. OpenAI API key is correct
        """)
    
    if auth_initialized:
        st.sidebar.success("✅ Firebase Authentication Connected")
    else:
        st.sidebar.error("❌ Firebase Authentication Not Connected")
        st.sidebar.markdown("""
        Please ensure:
        1. Firebase config is correct in .env file
        """)
        
    if firestore_connected:
        st.sidebar.success("✅ Firestore Database Connected")
    else:
        st.sidebar.error("❌ Firestore Database Not Connected")
        st.sidebar.markdown("""
        Please ensure:
        1. Firebase config is correct in .env file
        """)
    
    st.sidebar.markdown("---")
    
    # Saved Reports section
    if st.session_state.saved_reports:
        st.sidebar.subheader("Saved Reports")
        for i, (report_id, title) in enumerate(st.session_state.saved_reports):
            st.sidebar.markdown(f"{i+1}. {title} (ID: {report_id[:8]}...)")
    
    # Instructions
    st.sidebar.subheader("Instructions")
    st.sidebar.markdown("""
    1. Enter the row number (0-based) of the video you want to analyze
    2. Click "Analyze Video"
    3. View the detailed analysis
    4. Save to Firebase or download as CSV
    
    Note: Row 0 is the first data row (after the header)
    """)

def render_manual_input_form():
    """Render manual input form for analyzing a single video"""
    st.subheader("📝 Analyze Single Video")
    
    # Create a form for video data
    with st.form("video_data_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title_hook = st.text_area("Title/Hook", height=100)
            caption = st.text_area("Caption", height=100)
            hashtags = st.text_input("Hashtags (optional)")
            notes = st.text_input("Notes (Topic/Emotion) (optional)")
            
        with col2:
            views = st.number_input("Views (24h)", min_value=0, step=1)
            likes = st.number_input("Likes", min_value=0, step=1)
            comments = st.number_input("Comments", min_value=0, step=1)
            saves = st.number_input("Saves", min_value=0, step=1)
            
        # Submit button
        submitted = st.form_submit_button("Analyze Video")
        
    # Handle form submission
    if submitted:
        if not title_hook or views == 0:
            st.error("Please provide at least a title/hook and number of views.")
            return
            
        # Create video data dictionary
        video_data = {
            "Title": title_hook,
            "Hook": title_hook,
            "Caption": caption,
            "Hashtags": hashtags,
            "Views": views,
            "Likes": likes,
            "Comments": comments,
            "Saves": saves,
            "Notes": notes
        }
        
        # Analyze video
        with st.spinner("Analyzing video..."):
            report = analyzer.analyze_single_video(video_data)
            
        # Display formatted report
        st.subheader("📊 Analysis Report")
        formatted_report = utils.format_report_for_display(report)
        st.markdown(formatted_report)
        
        # Create a simple save and download section
        st.subheader("Save or Download Report")
        col1, col2 = st.columns(2)
        
        # Download button
        with col1:
            report_csv = pd.DataFrame([{**video_data, "Analysis Report": report}])
            st.download_button(
                label="Download Report as CSV",
                data=report_csv.to_csv(index=False),
                file_name="tiktok_analysis_report.csv",
                mime="text/csv"
            )
        
        # Save button - direct implementation
        with col2:
            if st.button("Save to Database", key="save_direct"):
                with st.spinner("Saving report to database..."):
                    try:
                        # Save directly to Firestore
                        title = video_data.get("Title", "")
                        description = video_data.get("Caption", "")
                        
                        # Log attempt
                        logger.info(f"Attempting direct save for title: {title}")
                        
                        # Call the direct save function
                        report_id = direct_save_to_firestore(
                            title=title,
                            description=description,
                            report_content=report,
                            report_data=video_data
                        )
                        
                        if report_id:
                            st.success(f"Report saved successfully! ID: {report_id}")
                            
                            # Force refresh of the saved reports to show the new one
                            if st.button("View Saved Reports"):
                                st.session_state.active_tab = "Saved Reports"
                                st.rerun()
                        else:
                            st.error("Failed to save report. Please check logs for details.")
                            
                    except Exception as e:
                        logger.error(f"Error in direct save button handler: {str(e)}", exc_info=True)
                        st.error(f"Error saving report: {str(e)}")

def render_sheets_analysis_form():
    """Render Google Sheets analysis form"""
    st.subheader("📊 Analyze Videos from Google Sheets")
    
    # Check if Google Sheets API is connected
    if not sheets_connected:
        st.error("Google Sheets API is not connected. Please check credentials.")
        st.info("Make sure credentials.json exists in the project root directory.")
        return
    
    # Default Google Sheet URL
    default_url = "https://docs.google.com/spreadsheets/d/1BMpnIDFVeVbk-l2jZEibWwu9XntddlnjVpmnylcf3J4/edit?gid=539928533#gid=539928533"
    sheet_url = st.text_input("Google Sheet URL", value=default_url)
    worksheet_name = st.text_input("Worksheet Name", value="Account A Data")
    
    # Simple row selection
    row_number = st.number_input("Enter Row Number to Analyze (0-based)", min_value=0, value=0, help="0 is the first data row after the header")
    
    # Load data button
    load_data = st.button("Load Sheet Data")
    
    # Store sheet data in session state to prevent reloading
    if 'sheet_data' not in st.session_state:
        st.session_state.sheet_data = None
    
    # Load the data when button is clicked
    if load_data:
        try:
            with st.spinner("Loading sheet data..."):
                print(f"Opening Google Sheet with URL: {sheet_url}")
                sheet = sheets_api.open_sheet_by_url(sheet_url)
                
                if sheet:
                    print(f"Successfully opened Google Sheet, getting worksheet: {worksheet_name}")
                    worksheet = sheets_api.get_worksheet_by_name(sheet, worksheet_name)
                    
                    if worksheet:
                        print(f"Successfully opened worksheet, getting data as DataFrame")
                        sheet_data = sheets_api.get_data_as_dataframe(worksheet)
                        
                        if sheet_data.empty:
                            st.error("No data found in the worksheet.")
                        else:
                            print(f"Successfully loaded data with {len(sheet_data)} rows")
                            print(f"Columns: {sheet_data.columns.tolist()}")
                            
                            st.session_state.sheet_data = sheet_data
                            st.success(f"Loaded {len(sheet_data)} videos from the sheet.")
                    else:
                        st.error(f"Could not find worksheet named '{worksheet_name}'")
                else:
                    st.error("Could not open Google Sheet with the provided URL.")
        except Exception as e:
            st.error(f"Error loading sheet data: {str(e)}")
            print(f"Error loading Google Sheet: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    # Display data preview if available
    if st.session_state.sheet_data is not None:
        # Show a preview of the loaded data (limited columns to prevent display issues)
        display_cols = ['Title/Hook', 'Views (24h)', 'Likes', 'Comments', 'Saves']
        display_cols = [col for col in display_cols if col in st.session_state.sheet_data.columns]
        
        st.subheader("Data Preview")
        st.dataframe(st.session_state.sheet_data[display_cols].head())
        
        # Analyze specific video button
        analyze_video = st.button("Analyze Selected Video")
        
        if analyze_video:
            # Validate row number
            if row_number >= len(st.session_state.sheet_data):
                st.error(f"Row number {row_number} is out of range. Maximum row number is {len(st.session_state.sheet_data)-1}.")
            else:
                # Get the selected row data
                row_data = st.session_state.sheet_data.iloc[row_number]
                
                with st.spinner("Analyzing video..."):
                    # Prepare data for analysis
                    video_data = {}
                    
                    # Extract necessary columns
                    video_data["Title"] = row_data.get("Title/Hook", "")
                    video_data["Hook"] = row_data.get("Title/Hook", "")
                    video_data["Caption"] = row_data.get("Caption", "")
                    video_data["Hashtags"] = row_data.get("Hashtags", "")
                    video_data["Views"] = row_data.get("Views (24h)", 0)
                    video_data["Likes"] = row_data.get("Likes", 0)
                    video_data["Comments"] = row_data.get("Comments", 0)
                    video_data["Saves"] = row_data.get("Saves", 0)
                    video_data["Notes"] = row_data.get("Notes (Topic/Emotion)", "")
                    
                    # Generate analysis
                    report = analyzer.analyze_single_video(video_data)
                
                # Display the video details
                st.subheader(f"Analysis for Video (Row {row_number})")
                st.markdown(f"**Title/Hook:** {video_data['Title']}")
                
                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Views", video_data["Views"])
                with col2:
                    st.metric("Likes", video_data["Likes"])
                with col3:
                    st.metric("Comments", video_data["Comments"])
                with col4:
                    st.metric("Saves", video_data["Saves"])
                
                # Display the analysis report
                st.subheader("📊 Analysis Report")
                formatted_report = utils.format_report_for_display(report)
                st.markdown(formatted_report)
                
                # Create a simple save and download section
                st.subheader("Save or Download Report")
                col1, col2 = st.columns(2)
                
                # Download button
                with col1:
                    st.download_button(
                        label="Download Report as CSV",
                        data=pd.DataFrame([{**video_data, "Analysis Report": report}]).to_csv(index=False),
                        file_name=f"tiktok_analysis_row{row_number}.csv",
                        mime="text/csv"
                    )
                
                # Save button - direct implementation
                with col2:
                    if st.button("Save to Database", key="sheets_save_direct"):
                        with st.spinner("Saving report to database..."):
                            try:
                                # Save directly to Firestore
                                title = video_data.get("Title", "")
                                description = video_data.get("Caption", "")
                                
                                # Log attempt
                                logger.info(f"Attempting direct save for sheets report title: {title}")
                                
                                # Call the direct save function
                                report_id = direct_save_to_firestore(
                                    title=title,
                                    description=description,
                                    report_content=report,
                                    report_data=video_data
                                )
                                
                                if report_id:
                                    st.success(f"Report saved successfully! ID: {report_id}")
                                    
                                    # Force refresh of the saved reports to show the new one
                                    if st.button("View Saved Reports"):
                                        st.session_state.active_tab = "Saved Reports"
                                        st.rerun()
                                else:
                                    st.error("Failed to save report. Please check logs for details.")
                                    
                            except Exception as e:
                                logger.error(f"Error in sheets direct save button handler: {str(e)}", exc_info=True)
                                st.error(f"Error saving report: {str(e)}")

def get_local_file_reports():
    """Get reports from the local file directory"""
    try:
        import os
        import json
        
        reports_dir = "saved_reports"
        if not os.path.exists(reports_dir):
            return []
        
        reports = []
        for filename in os.listdir(reports_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(reports_dir, filename), 'r') as f:
                        report_data = json.load(f)
                        reports.append(report_data)
                except Exception as e:
                    print(f"Error loading report from file {filename}: {str(e)}")
        
        print(f"Found {len(reports)} reports in local file directory")
        return reports
    except Exception as e:
        print(f"Error getting reports from local file directory: {str(e)}")
        return []

def render_saved_reports():
    """Render saved reports tab"""
    st.subheader("💾 Saved Reports")
    
    # Debug information
    st.write("### Debug Information")
    st.write("This section will help diagnose why reports aren't showing up")
    
    # Display Firebase connection status
    try:
        from firebase_api import FirebaseAPI
        firebase_api = FirebaseAPI()
        st.write(f"Firebase connected: {firebase_api.is_connected()}")
        st.write(f"Using local storage: {firebase_api.using_local_storage}")
    except Exception as firebase_error:
        st.error(f"Error checking Firebase connection: {str(firebase_error)}")
    
    # Check Firestore connection
    try:
        import firebase_admin
        from firebase_admin import firestore
        try:
            app = firebase_admin.get_app()
            db = firestore.client()
            st.write("Firestore app initialized and client created successfully")
        except ValueError:
            st.error("Firebase app not initialized")
        except Exception as fs_error:
            st.error(f"Error getting Firestore client: {str(fs_error)}")
    except ImportError:
        st.error("firebase_admin module not available")
    
    # Check saved_reports directory
    import os
    saved_reports_dir = "saved_reports"
    if not os.path.exists(saved_reports_dir):
        st.error(f"Directory {saved_reports_dir} does not exist")
        try:
            os.makedirs(saved_reports_dir)
            st.success(f"Created {saved_reports_dir} directory")
        except Exception as dir_error:
            st.error(f"Error creating directory: {str(dir_error)}")
    else:
        st.write(f"Directory {saved_reports_dir} exists")
        # List files in the directory
        files = os.listdir(saved_reports_dir)
        st.write(f"Files in {saved_reports_dir}: {', '.join(files) if files else 'No files'}")
    
    # Display reports_data.json content
    if os.path.exists("reports_data.json"):
        try:
            with open("reports_data.json", "r") as f:
                import json
                data = json.load(f)
                st.write(f"reports_data.json contains {len(data.get('reports', {}))} reports")
        except Exception as json_error:
            st.error(f"Error reading reports_data.json: {str(json_error)}")
    else:
        st.error("reports_data.json file does not exist")
    
    # Add a separator before the original content
    st.markdown("---")
    
    # Add a refresh button to reload reports
    if st.button("Refresh Reports"):
        with st.spinner("Reloading saved reports..."):
            try:
                # Use direct function to get reports from Firestore
                firestore_reports = direct_get_all_reports()
                
                # Also get reports from local file directory
                local_file_reports = get_local_file_reports()
                
                # Combine reports from both sources
                reports = firestore_reports + local_file_reports
                
                if reports:
                    # Clear existing reports
                    st.session_state.saved_reports = []
                    # Add reports to session state
                    for report in reports:
                        report_id = report.get('id')
                        title = report.get('title', 'Unknown')
                        if report_id:
                            st.session_state.saved_reports.append((report_id, title))
                    st.success(f"Successfully loaded {len(reports)} reports")
                else:
                    st.info("No reports found in database or local files")
            except Exception as e:
                st.error(f"Error refreshing reports: {str(e)}")
                import traceback
                st.error(traceback.format_exc())
    
    # Get all reports directly
    with st.spinner("Loading saved reports..."):
        try:
            # Use direct function to get reports from Firestore
            firestore_reports = direct_get_all_reports()
            logger.info(f"Retrieved {len(firestore_reports)} reports from Firestore directly")
            
            # Also get reports from local file directory
            local_file_reports = get_local_file_reports()
            
            # Combine reports from both sources
            reports = firestore_reports + local_file_reports
            
            if not reports and len(st.session_state.saved_reports) > 0:
                st.warning("Could not load reports from database or local files. Using cached reports.")
                # Try to convert session state reports to the expected format
                reports = []
                for report_id, title in st.session_state.saved_reports:
                    # Try direct Firestore retrieval first
                    single_report = direct_get_report(report_id)
                    if not single_report:
                        # Try local file
                        try:
                            import os
                            import json
                            report_path = f"saved_reports/{report_id}.json"
                            if os.path.exists(report_path):
                                with open(report_path, 'r') as f:
                                    single_report = json.load(f)
                        except Exception as file_error:
                            print(f"Error loading report from file: {str(file_error)}")
                    
                    if single_report:
                        reports.append(single_report)
        except Exception as e:
            st.error(f"Error loading reports: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            reports = []
    
    if not reports:
        st.info("No saved reports found. Try saving a report first.")
        return
    
    # Create a table with report overview
    st.write(f"Found {len(reports)} saved reports")
    
    # Create a DataFrame for display
    report_data = []
    for report in reports:
        # Try to parse video data from query field
        try:
            video_data = json.loads(report.get('query', '{}'))
        except:
            video_data = {}
            
        created_at = report.get('created_at', 'Unknown')
        
        # Format creation date if it's a timestamp
        if hasattr(created_at, 'strftime'):
            created_at = created_at.strftime('%Y-%m-%d %H:%M')
        elif isinstance(created_at, (int, float)):
            # Handle Unix timestamp
            from datetime import datetime
            created_at = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M')
        elif isinstance(created_at, dict) and '_seconds' in created_at:
            # Handle Firestore timestamp format
            from datetime import datetime
            created_at = datetime.fromtimestamp(created_at['_seconds']).strftime('%Y-%m-%d %H:%M')
        
        report_data.append({
            'ID': report.get('id', 'Unknown'),
            'Title': report.get('title', video_data.get('Title', 'Unknown')),
            'Views': video_data.get('Views', 0),
            'Likes': video_data.get('Likes', 0),
            'Date Saved': created_at
        })
    
    # Display report list
    df = pd.DataFrame(report_data)
    st.dataframe(df)
    
    if len(df) > 0:
        # Allow selecting a report to view in detail
        selected_report_id = st.selectbox("Select a report to view", options=df['ID'].tolist(), format_func=lambda x: f"{df[df['ID']==x]['Title'].iloc[0]} (ID: {x})")
        
        if st.button("View Report"):
            with st.spinner("Loading report..."):
                # Try to get report directly from Firestore first
                report = direct_get_report(selected_report_id)
                
                # If direct retrieval fails, try local file
                if not report:
                    try:
                        import os
                        import json
                        local_path = f"saved_reports/{selected_report_id}.json"
                        if os.path.exists(local_path):
                            with open(local_path, 'r') as f:
                                report = json.load(f)
                            print(f"Loaded report from local file: {local_path}")
                    except Exception as file_error:
                        print(f"Error loading report from local file: {str(file_error)}")
                
            if report:
                # Display report details
                st.subheader(f"📊 Report for: {report.get('title', 'Unknown')}")
                
                # Try to parse video data
                try:
                    video_data = json.loads(report.get('query', '{}'))
                except:
                    video_data = {}
                
                # Display metrics in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Views", video_data.get('Views', 0))
                with col2:
                    st.metric("Likes", video_data.get('Likes', 0))
                with col3:
                    st.metric("Comments", video_data.get('Comments', 0))
                with col4:
                    st.metric("Saves", video_data.get('Saves', 0))
                
                # Display the report
                st.subheader("📝 Analysis")
                report_text = report.get('metrics', 'No analysis found')
                formatted_report = utils.format_report_for_display(report_text)
                st.markdown(formatted_report)
                
                # Delete button
                if st.button("Delete Report"):
                    with st.spinner("Deleting report..."):
                        # Try to delete directly from Firestore first
                        success = direct_delete_report(selected_report_id)
                        
                        # If direct delete fails, try local file
                        if not success:
                            try:
                                import os
                                local_path = f"saved_reports/{selected_report_id}.json"
                                if os.path.exists(local_path):
                                    os.remove(local_path)
                                    success = True
                                    print(f"Deleted local report file: {local_path}")
                            except Exception as file_error:
                                print(f"Error deleting local report file: {str(file_error)}")
                        
                        if success:
                            st.success(f"Report deleted successfully!")
                            # Remove from session state
                            st.session_state.saved_reports = [(rid, title) for rid, title in st.session_state.saved_reports if rid != selected_report_id]
                            st.rerun()
                        else:
                            st.error("Failed to delete report")
            else:
                st.error(f"Could not load report with ID: {selected_report_id}")
                # Check if report exists in Firestore collection (debugging)
                try:
                    # Write debug info to log
                    with open("save_attempts.log", "a") as log:
                        log.write(f"{datetime.now().isoformat()} - Debug: Checking if report exists: {selected_report_id}\n")
                    
                    # Try to get all reports to check
                    all_reports = direct_get_all_reports()
                    report_ids = [r.get('id') for r in all_reports]
                    with open("save_attempts.log", "a") as log:
                        log.write(f"{datetime.now().isoformat()} - Debug: All report IDs: {report_ids}\n")
                    
                    if selected_report_id in report_ids:
                        st.warning(f"Report ID {selected_report_id} exists in the database but could not be retrieved. This may be a permission issue.")
                    else:
                        st.warning(f"Report ID {selected_report_id} does not exist in the database.")
                except Exception as debug_error:
                    logger.error(f"Error during report debugging: {str(debug_error)}", exc_info=True)

    # Add a button to create a test report if no reports are found
    if not reports:
        st.markdown("---")
        st.subheader("Create Test Report")
        st.write("No reports found. You can create a test report to verify the functionality.")
        
        if st.button("Create Test Report"):
            try:
                # Create test report data
                import uuid
                import json
                import datetime
                import os
                
                # Ensure the directory exists
                saved_reports_dir = "saved_reports"
                if not os.path.exists(saved_reports_dir):
                    os.makedirs(saved_reports_dir, exist_ok=True)
                
                # Create a unique ID
                report_id = str(uuid.uuid4())
                
                # Format timestamp
                timestamp = datetime.datetime.now().isoformat()
                
                # Create test data
                test_report = {
                    'id': report_id,
                    'title': f"Test Report {timestamp}",
                    'description': "This is a test report created directly from the app",
                    'image_path': "",
                    'query': json.dumps({
                        'Title': 'Test TikTok Video',
                        'Views': 1000,
                        'Likes': 100,
                        'Comments': 50,
                        'Saves': 25
                    }),
                    'metrics': "This is a test analysis of this TikTok video:\n\n1. Engagement rate is good\n2. Comments are mostly positive\n3. Recommend creating similar content",
                    'created_at': time.time()
                }
                
                # Try to save to Firebase using FirebaseAPI
                try:
                    from firebase_api import FirebaseAPI
                    firebase_api = FirebaseAPI()
                    if firebase_api.is_connected():
                        saved_id = firebase_api.save_report(
                            test_report['title'],
                            test_report['description'],
                            test_report['image_path'],
                            test_report['query'],
                            test_report['metrics']
                        )
                        if saved_id:
                            st.success(f"Test report saved to Firebase with ID: {saved_id}")
                            st.info("Please refresh the page or click 'Refresh Reports' to see the test report.")
                            return
                except Exception as firebase_error:
                    st.error(f"Error saving to Firebase: {str(firebase_error)}")
                
                # If Firebase fails, save to local file
                try:
                    # Save to file in saved_reports directory
                    report_path = os.path.join(saved_reports_dir, f"{report_id}.json")
                    with open(report_path, 'w') as f:
                        json.dump(test_report, f, indent=2)
                    
                    st.success(f"Test report saved to local file: {report_path}")
                    st.info("Please refresh the page or click 'Refresh Reports' to see the test report.")
                except Exception as file_error:
                    st.error(f"Error saving to local file: {str(file_error)}")
                    
            except Exception as e:
                st.error(f"Error creating test report: {str(e)}")
                import traceback
                st.error(traceback.format_exc())

def save_report_to_local_file(video_data, report):
    """Save a report directly to a local file as fallback"""
    try:
        from datetime import datetime
        import json
        import os
        
        logger.info("Attempting to save report to local file")
        
        # Create a reports directory if it doesn't exist
        reports_dir = "saved_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            logger.info(f"Created directory: {reports_dir}")
        
        # Generate a unique filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_id = f"{timestamp}_{hash(video_data.get('Title', ''))}"
        
        # Create the report data
        report_data = {
            'id': report_id,
            'title': video_data.get('Title', 'Untitled'),
            'description': video_data.get('Caption', ''),
            'query': json.dumps(video_data),
            'metrics': report,
            'created_at': datetime.now().timestamp()
        }
        
        # Save to file
        filename = f"{reports_dir}/{report_id}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"Report saved successfully to local file: {filename}")
        print(f"Report saved successfully to local file: {filename}")
        
        # Also log to a specific save log file
        with open("save_log.txt", "a") as log:
            log.write(f"{datetime.now().isoformat()} - Saved report {report_id} to {filename}\n")
        
        return report_id
    except Exception as e:
        logger.error(f"Error saving report to local file: {str(e)}", exc_info=True)
        print(f"Error saving report to local file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main application function"""
    # Check if user is authenticated
    if not st.session_state.authenticated:
        render_login()
        return
    
    # Try to load saved reports if not already loaded
    if not st.session_state.saved_reports:
        try:
            logger.info("Loading saved reports into session state...")
            # Use direct function to get all reports
            all_reports = direct_get_all_reports()
            if all_reports:
                # Clear existing reports if any
                st.session_state.saved_reports = []
                # Add reports to session state
                for report in all_reports:
                    report_id = report.get('id')
                    title = report.get('title', 'Unknown')
                    if report_id:
                        st.session_state.saved_reports.append((report_id, title))
                logger.info(f"Loaded {len(st.session_state.saved_reports)} reports into session state")
        except Exception as e:
            logger.error(f"Error loading saved reports: {str(e)}", exc_info=True)
    
    # Main header
    st.title("🧠 TikTok Content Performance Analyst")
    st.markdown("""
    This tool analyzes TikTok video performance metrics and generates detailed actionable reports to help optimize for virality.
    """)
    
    # Check if both APIs are connected
    if not (sheets_connected and openai_connected):
        st.error("Cannot proceed without API connections. Please check sidebar for details.")
        return
    
    # Create tabs for different analysis methods
    tab1, tab2, tab3 = st.tabs(["Google Sheets Analysis", "Single Video Analysis", "Saved Reports"])
    
    # Set the active tab based on session state
    active_tab_index = 0
    if st.session_state.active_tab == "Single Video Analysis":
        active_tab_index = 1
    elif st.session_state.active_tab == "Saved Reports":
        active_tab_index = 2
    
    with tab1:
        if active_tab_index == 0:
            render_sheets_analysis_form()
        
    with tab2:
        if active_tab_index == 1:
            render_manual_input_form()
        
    with tab3:
        if active_tab_index == 2:
            render_saved_reports()

if __name__ == "__main__":
    # Initialize APIs
    sheets_connected, openai_connected, auth_initialized, firestore_connected, sheets_api, openai_api, firebase_auth, firestore_db, analyzer = initialize_apis()
    
    # Render sidebar
    render_sidebar()
    
    # Render main app
    main() 