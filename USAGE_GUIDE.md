# JobSpy Date Filtering Usage Guide

## Overview

Your JobSpy script has been updated to provide flexible date filtering options. Now you can easily scrape jobs from specific time periods to keep your Google Sheet clean and organized.

## Key Changes

### ✅ Date Filtering
Multiple options to filter jobs by posting date (see below for details).

### ✅ Column Renaming
- **`job_url` → `job_board_url`**: The original JobSpy URL column is now renamed to `job_board_url`
- **`job_url`**: This column name is now available for your custom use
- **`job_url_direct`**: Still available (contains direct application URLs when available)

## Column Layout After Changes

Your Google Sheet will now have these URL-related columns in this order:

1. **`job_board_url`** (position 3): Original job board URLs (Indeed, LinkedIn, etc.)
2. **`job_url_direct`** (position 4): Direct application URLs (company career pages)
3. **`company_url`** (position 22): Company profile pages on job boards  
4. **`company_url_direct`** (position 24): Company websites
5. **`job_url`** (last column): **Empty column ready for your custom URLs!** 🎯

## Available Filtering Options

### 1. Today Only (Recommended)
```python
search_pharmacist_jobs_with_date_filter(date_filter_option="today")
```
- **What it does**: Scrapes jobs from the last 12 hours, then filters to only include jobs posted today
- **Best for**: Daily runs to get only fresh jobs
- **Output file**: `pharmacist_jobs_today_YYYYMMDD.csv`

### 2. Yesterday Only
```python
search_pharmacist_jobs_with_date_filter(date_filter_option="yesterday")
```
- **What it does**: Scrapes jobs from the last 36 hours, then filters to only include jobs posted yesterday
- **Best for**: Catching up on jobs you might have missed
- **Output file**: `pharmacist_jobs_yesterday_YYYYMMDD.csv`

### 3. Last 12 Hours
```python
search_pharmacist_jobs_with_date_filter(date_filter_option="last_12h")
```
- **What it does**: Gets all jobs posted in the last 12 hours (no additional date filtering)
- **Best for**: Very recent jobs only
- **Output file**: `pharmacist_jobs_last_12h_YYYYMMDD.csv`

### 4. Last 24 Hours (Original Behavior)
```python
search_pharmacist_jobs_with_date_filter(date_filter_option="last_24h")
```
- **What it does**: Gets all jobs posted in the last 24 hours (your original setup)
- **Best for**: When you want more results but still relatively recent
- **Output file**: `pharmacist_jobs_last_24h_YYYYMMDD.csv`

### 5. Custom Hours
```python
search_pharmacist_jobs_with_date_filter(date_filter_option="custom_hours", hours_old=6)
```
- **What it does**: Gets all jobs posted in the last X hours (specify your own number)
- **Best for**: Fine-tuning based on your needs
- **Output file**: `pharmacist_jobs_custom_hours_YYYYMMDD.csv`

## How to Use

### Quick Start (Recommended)
Simply run the script as-is - it's now set to only get jobs posted today:
```bash
python pharmacist_job_search.py
```

### Customize Your Search
Edit the main execution block in `pharmacist_job_search.py`:

```python
if __name__ == "__main__":
    # Change this line to use a different filter:
    search_pharmacist_jobs_with_date_filter(date_filter_option="today")  # Change "today" to your preference
```

### Schedule Different Searches
You can run different searches throughout the day:

**Morning run** (catch today's jobs):
```python
search_pharmacist_jobs_with_date_filter(date_filter_option="today")
```

**Evening run** (catch very recent jobs):
```python
search_pharmacist_jobs_with_date_filter(date_filter_option="last_12h")
```

## Key Benefits

1. **Cleaner Google Sheet**: No more duplicate or old jobs cluttering your results
2. **Better Organization**: File names include the filter type and date
3. **Flexible Scheduling**: Run different filters at different times
4. **Improved Logging**: See exactly how many jobs were filtered out from each date

## Example Log Output

```
INFO - Found 45 existing jobs in Google Sheet
INFO - Searching for jobs from today...
INFO - Scraped 120 total jobs
INFO - Found 95 remote jobs after filtering
INFO - After filtering for jobs from today: 23 jobs (removed 72 from other dates)
INFO - Found 18 new remote jobs from today after filtering duplicates
INFO - Successfully added 18 new jobs to Google Sheet
INFO - Results saved to job_results/pharmacist_jobs_today_20241220.csv
```

## Troubleshooting

### No Jobs Found
- Try increasing the time window: use "last_24h" instead of "today"
- Check if jobs are actually being posted on weekends/holidays
- Verify your search terms and location settings

### Too Many Old Jobs
- Use "today" filter for the cleanest results
- Consider running the script more frequently (e.g., twice a day)

### Missing Recent Jobs
- Some job sites may have delays in posting dates
- Try "last_12h" to catch jobs that might be mis-dated

## Backward Compatibility

The original `search_pharmacist_jobs()` function still works and now defaults to "today only" filtering:

```python
search_pharmacist_jobs()  # Same as search_pharmacist_jobs_with_date_filter(date_filter_option="today")
``` 