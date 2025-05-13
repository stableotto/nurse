#!/bin/bash

# Get the current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the cron job command
CRON_CMD="0 9 * * * cd ${DIR} && /usr/local/bin/python3 ${DIR}/pharmacist_job_search.py >> ${DIR}/job_results/cron.log 2>&1"

# Add the cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "Cron job has been scheduled to run daily at 9:00 AM"
echo "To view scheduled cron jobs, use: crontab -l" 