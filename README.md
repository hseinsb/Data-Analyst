# TikTok Content Performance Analyst

An AI-powered tool that analyzes TikTok video performance metrics from Google Sheets and generates detailed actionable reports to optimize for virality.

## Features

- Connects to Google Sheets to retrieve TikTok video metrics
- Analyzes performance data (views, likes, comments, saves, and calculated ratios)
- Generates detailed reports with specific insights on each metric
- Provides actionable recommendations to improve future content
- Focuses on optimizing for TikTok virality

## Setup Instructions

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up a Google Cloud Project and enable the Google Sheets API:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project 
   - Enable the Google Sheets API
   - Create a service account and download the JSON credentials file
   - Rename the credentials file to `credentials.json` and place it in the project root

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

5. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Enter the URL of your Google Sheet containing TikTok video data
2. The sheet should have columns for: Title, Hook, Caption, Views, Likes, Comments, Saves, and calculated ratios
3. Click "Analyze Videos" to generate detailed performance reports
4. View reports directly in the app or have them written back to your Google Sheet

## File Structure

- `app.py`: Main Streamlit application
- `sheets_api.py`: Google Sheets API integration
- `openai_api.py`: OpenAI API integration
- `analyzer.py`: Core analysis logic
- `utils.py`: Utility functions 