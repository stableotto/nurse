import csv
from datetime import datetime
from jobspy import scrape_jobs
import os
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
RANGE_NAME = 'Sheet1!A:Z'  # Changed to Sheet1 as it's the default first sheet name

def serialize_dates(obj):
    """Convert datetime objects to string format."""
    if pd.isna(obj):
        return ""
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime('%Y-%m-%d')
    return str(obj)

def get_google_sheets_service():
    """Initialize Google Sheets service."""
    try:
        # Load credentials from service account JSON stored in GitHub secrets
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        if not creds_json:
            logger.error("No Google Sheets credentials found in environment variables")
            return None
            
        try:
            creds_dict = json.loads(creds_json)
            logger.info("Successfully parsed credentials JSON")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse credentials JSON: {str(e)}")
            return None
            
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully created Google Sheets service")
        return service
    except Exception as e:
        logger.error(f"Error setting up Google Sheets service: {str(e)}")
        return None

def get_existing_jobs():
    """Get existing jobs from Google Sheets to avoid duplicates."""
    service = get_google_sheets_service()
    if not service:
        return set()
    
    try:
        if not SPREADSHEET_ID:
            logger.error("No spreadsheet ID found in environment variables")
            return set()
            
        logger.info(f"Attempting to read from spreadsheet ID: {SPREADSHEET_ID}")
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        rows = result.get('values', [])
        logger.info(f"Found {len(rows)} existing rows in Google Sheet")
        
        if not rows:
            return set()
        
        existing_jobs = set()
        for row in rows[1:]:  # Skip header row
            if len(row) >= 3:
                job_id = f"{row[0]}|{row[1]}|{row[2]}"
                existing_jobs.add(job_id)
        
        return existing_jobs
    except HttpError as e:
        logger.error(f"Google Sheets API error: {str(e)}")
        return set()
    except Exception as e:
        logger.error(f"Error getting existing jobs: {str(e)}")
        return set()

def update_google_sheet(new_jobs_df):
    """Update Google Sheet with new jobs."""
    service = get_google_sheets_service()
    if not service:
        return
    
    try:
        if new_jobs_df.empty:
            logger.info("No new jobs to add to Google Sheet")
            return

        # Convert all values to strings and handle dates
        processed_df = new_jobs_df.applymap(serialize_dates)
            
        # Prepare the data
        values = [processed_df.columns.tolist()]  # Header row
        values.extend(processed_df.values.tolist())
        
        body = {
            'values': values
        }
        
        logger.info(f"Attempting to append {len(values)-1} new jobs to Google Sheet")
        
        # Check if the sheet exists and create it if it doesn't
        try:
            service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
        except HttpError as e:
            if e.resp.status == 404:
                # Sheet doesn't exist, create it
                body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': 'Sheet1'
                            }
                        }
                    }]
                }
                service.spreadsheets().batchUpdate(
                    spreadsheetId=SPREADSHEET_ID,
                    body=body
                ).execute()
                logger.info("Created new sheet 'Sheet1'")
        
        # Append the new data
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        logger.info(f"Successfully added {result.get('updates', {}).get('updatedRows', 0)} new jobs to Google Sheet")
    except Exception as e:
        logger.error(f"Error updating Google Sheet: {str(e)}")

def search_pharmacist_jobs():
    """Search for new pharmacist jobs and update Google Sheet."""
    timestamp = datetime.now().strftime("%Y%m%d")
    
    try:
        # Get existing jobs to avoid duplicates
        existing_jobs = get_existing_jobs()
        logger.info(f"Found {len(existing_jobs)} existing jobs in Google Sheet")
        
        # Search for remote pharmacist jobs
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
            search_term="pharmacist",
            is_remote=True,
            results_wanted=100,
            hours_old=24,
            country_indeed='USA'
        )
        
        # Convert to DataFrame
        jobs_df = pd.DataFrame(jobs)
        logger.info(f"Scraped {len(jobs_df)} total jobs")
        
        # Create unique identifiers for new jobs
        jobs_df['job_id'] = jobs_df.apply(
            lambda x: f"{x['title']}|{x['company']}|{x['location']}", axis=1
        )
        
        # Filter out existing jobs
        new_jobs_df = jobs_df[~jobs_df['job_id'].isin(existing_jobs)]
        new_jobs_df = new_jobs_df.drop('job_id', axis=1)
        
        logger.info(f"Found {len(new_jobs_df)} new jobs after filtering duplicates")
        
        if len(new_jobs_df) > 0:
            # Update Google Sheet with new jobs
            update_google_sheet(new_jobs_df)
        else:
            logger.info("No new jobs to add to Google Sheet")
        
        # Save local backup
        if not os.path.exists('job_results'):
            os.makedirs('job_results')
        
        filename = f"job_results/pharmacist_jobs_{timestamp}.csv"
        new_jobs_df.to_csv(filename, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
        logger.info(f"Results saved to {filename}")
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    search_pharmacist_jobs() 