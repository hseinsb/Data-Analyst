import streamlit as st
import json
import os
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Simple Report Saver",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'saved_reports' not in st.session_state:
    st.session_state.saved_reports = []

# Function to save a report to a local file
def save_report_to_file(title, description, content):
    """Save a report to a local file"""
    try:
        # Create the reports directory if it doesn't exist
        reports_dir = "simple_reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            st.success(f"Created directory: {reports_dir}")
        
        # Generate a unique ID
        report_id = f"report_{int(time.time())}"
        
        # Create the report data
        report_data = {
            'id': report_id,
            'title': title,
            'description': description,
            'content': content,
            'created_at': time.time()
        }
        
        # Save to file
        filename = os.path.join(reports_dir, f"{report_id}.json")
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Add to session state
        st.session_state.saved_reports.append((report_id, title))
        
        return report_id, filename
    except Exception as e:
        st.error(f"Error saving report: {str(e)}")
        return None, None

# Function to list all saved reports
def get_all_reports():
    """Get all saved reports"""
    reports = []
    reports_dir = "simple_reports"
    
    if not os.path.exists(reports_dir):
        return []
    
    for filename in os.listdir(reports_dir):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(reports_dir, filename), 'r') as f:
                    report_data = json.load(f)
                    reports.append(report_data)
            except Exception as e:
                st.error(f"Error loading report {filename}: {str(e)}")
    
    return reports

# Main app
st.title("📝 Simple Report Saver")

# Input form
with st.form("report_form"):
    title = st.text_input("Report Title")
    description = st.text_area("Report Description")
    content = st.text_area("Report Content")
    
    submitted = st.form_submit_button("Save Report")
    
    if submitted:
        if not title or not content:
            st.error("Please provide a title and content.")
        else:
            with st.spinner("Saving report..."):
                report_id, filename = save_report_to_file(title, description, content)
                
                if report_id:
                    st.success(f"Report saved successfully! ID: {report_id}")
                    st.info(f"Saved to file: {filename}")
                else:
                    st.error("Failed to save report.")

# Display saved reports
st.subheader("Saved Reports")

# Manual refresh button
if st.button("Refresh Reports"):
    with st.spinner("Loading reports..."):
        reports = get_all_reports()
        
        # Update session state
        st.session_state.saved_reports = [(report['id'], report['title']) for report in reports]
        
        if reports:
            st.success(f"Loaded {len(reports)} reports")
        else:
            st.info("No reports found")
    
# Get and display reports
reports = get_all_reports()

if not reports:
    st.info("No reports found. Create one using the form above.")
else:
    # Create a list of report titles
    report_ids = [report['id'] for report in reports]
    report_titles = [report['title'] for report in reports]
    
    # Format for display
    report_options = {report_id: f"{title}" for report_id, title in zip(report_ids, report_titles)}
    
    # Show reports in a selectbox
    selected_id = st.selectbox("Select a report to view", options=report_ids, format_func=lambda x: report_options[x])
    
    # Find the selected report
    selected_report = next((r for r in reports if r['id'] == selected_id), None)
    
    if selected_report:
        # Display report details
        st.subheader(f"Report: {selected_report['title']}")
        st.markdown(f"**Description:** {selected_report['description']}")
        
        # Format creation date
        if 'created_at' in selected_report:
            created_at = datetime.fromtimestamp(selected_report['created_at']).strftime('%Y-%m-%d %H:%M:%S')
            st.markdown(f"**Created:** {created_at}")
        
        # Display content
        st.subheader("Content:")
        st.markdown(selected_report['content'])
        
        # Delete button
        if st.button("Delete Report"):
            try:
                # Delete the file
                filename = os.path.join("simple_reports", f"{selected_id}.json")
                if os.path.exists(filename):
                    os.remove(filename)
                    
                    # Update session state
                    st.session_state.saved_reports = [(rid, title) for rid, title in st.session_state.saved_reports if rid != selected_id]
                    
                    st.success("Report deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"File not found: {filename}")
            except Exception as e:
                st.error(f"Error deleting report: {str(e)}")

# Display debug info
st.subheader("Debug Information")
st.write(f"Reports directory exists: {os.path.exists('simple_reports')}")
st.write(f"Number of reports in session state: {len(st.session_state.saved_reports)}")

# Show the files in the reports directory
if os.path.exists("simple_reports"):
    files = os.listdir("simple_reports")
    st.write(f"Files in reports directory: {files}")
else:
    st.write("Reports directory does not exist") 