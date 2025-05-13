import csv
from datetime import datetime
from jobspy import scrape_jobs
import os
import pandas as pd
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Sheets constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
RANGE_NAME = 'Jobs!A:Z'  # Adjust based on your sheet's structure

def get_google_sheets_service():
    """Initialize Google Sheets service."""
    try:
        # Load credentials from service account JSON stored in GitHub secrets
        creds_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
        creds = service_account.Credentials.from_service_account_info(
            eval(creds_json), scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"Error setting up Google Sheets service: {str(e)}")
        return None

def get_existing_jobs():
    """Get existing jobs from Google Sheets to avoid duplicates."""
    service = get_google_sheets_service()
    if not service:
        return set()
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        
        rows = result.get('values', [])
        if not rows:
            return set()
        
        # Create a set of unique identifiers (job title + company + location)
        existing_jobs = set()
        for row in rows[1:]:  # Skip header row
            if len(row) >= 3:
                job_id = f"{row[0]}|{row[1]}|{row[2]}"
                existing_jobs.add(job_id)
        
        return existing_jobs
    except Exception as e:
        print(f"Error getting existing jobs: {str(e)}")
        return set()

def update_google_sheet(new_jobs_df):
    """Update Google Sheet with new jobs."""
    service = get_google_sheets_service()
    if not service:
        return
    
    try:
        # Prepare the data
        values = [new_jobs_df.columns.tolist()]  # Header row
        values.extend(new_jobs_df.values.tolist())
        
        body = {
            'values': values
        }
        
        # Append the new data
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        print(f"Added {result.get('updates').get('updatedRows')} new jobs to Google Sheet")
    except Exception as e:
        print(f"Error updating Google Sheet: {str(e)}")

def search_pharmacist_jobs():
    """Search for new pharmacist jobs and update Google Sheet."""
    timestamp = datetime.now().strftime("%Y%m%d")
    
    try:
        # Get existing jobs to avoid duplicates
        existing_jobs = get_existing_jobs()
        
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
        
        # Create unique identifiers for new jobs
        jobs_df['job_id'] = jobs_df.apply(
            lambda x: f"{x['title']}|{x['company']}|{x['location']}", axis=1
        )
        
        # Filter out existing jobs
        new_jobs_df = jobs_df[~jobs_df['job_id'].isin(existing_jobs)]
        new_jobs_df = new_jobs_df.drop('job_id', axis=1)
        
        if len(new_jobs_df) > 0:
            # Update Google Sheet with new jobs
            update_google_sheet(new_jobs_df)
            print(f"Found {len(new_jobs_df)} new jobs")
        else:
            print("No new jobs found")
        
        # Save local backup
        if not os.path.exists('job_results'):
            os.makedirs('job_results')
        
        filename = f"job_results/pharmacist_jobs_{timestamp}.csv"
        new_jobs_df.to_csv(filename, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
        print(f"Results saved to {filename}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    search_pharmacist_jobs() 