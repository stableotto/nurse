#!/usr/bin/env python3
"""
Generate XML RSS feed from nurse job search results.
"""

import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import glob
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def create_rss_feed(jobs_df, output_file="nurses_jobs_feed.xml"):
    """
    Create an RSS feed from the jobs DataFrame.
    """
    # Create RSS root element
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    
    # Create channel
    channel = ET.SubElement(rss, "channel")
    
    # Channel metadata
    ET.SubElement(channel, "title").text = "Daily Nurse Jobs Feed"
    ET.SubElement(channel, "description").text = "Daily feed of nursing jobs with direct company application links"
    ET.SubElement(channel, "link").text = "https://github.com/your-username/your-repo"  # Update with your repo URL
    ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    ET.SubElement(channel, "generator").text = "Nurse Job Search Bot"
    ET.SubElement(channel, "language").text = "en-us"
    
    # Add jobs as items
    for _, job in jobs_df.iterrows():
        item = ET.SubElement(channel, "item")
        
        # Job title and company
        title = f"{job.get('title', 'N/A')} at {job.get('company', 'N/A')}"
        ET.SubElement(item, "title").text = title
        
        # Job URL (prefer direct URL, fallback to board URL)
        job_url = job.get('job_url_direct', job.get('job_board_url', ''))
        if job_url:
            ET.SubElement(item, "link").text = str(job_url)
        
        # Unique identifier
        guid = ET.SubElement(item, "guid")
        guid.text = f"{job.get('company', '')}-{job.get('title', '')}-{job.get('location', '')}"
        guid.set("isPermaLink", "false")
        
        # Publication date - Use current date when XML is generated, not the old job posting date
        # This ensures the XML feed shows current timestamps even for older job data
        current_time = datetime.now()
        ET.SubElement(item, "pubDate").text = current_time.strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        # Description with job details
        description_parts = []
        
        # Location
        if pd.notna(job.get('location')):
            description_parts.append(f"📍 Location: {job['location']}")
        
        # Job type
        if pd.notna(job.get('job_type')):
            description_parts.append(f"💼 Type: {job['job_type'].title()}")
        
        # Remote status
        if pd.notna(job.get('is_remote')):
            remote_status = "Remote" if job['is_remote'] else "On-site"
            description_parts.append(f"🏠 Work: {remote_status}")
        
        # Salary information
        if pd.notna(job.get('min_amount')) and pd.notna(job.get('max_amount')):
            currency = job.get('currency', 'USD')
            interval = job.get('interval', 'yearly')
            description_parts.append(f"💰 Salary: {currency} {job['min_amount']:,.0f} - {job['max_amount']:,.0f} ({interval})")
        elif pd.notna(job.get('min_amount')):
            currency = job.get('currency', 'USD')
            interval = job.get('interval', 'yearly')
            description_parts.append(f"💰 Salary: {currency} {job['min_amount']:,.0f}+ ({interval})")
        
        # Job description (truncated)
        if pd.notna(job.get('description')):
            desc_text = str(job['description'])[:500]
            if len(str(job['description'])) > 500:
                desc_text += "..."
            description_parts.append(f"\n📝 Description: {desc_text}")
        
        # Application URLs
        url_parts = []
        if pd.notna(job.get('job_url_direct')) and 'indeed.com' not in str(job['job_url_direct']).lower():
            url_parts.append(f"🔗 Apply Direct: {job['job_url_direct']}")
        if pd.notna(job.get('job_board_url')):
            url_parts.append(f"🔗 Job Board: {job['job_board_url']}")
        
        if url_parts:
            description_parts.extend(url_parts)
        
        description_text = "\n".join(description_parts)
        ET.SubElement(item, "description").text = description_text
        
        # Add custom XML tags for structured data
        # Company Name
        if pd.notna(job.get('company')):
            ET.SubElement(item, "companyName").text = str(job['company'])
        
        # Job Type
        if pd.notna(job.get('job_type')):
            job_type_value = job['job_type']
            if isinstance(job_type_value, list):
                job_type_text = ", ".join(str(jt).title() for jt in job_type_value)
            else:
                job_type_text = str(job_type_value).title()
            ET.SubElement(item, "jobType").text = job_type_text
        
        # Location
        if pd.notna(job.get('location')):
            ET.SubElement(item, "jobLocation").text = str(job['location'])
        
        # Salary Min
        if pd.notna(job.get('min_amount')):
            ET.SubElement(item, "salaryMin").text = str(int(job['min_amount']))
        
        # Salary Max
        if pd.notna(job.get('max_amount')):
            ET.SubElement(item, "salaryMax").text = str(int(job['max_amount']))
        
        # Salary Schedule (interval)
        if pd.notna(job.get('interval')):
            ET.SubElement(item, "salarySchedule").text = str(job['interval']).lower()
        
        # Currency (bonus tag)
        if pd.notna(job.get('currency')):
            ET.SubElement(item, "salaryCurrency").text = str(job['currency'])
        
        # Remote work status (bonus tag)
        if pd.notna(job.get('is_remote')):
            ET.SubElement(item, "isRemote").text = str(job['is_remote']).lower()
        
        # Category
        ET.SubElement(item, "category").text = "Nursing Jobs"
    
    # Create the XML tree
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)  # Pretty print
    
    # Write to file
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    logger.info(f"RSS feed created: {output_file} with {len(jobs_df)} jobs")

def get_latest_csv_file():
    """
    Find the most recent nurse jobs CSV file.
    """
    pattern = "job_results/nurse_jobs_today_*.csv"
    files = glob.glob(pattern)
    
    if not files:
        logger.error("No nurse job CSV files found!")
        return None
    
    # Get the most recent file
    latest_file = max(files, key=os.path.getctime)
    logger.info(f"Using latest CSV file: {latest_file}")
    return latest_file

def main():
    """
    Main function to generate the XML feed.
    """
    try:
        # Find the latest CSV file
        csv_file = get_latest_csv_file()
        if not csv_file:
            return
        
        # Read the CSV data
        jobs_df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(jobs_df)} jobs from {csv_file}")
        
        if len(jobs_df) == 0:
            logger.warning("No jobs found in CSV file")
            # Create empty feed
            empty_df = pd.DataFrame()
            create_rss_feed(empty_df)
            return
        
        # Create the RSS feed
        create_rss_feed(jobs_df)
        
        # Create a summary
        total_jobs = len(jobs_df)
        direct_urls = len(jobs_df[
            (jobs_df['job_url_direct'].notna()) & 
            (~jobs_df['job_url_direct'].str.contains('indeed.com', case=False, na=False))
        ]) if 'job_url_direct' in jobs_df.columns else 0
        
        logger.info(f"✅ XML Feed Generated Successfully!")
        logger.info(f"📊 Total jobs: {total_jobs}")
        logger.info(f"🔗 Direct company URLs: {direct_urls}")
        logger.info(f"📁 Feed saved as: nurses_jobs_feed.xml")
        
    except Exception as e:
        logger.error(f"Error generating XML feed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 