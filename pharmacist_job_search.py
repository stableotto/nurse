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

def search_pharmacist_jobs_with_date_filter(date_filter_option="today", hours_old=12):
    """
    Search for new pharmacist jobs with flexible date filtering options.
    
    Args:
        date_filter_option (str): Options are:
            - "today": Only jobs posted today
            - "yesterday": Only jobs posted yesterday  
            - "last_24h": Jobs posted in last 24 hours (default JobSpy behavior)
            - "last_12h": Jobs posted in last 12 hours
            - "custom_hours": Use the hours_old parameter as-is
        hours_old (int): Number of hours to look back (used when date_filter_option is "custom_hours")
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    today = datetime.now().date()
    yesterday = today - pd.Timedelta(days=1)
    
    # Determine hours_old based on filter option
    if date_filter_option == "today":
        scrape_hours_old = 12  # Get last 12 hours, then filter for today
        filter_date = today
        filter_description = "today"
    elif date_filter_option == "yesterday":
        scrape_hours_old = 36  # Get last 36 hours, then filter for yesterday
        filter_date = yesterday  
        filter_description = "yesterday"
    elif date_filter_option == "last_24h":
        scrape_hours_old = 24
        filter_date = None  # No additional filtering
        filter_description = "last 24 hours"
    elif date_filter_option == "last_12h":
        scrape_hours_old = 12
        filter_date = None  # No additional filtering
        filter_description = "last 12 hours" 
    elif date_filter_option == "custom_hours":
        scrape_hours_old = hours_old
        filter_date = None  # No additional filtering
        filter_description = f"last {hours_old} hours"
    else:
        raise ValueError(f"Invalid date_filter_option: {date_filter_option}")
    
    try:
        # Get existing jobs to avoid duplicates
        existing_jobs = get_existing_jobs()
        logger.info(f"Found {len(existing_jobs)} existing jobs in Google Sheet")
        
        # Search for remote pharmacist jobs
        logger.info(f"Searching for jobs from {filter_description}...")
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
            search_term="pharmacist",
            is_remote=True,
            results_wanted=100,
            hours_old=scrape_hours_old,
            country_indeed='USA'
        )
        
        # Convert to DataFrame
        jobs_df = pd.DataFrame(jobs)
        logger.info(f"Scraped {len(jobs_df)} total jobs")
        
        # STRICT FILTERING: Only include jobs where is_remote = True, completely exclude is_remote = False
        if not jobs_df.empty and 'is_remote' in jobs_df.columns:
            # Count non-remote jobs before filtering
            non_remote_count = len(jobs_df[jobs_df['is_remote'] == False])
            
            # Apply strict remote-only filter
            jobs_df = jobs_df[jobs_df['is_remote'] == True]
            
            logger.info(f"REMOTE FILTERING: Found {len(jobs_df)} remote jobs, excluded {non_remote_count} non-remote jobs")
            
            # Double-check: Ensure no non-remote jobs slipped through
            if len(jobs_df) > 0:
                remaining_non_remote = len(jobs_df[jobs_df['is_remote'] == False])
                if remaining_non_remote > 0:
                    logger.warning(f"WARNING: {remaining_non_remote} non-remote jobs still present after filtering!")
                    jobs_df = jobs_df[jobs_df['is_remote'] == True]  # Apply filter again
                else:
                    logger.info("✅ VERIFIED: All remaining jobs are remote (is_remote=True)")
        else:
            logger.warning("⚠️ 'is_remote' column not found or DataFrame is empty")
        
        # Apply date filtering if specified
        if filter_date is not None and not jobs_df.empty and 'date_posted' in jobs_df.columns:
            # Convert date_posted to datetime if it's not already
            jobs_df['date_posted'] = pd.to_datetime(jobs_df['date_posted'], errors='coerce').dt.date
            
            # Filter for specific date
            initial_count = len(jobs_df)
            jobs_df = jobs_df[jobs_df['date_posted'] == filter_date]
            logger.info(f"After filtering for jobs from {filter_description}: {len(jobs_df)} jobs (removed {initial_count - len(jobs_df)} from other dates)")
        
        # Rename job_url column to job_board_url to free up "job_url" for user's custom use
        if 'job_url' in jobs_df.columns:
            jobs_df = jobs_df.rename(columns={'job_url': 'job_board_url'})
            
            # Add an empty job_url column for user's custom use
            jobs_df['job_url'] = None
            
            # Reorder columns to put job_board_url where job_url was, and job_url at the end
            cols = list(jobs_df.columns)
            # Remove job_url from current position
            cols.remove('job_url')
            # Insert job_url at the end (before any existing custom columns)
            cols.append('job_url')
            jobs_df = jobs_df[cols]
            
            logger.info("Renamed 'job_url' column to 'job_board_url' and added empty 'job_url' column for custom use")
            # Available URL columns after renaming:
            # - job_board_url: Original job board URL (e.g., Indeed, LinkedIn page)
            # - job_url_direct: Direct application URL (company career page, when available)
            # - job_url: Now available for your custom use! (empty column at the end)
            # - company_url: Company profile page on job board
            # - company_url_direct: Company's website
        
        # Create unique identifiers for new jobs
        jobs_df['job_id'] = jobs_df.apply(
            lambda x: f"{x['title']}|{x['company']}|{x['location']}", axis=1
        )
        
        # Filter out existing jobs
        new_jobs_df = jobs_df[~jobs_df['job_id'].isin(existing_jobs)]
        new_jobs_df = new_jobs_df.drop('job_id', axis=1)
        
        logger.info(f"Found {len(new_jobs_df)} new remote jobs from {filter_description} after filtering duplicates")
        
        # FINAL SAFETY CHECK: Ensure absolutely no non-remote jobs are being sent to Google Sheets
        if len(new_jobs_df) > 0 and 'is_remote' in new_jobs_df.columns:
            non_remote_final = len(new_jobs_df[new_jobs_df['is_remote'] == False])
            if non_remote_final > 0:
                logger.error(f"🚨 CRITICAL: {non_remote_final} non-remote jobs about to be sent to Google Sheets!")
                # Remove any remaining non-remote jobs as a final safeguard
                new_jobs_df = new_jobs_df[new_jobs_df['is_remote'] == True]
                logger.info(f"🛡️ SAFEGUARD: Removed {non_remote_final} non-remote jobs before Google Sheets update")
            
            logger.info(f"🎯 FINAL VERIFICATION: Sending {len(new_jobs_df)} confirmed remote jobs to Google Sheets")
        
        if len(new_jobs_df) > 0:
            # Update Google Sheet with new jobs
            update_google_sheet(new_jobs_df)
        else:
            logger.info(f"No new jobs from {filter_description} to add to Google Sheet")
        
        # Save local backup
        if not os.path.exists('job_results'):
            os.makedirs('job_results')
        
        filename = f"job_results/pharmacist_jobs_{date_filter_option}_{timestamp}.csv"
        new_jobs_df.to_csv(filename, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
        logger.info(f"Results saved to {filename}")
        
        return new_jobs_df
        
    except Exception as e:
        logger.error(f"Error in search_pharmacist_jobs_with_date_filter: {str(e)}")
        raise

def search_pharmacist_jobs():
    """Search for new pharmacist jobs posted today only."""
    return search_pharmacist_jobs_with_date_filter(date_filter_option="today")

if __name__ == "__main__":
    # Example usage:
    
    # Option 1: Only jobs posted today (recommended for clean results)
    print("=== Searching for jobs posted TODAY only ===")
    search_pharmacist_jobs_with_date_filter(date_filter_option="today")
    
    # Uncomment one of the following for different filtering options:
    
    # Option 2: Only jobs posted yesterday
    # search_pharmacist_jobs_with_date_filter(date_filter_option="yesterday")
    
    # Option 3: Jobs from last 12 hours (no additional date filtering)
    # search_pharmacist_jobs_with_date_filter(date_filter_option="last_12h")
    
    # Option 4: Jobs from last 24 hours (original behavior)
    # search_pharmacist_jobs_with_date_filter(date_filter_option="last_24h")
    
    # Option 5: Custom hours (e.g., last 6 hours)
    # search_pharmacist_jobs_with_date_filter(date_filter_option="custom_hours", hours_old=6) 