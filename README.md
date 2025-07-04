<img src="https://github.com/cullenwatson/JobSpy/assets/78247585/ae185b7e-e444-4712-8bb9-fa97f53e896b" width="400">

**JobSpy** is a job scraping library with the goal of aggregating all the jobs from popular job boards with one tool.

## Features

- Scrapes job postings from **LinkedIn**, **Indeed**, **Glassdoor**, **Google**, **ZipRecruiter**, **Bayt** & **Naukri** concurrently
- Aggregates the job postings in a dataframe
- Proxies support to bypass blocking

![jobspy](https://github.com/cullenwatson/JobSpy/assets/78247585/ec7ef355-05f6-4fd3-8161-a817e31c5c57)

### Installation

```
pip install -U python-jobspy
```

_Python version >= [3.10](https://www.python.org/downloads/release/python-3100/) required_

### Usage

```python
import csv
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt", "naukri"],
    search_term="software engineer",
    google_search_term="software engineer jobs near San Francisco, CA since yesterday",
    location="San Francisco, CA",
    results_wanted=20,
    hours_old=72,
    country_indeed='USA',
    
    # linkedin_fetch_description=True # gets more info such as description, direct job url (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False) # to_excel
```

### Output

```
SITE           TITLE                             COMPANY           CITY          STATE  JOB_TYPE  INTERVAL  MIN_AMOUNT  MAX_AMOUNT  JOB_URL                                            DESCRIPTION
indeed         Software Engineer                 AMERICAN SYSTEMS  Arlington     VA     None      yearly    200000      150000      https://www.indeed.com/viewjob?jk=5e409e577046...  THIS POSITION COMES WITH A 10K SIGNING BONUS!...
indeed         Senior Software Engineer          TherapyNotes.com  Philadelphia  PA     fulltime  yearly    135000      110000      https://www.indeed.com/viewjob?jk=da39574a40cb...  About Us TherapyNotes is the national leader i...
linkedin       Software Engineer - Early Career  Lockheed Martin   Sunnyvale     CA     fulltime  yearly    None        None        https://www.linkedin.com/jobs/view/3693012711      Description:By bringing together people that u...
linkedin       Full-Stack Software Engineer      Rain              New York      NY     fulltime  yearly    None        None        https://www.linkedin.com/jobs/view/3696158877      Rain’s mission is to create the fastest and ea...
zip_recruiter Software Engineer - New Grad       ZipRecruiter      Santa Monica  CA     fulltime  yearly    130000      150000      https://www.ziprecruiter.com/jobs/ziprecruiter...  We offer a hybrid work environment. Most US-ba...
zip_recruiter Software Developer                 TEKsystems        Phoenix       AZ     fulltime  hourly    65          75          https://www.ziprecruiter.com/jobs/teksystems-0...  Top Skills' Details• 6 years of Java developme...

```

### Parameters for `scrape_jobs()`

```plaintext
Optional
├── site_name (list|str): 
|    linkedin, zip_recruiter, indeed, glassdoor, google, bayt
|    (default is all)
│
├── search_term (str)
|
├── google_search_term (str)
|     search term for google jobs. This is the only param for filtering google jobs.
│
├── location (str)
│
├── distance (int): 
|    in miles, default 50
│
├── job_type (str): 
|    fulltime, parttime, internship, contract
│
├── proxies (list): 
|    in format ['user:pass@host:port', 'localhost']
|    each job board scraper will round robin through the proxies
|
├── is_remote (bool)
│
├── results_wanted (int): 
|    number of job results to retrieve for each site specified in 'site_name'
│
├── easy_apply (bool): 
|    filters for jobs that are hosted on the job board site (LinkedIn easy apply filter no longer works)
│
├── description_format (str): 
|    markdown, html (Format type of the job descriptions. Default is markdown.)
│
├── offset (int): 
|    starts the search from an offset (e.g. 25 will start the search from the 25th result)
│
├── hours_old (int): 
|    filters jobs by the number of hours since the job was posted 
|    (ZipRecruiter and Glassdoor round up to next day.)
│
├── verbose (int) {0, 1, 2}: 
|    Controls the verbosity of the runtime printouts 
|    (0 prints only errors, 1 is errors+warnings, 2 is all logs. Default is 2.)

├── linkedin_fetch_description (bool): 
|    fetches full description and direct job url for LinkedIn (Increases requests by O(n))
│
├── linkedin_company_ids (list[int]): 
|    searches for linkedin jobs with specific company ids
|
├── country_indeed (str): 
|    filters the country on Indeed & Glassdoor (see below for correct spelling)
|
├── enforce_annual_salary (bool): 
|    converts wages to annual salary
|
├── ca_cert (str)
|    path to CA Certificate file for proxies
```

```
├── Indeed limitations:
|    Only one from this list can be used in a search:
|    - hours_old
|    - job_type & is_remote
|    - easy_apply
│
└── LinkedIn limitations:
|    Only one from this list can be used in a search:
|    - hours_old
|    - easy_apply
```

## Supported Countries for Job Searching

### **LinkedIn**

LinkedIn searches globally & uses only the `location` parameter. 

### **ZipRecruiter**

ZipRecruiter searches for jobs in **US/Canada** & uses only the `location` parameter.

### **Indeed / Glassdoor**

Indeed & Glassdoor supports most countries, but the `country_indeed` parameter is required. Additionally, use the `location`
parameter to narrow down the location, e.g. city & state if necessary. 

You can specify the following countries when searching on Indeed (use the exact name, * indicates support for Glassdoor):

|                      |              |            |                |
|----------------------|--------------|------------|----------------|
| Argentina            | Australia*   | Austria*   | Bahrain        |
| Belgium*             | Brazil*      | Canada*    | Chile          |
| China                | Colombia     | Costa Rica | Czech Republic |
| Denmark              | Ecuador      | Egypt      | Finland        |
| France*              | Germany*     | Greece     | Hong Kong*     |
| Hungary              | India*       | Indonesia  | Ireland*       |
| Israel               | Italy*       | Japan      | Kuwait         |
| Luxembourg           | Malaysia     | Mexico*    | Morocco        |
| Netherlands*         | New Zealand* | Nigeria    | Norway         |
| Oman                 | Pakistan     | Panama     | Peru           |
| Philippines          | Poland       | Portugal   | Qatar          |
| Romania              | Saudi Arabia | Singapore* | South Africa   |
| South Korea          | Spain*       | Sweden     | Switzerland*   |
| Taiwan               | Thailand     | Turkey     | Ukraine        |
| United Arab Emirates | UK*          | USA*       | Uruguay        |
| Venezuela            | Vietnam*     |            |                |

### **Bayt**

Bayt only uses the search_term parameter currently and searches internationally



## Notes
* Indeed is the best scraper currently with no rate limiting.  
* All the job board endpoints are capped at around 1000 jobs on a given search.  
* LinkedIn is the most restrictive and usually rate limits around the 10th page with one ip. Proxies are a must basically.

## Frequently Asked Questions

---
**Q: Why is Indeed giving unrelated roles?**  
**A:** Indeed searches the description too.

- use - to remove words
- "" for exact match

Example of a good Indeed query

```py
search_term='"engineering intern" software summer (java OR python OR c++) 2025 -tax -marketing'
```

This searches the description/title and must include software, summer, 2025, one of the languages, engineering intern exactly, no tax, no marketing.

---

**Q: No results when using "google"?**  
**A:** You have to use super specific syntax. Search for google jobs on your browser and then whatever pops up in the google jobs search box after applying some filters is what you need to copy & paste into the google_search_term. 

---

**Q: Received a response code 429?**  
**A:** This indicates that you have been blocked by the job board site for sending too many requests. All of the job board sites are aggressive with blocking. We recommend:

- Wait some time between scrapes (site-dependent).
- Try using the proxies param to change your IP address.

---

### JobPost Schema

```plaintext
JobPost
├── title
├── company
├── company_url
├── job_url
├── location
│   ├── country
│   ├── city
│   ├── state
├── is_remote
├── description
├── job_type: fulltime, parttime, internship, contract
├── job_function
│   ├── interval: yearly, monthly, weekly, daily, hourly
│   ├── min_amount
│   ├── max_amount
│   ├── currency
│   └── salary_source: direct_data, description (parsed from posting)
├── date_posted
└── emails

Linkedin specific
└── job_level

Linkedin & Indeed specific
└── company_industry

Indeed specific
├── company_country
├── company_addresses
├── company_employees_label
├── company_revenue_label
├── company_description
└── company_logo

Naukri specific
├── skills
├── experience_range
├── company_rating
├── company_reviews_count
├── vacancy_count
└── work_from_home_type
```

# Daily Nurse Jobs Feed

Automated daily nurse job search with direct company application links, delivered via XML RSS feed.

## 🚀 Features

- **Daily automated job search** for nursing positions across the US
- **Direct company URLs only** - filters out Indeed redirect links
- **XML RSS feed** - easy integration with feed readers or other systems
- **GitHub Actions powered** - runs automatically every day
- **Comprehensive filtering** - jobs posted today only, all job types (remote, on-site, hybrid)

## 📊 Current Feed

The latest nurse jobs feed is available at: `nurses_jobs_feed.xml`

## 🔧 Setup for GitHub Actions

### 1. Repository Setup
```bash
# Clone and push to your GitHub repository
git clone <your-repo-url>
cd <your-repo>
git add .
git commit -m "Initial setup for daily nurse jobs"
git push origin main
```

### 2. Enable GitHub Actions
1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. Enable GitHub Actions if prompted
4. The workflow will run automatically daily at 9:00 AM UTC

### 3. Manual Trigger
You can manually trigger the job search:
1. Go to **Actions** tab in your repository
2. Click on **Daily Nurse Job Search**
3. Click **Run workflow**

## 📁 Output Files

- **`job_results/nurse_jobs_today_YYYYMMDD.csv`** - Daily CSV results
- **`nurses_jobs_feed.xml`** - RSS XML feed (updated daily)

## 🎯 Filtering Criteria

- **Search term:** "nurse" (nationwide US search)
- **Date filter:** Jobs posted today only
- **URL filter:** Only jobs with direct company application links (excludes Indeed redirects)
- **Job types:** All types included (remote, on-site, hybrid)
- **Results:** Up to 500 jobs scraped, filtered down to today's direct-link jobs

## 📋 XML Feed Format

The RSS feed includes:
- Job title and company
- Location and job type
- Salary information (when available)
- Direct application URLs
- Job descriptions (truncated)
- Publication date

## 🛠️ Local Development

### Prerequisites
- Python 3.10+
- Virtual environment (recommended)

### Installation
```bash
# Create virtual environment
python3 -m venv nurse_env
source nurse_env/bin/activate  # On Windows: nurse_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Manual Run
```bash
# Search for jobs
python3 nurse_job_search.py

# Generate XML feed
python3 generate_xml_feed.py
```

## 📈 Filter Modes

The script supports different filtering modes in `nurse_job_search.py`:

```python
FILTER_MODE = "strict"    # Only direct company URLs (recommended)
FILTER_MODE = "moderate"  # All jobs, flagged which are direct
FILTER_MODE = "none"      # All jobs, no URL filtering
```

## 🔗 Accessing the Feed

### Direct Access
- Raw XML: `https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/nurses_jobs_feed.xml`
- Repository: `https://github.com/YOUR-USERNAME/YOUR-REPO/blob/main/nurses_jobs_feed.xml`

### RSS Feed Readers
Add the raw GitHub URL to any RSS reader:
- Feedly
- Inoreader  
- RSS Bot for Discord/Slack
- Custom applications

## ⚙️ Customization

### Change Schedule
Edit `.github/workflows/daily-nurse-jobs.yml`:
```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

### Modify Search Parameters
Edit `nurse_job_search.py`:
```python
jobs = scrape_jobs(
    search_term="nurse",           # Change search term
    location="United States",      # Change location
    results_wanted=500,           # Adjust result count
    hours_old=scrape_hours_old,   # Adjust time window
)
```

## 🐛 Troubleshooting

### GitHub Actions Issues
1. Check **Actions** tab for error logs
2. Verify repository permissions for Actions
3. Ensure `requirements.txt` includes all dependencies

### Feed Issues
1. Check if CSV files are being generated in `job_results/`
2. Verify XML feed exists and is valid
3. Test locally with `python3 generate_xml_feed.py`

## 📧 Support

For issues or questions, please create an issue in this repository.

## 📄 License

MIT License - see LICENSE file for details.
