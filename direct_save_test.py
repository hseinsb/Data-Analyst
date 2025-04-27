import os
import json
import time
from datetime import datetime

# Create directory if it doesn't exist
reports_dir = "saved_reports"
if not os.path.exists(reports_dir):
    os.makedirs(reports_dir)
    print(f"Created directory: {reports_dir}")

# Create a test report
report_id = f"test_report_{int(time.time())}"
report_data = {
    'id': report_id,
    'title': "Test Report",
    'description': "This is a test report",
    'query': json.dumps({"Title": "Test Video", "Views": 1000, "Likes": 100}),
    'metrics': "This is test metrics content",
    'created_at': time.time()
}

# Save to file
filename = f"{reports_dir}/{report_id}.json"
with open(filename, 'w') as f:
    json.dump(report_data, f, indent=2)

print(f"Report saved successfully to: {filename}")

# Verify the file exists
if os.path.exists(filename):
    print(f"File verified to exist: {filename}")
    print(f"File size: {os.path.getsize(filename)} bytes")
    
    # Read the file contents
    with open(filename, 'r') as f:
        content = json.load(f)
    print(f"File content read successfully: {json.dumps(content)[:100]}...")
else:
    print(f"ERROR: File does not exist: {filename}")

# List all reports in the directory
print(f"\nAll reports in {reports_dir}:")
if os.path.exists(reports_dir):
    for file in os.listdir(reports_dir):
        if file.endswith(".json"):
            print(f"- {file}")
else:
    print(f"Directory does not exist: {reports_dir}") 