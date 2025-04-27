import pandas as pd
from sheets_api import SheetsAPI
from openai_api import OpenAIAPI

class TikTokAnalyzer:
    def __init__(self, sheets_api, openai_api):
        """
        Initialize the TikTok video analyzer
        
        Args:
            sheets_api (SheetsAPI): Google Sheets API instance
            openai_api (OpenAIAPI): OpenAI API instance
        """
        self.sheets_api = sheets_api
        self.openai_api = openai_api
        
    def analyze_videos(self, sheet_url, worksheet_name="Account A Data", analysis_col_index=None, selected_indices=None):
        """
        Analyze videos in a Google Sheet
        
        Args:
            sheet_url (str): URL of the Google Sheet
            worksheet_name (str): Name of the worksheet to analyze
            analysis_col_index (int, optional): Index of the column to store analysis reports
            selected_indices (list, optional): List of row indices to analyze (0-based, excluding header)
            
        Returns:
            tuple: (success (bool), message (str), reports (list))
        """
        try:
            # Open the Google Sheet
            sheet = self.sheets_api.open_sheet_by_url(sheet_url)
            if not sheet:
                return False, "Failed to open Google Sheet", []
                
            # Get the worksheet by name
            worksheet = self.sheets_api.get_worksheet_by_name(sheet, worksheet_name)
            if not worksheet:
                return False, "Failed to open worksheet", []
                
            # Get the video data as a DataFrame
            df = self.sheets_api.get_data_as_dataframe(worksheet)
            if df.empty:
                return False, "No data found in worksheet", []
                
            # Check if required columns exist (using your sheet's column names)
            required_columns = ['Title/Hook', 'Caption', 'Views (24h)', 'Likes', 'Comments', 'Saves']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", []
                
            # Process data (convert data types, handle null values, etc.)
            processed_df = self._preprocess_data(df)
            
            # Calculate ratios if they don't exist
            processed_df = self._calculate_missing_ratios(processed_df)
                
            # Generate analysis reports for selected videos or all videos
            reports = []
            
            # Filter rows if specific indices are provided
            if selected_indices is not None and len(selected_indices) > 0:
                # Ensure indices are within range
                valid_indices = [i for i in selected_indices if 0 <= i < len(processed_df)]
                if not valid_indices:
                    return False, "No valid row indices provided", []
                
                rows_to_analyze = processed_df.iloc[valid_indices]
            else:
                rows_to_analyze = processed_df
                
            for _, row in rows_to_analyze.iterrows():
                # Prepare data for analysis
                video_data = self._prepare_video_data(row)
                
                # Generate analysis for this video
                report = self.openai_api.generate_analysis(video_data)
                reports.append(report)
                
            # Update the analysis column in the worksheet if specified
            if analysis_col_index is not None:
                if selected_indices is not None:
                    # Only update specific rows
                    for i, idx in enumerate(selected_indices):
                        if i < len(reports):
                            # +2 because: +1 for 1-indexed spreadsheet, +1 for header row
                            self.sheets_api.update_cell(
                                worksheet, 
                                idx + 2, 
                                analysis_col_index + 1,  # +1 because spreadsheet columns are 1-indexed
                                reports[i]
                            )
                else:
                    # Update all rows
                    success = self.sheets_api.update_analysis_column(
                        worksheet, reports, analysis_col_index
                    )
                    if not success:
                        return True, "Analysis complete but failed to update sheet", reports
                    
            return True, f"Successfully analyzed {len(reports)} videos", reports
        except Exception as e:
            return False, f"Error analyzing videos: {str(e)}", []
    
    def _preprocess_data(self, df):
        """Preprocess the data from the sheet"""
        # Make a copy to avoid modifying the original
        processed_df = df.copy()
        
        # Ensure metric columns are numeric
        numeric_columns = ['Views (24h)', 'Likes', 'Comments', 'Saves']
        
        for col in numeric_columns:
            if col in processed_df.columns:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
                
        # Fill NaN values with 0 for numeric columns
        for col in numeric_columns:
            if col in processed_df.columns:
                processed_df[col] = processed_df[col].fillna(0)
        
        # Fill NaN values with empty strings for text columns
        for col in ['Title/Hook', 'Caption', 'Hashtags', 'Notes (Topic/Emotion)']:
            if col in processed_df.columns:
                processed_df[col] = processed_df[col].fillna('')
                
        return processed_df
    
    def _prepare_video_data(self, row):
        """
        Prepare data for analysis by mapping sheet columns to expected format
        
        Args:
            row (pandas.Series): Row from the processed DataFrame
            
        Returns:
            dict: Formatted video data for analysis
        """
        # Extract title and hook from combined field
        title_hook = row.get('Title/Hook', '')
        
        # Prepare the basic video data
        video_data = {
            "Title": title_hook,  # Use combined field
            "Hook": title_hook,   # Use same field for hook
            "Caption": row.get('Caption', ''),
            "Hashtags": row.get('Hashtags', ''),
            "Views": row.get('Views (24h)', 0),
            "Likes": row.get('Likes', 0),
            "Comments": row.get('Comments', 0),
            "Saves": row.get('Saves', 0),
            "Notes": row.get('Notes (Topic/Emotion)', '')
        }
        
        # Add ratio data using the actual sheet column names
        ratio_columns = [
            'Views to Like Ratio (%)', 
            'Views to Comment Ratio (%)', 
            'Views to Save Ratio (%)',
            'Like to Comment Ratio (%)',
            'Like to Save Ratio (%)'
        ]
        
        for col in ratio_columns:
            if col in row:
                video_data[col] = row[col]
        
        return video_data
            
    def analyze_single_video(self, video_data):
        """
        Analyze a single video based on the provided data
        
        Args:
            video_data (dict): Dictionary containing video metrics and details
            
        Returns:
            str: The generated analysis report
        """
        try:
            # Convert to DataFrame to calculate missing ratios if needed
            df = pd.DataFrame([video_data])
            
            # Ensure all ratios are calculated
            df = self._calculate_missing_ratios(df)
            
            # Convert back to dictionary
            updated_video_data = df.iloc[0].to_dict()
            
            # Generate analysis
            report = self.openai_api.generate_analysis(updated_video_data)
            
            return report
        except Exception as e:
            print(f"Error analyzing video: {str(e)}")
            return "Error analyzing video. Please try again."
            
    def _calculate_missing_ratios(self, df):
        """Calculate missing ratio columns in the DataFrame"""
        try:
            # Map column names between the sheet and our expected format
            view_col = 'Views (24h)' if 'Views (24h)' in df.columns else 'Views'
            
            # Ensure we have the necessary columns to calculate ratios
            if view_col not in df.columns or 'Likes' not in df.columns or 'Comments' not in df.columns or 'Saves' not in df.columns:
                return df
            
            # Make sure all metrics are numeric
            for col in [view_col, 'Likes', 'Comments', 'Saves']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Calculate all ratios (using the sheet's column names)
            df['Views to Like Ratio (%)'] = (df['Likes'] / df[view_col] * 100).round(2)
            df['Views to Comment Ratio (%)'] = (df['Comments'] / df[view_col] * 100).round(2)
            df['Views to Save Ratio (%)'] = (df['Saves'] / df[view_col] * 100).round(2)
            df['Like to Comment Ratio (%)'] = (df['Comments'] / df['Likes'] * 100).round(2).replace([float('inf'), float('nan')], 0)
            df['Like to Save Ratio (%)'] = (df['Saves'] / df['Likes'] * 100).round(2).replace([float('inf'), float('nan')], 0)
            
            return df
        except Exception as e:
            print(f"Error calculating ratios: {str(e)}")
            return df 