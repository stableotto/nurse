# 🚀 GitHub Actions Setup Instructions

## Quick Setup Guide

### 1. Create GitHub Repository
```bash
# Create a new repository on GitHub, then:
git init
git add .
git commit -m "Initial commit: Daily nurse jobs automation"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

### 2. Enable GitHub Actions
1. Go to your repository on GitHub
2. Click **Actions** tab
3. If prompted, click **"I understand my workflows"** to enable Actions

### 3. Verify Workflow File
Ensure `.github/workflows/daily-nurse-jobs.yml` exists and contains the automation workflow.

### 4. Test Manual Run
1. Go to **Actions** tab
2. Click **"Daily Nurse Job Search"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the execution in real-time

### 5. Access Your Feed
After the first successful run:
- **XML Feed:** `https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/nurses_jobs_feed.xml`
- **CSV Results:** Check the `job_results/` folder in your repository

## 🔧 Configuration Options

### Change Schedule
Edit `.github/workflows/daily-nurse-jobs.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'  # 9 AM UTC daily
  - cron: '0 21 * * *' # 9 PM UTC daily (add for twice daily)
```

### Modify Search Parameters
Edit `nurse_job_search.py`:
```python
# Line ~185: Adjust search parameters
jobs = scrape_jobs(
    search_term="nurse",              # Change search term
    location="United States",         # Change location  
    results_wanted=500,              # Increase/decrease results
    hours_old=scrape_hours_old,      # Time window
)

# Line ~155: Change filter mode
FILTER_MODE = "strict"    # "strict", "moderate", or "none"
```

## 📊 Understanding the Output

### Daily CSV Files
Location: `job_results/nurse_jobs_today_YYYYMMDD.csv`

Contains all filtered job data with columns:
- `title`, `company`, `location`
- `job_board_url`, `job_url_direct`, `job_url` (custom)
- `date_posted`, `job_type`, `is_remote`
- `min_amount`, `max_amount`, `currency`, `interval`
- `description`, `company_url`, etc.

### XML RSS Feed
Location: `nurses_jobs_feed.xml`

RSS-compatible feed with:
- Job titles and companies
- Direct application URLs
- Formatted descriptions
- Publication dates
- Categories

## 🔗 Feed Integration Examples

### RSS Readers
Add this URL to any RSS reader:
```
https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/nurses_jobs_feed.xml
```

### Discord Bot
Use RSS Bot or similar:
```
/rss add https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/nurses_jobs_feed.xml
```

### Slack Integration
Use RSS app:
```
/feed subscribe https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/nurses_jobs_feed.xml
```

### Custom Application
```python
import feedparser

feed = feedparser.parse('https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/nurses_jobs_feed.xml')
for entry in feed.entries:
    print(f"Job: {entry.title}")
    print(f"Link: {entry.link}")
    print(f"Description: {entry.description}")
```

## 🐛 Troubleshooting

### Workflow Fails
1. Check **Actions** tab for error details
2. Common issues:
   - Repository permissions
   - Invalid workflow YAML syntax
   - Python dependency issues

### No Jobs Found
1. Check if job sites are blocking requests
2. Try different search terms
3. Adjust time window (use "last_24h" instead of "today")

### XML Feed Issues
1. Verify CSV files are generating in `job_results/`
2. Check if `generate_xml_feed.py` runs without errors
3. Validate XML at https://validator.w3.org/feed/

### Rate Limiting
Job sites may block requests. Solutions:
1. Reduce `results_wanted` parameter
2. Add delays between requests
3. Use proxies (advanced)

## 📈 Performance Tips

### Optimal Schedule
- Run once daily during off-peak hours
- Avoid weekend runs if not needed
- Consider timezone of target job markets

### Result Quality
- Use "strict" filter mode for best direct URLs
- Monitor `job_results/` folder size
- Adjust search terms based on results

### Feed Management
- RSS feed updates automatically
- Old CSV files accumulate (consider cleanup)
- Monitor GitHub Actions minutes usage

## 🔐 Security Notes

- No credentials needed for basic setup
- All data is public in repository
- Job search data contains no sensitive information
- RSS feed is publicly accessible

## 📞 Support

### GitHub Actions Documentation
- [GitHub Actions Quickstart](https://docs.github.com/en/actions/quickstart)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

### Issues
Create an issue in this repository for:
- Bugs or errors
- Feature requests  
- Setup problems
- Performance issues 