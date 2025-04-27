import os
import re
import pandas as pd
from datetime import datetime

def validate_google_sheet_url(url):
    """
    Validate that a URL is a valid Google Sheet URL
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Check if URL is a Google Sheets URL
    pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit|/view)'
    return bool(re.match(pattern, url))
    
def validate_column_names(df, required_columns):
    """
    Validate that a DataFrame contains all required columns
    
    Args:
        df (pandas.DataFrame): DataFrame to validate
        required_columns (list): List of required column names
        
    Returns:
        tuple: (is_valid (bool), missing_columns (list))
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    is_valid = len(missing_columns) == 0
    return is_valid, missing_columns
    
def format_report_for_display(report):
    """
    Format an analysis report for display in Streamlit
    
    Args:
        report (str): Raw report text
        
    Returns:
        str: Formatted report with HTML/Markdown styling
    """
    # Replace section headers with styled headers
    sections = {
        "Overview Summary": "## Overview Summary",
        "Detailed Metric Breakdown": "## Detailed Metric Breakdown",
        "Strengths Identified": "## Strengths Identified",
        "Weaknesses Identified": "## Weaknesses Identified",
        "Actionable Improvements": "## Actionable Improvements",
        "Viral Potential Score": "## Viral Potential Score"
    }
    
    formatted_report = report
    for section, markdown in sections.items():
        # Match the section name at the beginning of a line or after newlines
        pattern = fr'(?:\n|^)({section}|{section}:)'
        formatted_report = re.sub(pattern, f'\n{markdown}', formatted_report)
    
    # Format metric names in bold
    metrics = ["Like-to-View", "Comment-to-View", "Comment-to-Like", "Save-to-View", "Save-to-Like"]
    for metric in metrics:
        formatted_report = formatted_report.replace(f"{metric}:", f"**{metric}:**")
    
    return formatted_report
    
def export_to_csv(reports, video_data, output_path=None):
    """
    Export analysis reports to a CSV file
    
    Args:
        reports (list): List of analysis reports
        video_data (pandas.DataFrame): DataFrame of video data
        output_path (str, optional): Path to save the CSV file
        
    Returns:
        str: Path to the saved CSV file
    """
    # Create a DataFrame with video data and reports
    export_df = video_data.copy()
    export_df['Analysis Report'] = reports
    
    # Generate a default filename if none provided
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"tiktok_analysis_{timestamp}.csv"
    
    # Save to CSV
    export_df.to_csv(output_path, index=False)
    
    return output_path 