import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

class SheetsAPI:
    def __init__(self, credentials_path="credentials.json"):
        """Initialize the Google Sheets API connection"""
        try:
            self.credentials = Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )
            self.client = gspread.authorize(self.credentials)
            self.connected = True
        except Exception as e:
            print(f"Error connecting to Google Sheets API: {str(e)}")
            self.connected = False
            
    def is_connected(self):
        """Check if API connection is established"""
        return self.connected
            
    def open_sheet_by_url(self, sheet_url):
        """Open a Google Sheet by its URL"""
        try:
            sheet = self.client.open_by_url(sheet_url)
            return sheet
        except Exception as e:
            print(f"Error opening sheet: {str(e)}")
            return None
            
    def get_worksheet(self, sheet, worksheet_index=0):
        """Get a specific worksheet from a Google Sheet by index"""
        try:
            return sheet.get_worksheet(worksheet_index)
        except Exception as e:
            print(f"Error getting worksheet: {str(e)}")
            return None
            
    def get_worksheet_by_name(self, sheet, worksheet_name):
        """Get a specific worksheet from a Google Sheet by name"""
        try:
            # Get all worksheets
            worksheets = sheet.worksheets()
            
            # Find worksheet by name
            for worksheet in worksheets:
                if worksheet.title == worksheet_name:
                    return worksheet
                    
            # If not found, return None
            print(f"Worksheet '{worksheet_name}' not found. Available worksheets: {[ws.title for ws in worksheets]}")
            return None
        except Exception as e:
            print(f"Error getting worksheet by name: {str(e)}")
            return None
            
    def get_all_records(self, worksheet):
        """Get all records from a worksheet as a list of dictionaries"""
        try:
            return worksheet.get_all_records()
        except Exception as e:
            print(f"Error getting records: {str(e)}")
            return []
            
    def get_data_as_dataframe(self, worksheet):
        """Get worksheet data as a pandas DataFrame"""
        try:
            records = worksheet.get_all_records()
            return pd.DataFrame(records)
        except Exception as e:
            print(f"Error converting to DataFrame: {str(e)}")
            return pd.DataFrame()
            
    def update_cell(self, worksheet, row, col, value):
        """Update a specific cell in the worksheet"""
        try:
            worksheet.update_cell(row, col, value)
            return True
        except Exception as e:
            print(f"Error updating cell: {str(e)}")
            return False
            
    def append_row(self, worksheet, row_data):
        """Append a row to the worksheet"""
        try:
            worksheet.append_row(row_data)
            return True
        except Exception as e:
            print(f"Error appending row: {str(e)}")
            return False
            
    def update_analysis_column(self, worksheet, analysis_data, analysis_col_index):
        """Update the analysis column with generated reports"""
        try:
            # Get the current values in the worksheet
            all_values = worksheet.get_all_values()
            header_row = all_values[0]
            
            # Ensure the analysis column exists
            if len(header_row) <= analysis_col_index:
                # Add a new column if needed
                for i, row in enumerate(all_values):
                    if i == 0:
                        worksheet.update_cell(1, analysis_col_index + 1, "Analysis Report")
                    row.append("")
                    
            # Update the analysis column with the new reports
            for i, analysis in enumerate(analysis_data):
                # Skip the header row
                row_index = i + 2  # +2 because spreadsheet is 1-indexed and we skip header
                worksheet.update_cell(row_index, analysis_col_index + 1, analysis)
                
            return True
        except Exception as e:
            print(f"Error updating analysis column: {str(e)}")
            return False 