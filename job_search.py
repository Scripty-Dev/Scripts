from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import os
import hashlib
import json
from pathlib import Path
import requests

def get_base_directory():
    """Get the base directory in user's home folder"""
    home = str(Path.home())
    base = os.path.join(home, "Job Search Results")
    os.makedirs(base, exist_ok=True)
    return base

def save_description(description, descriptions_dir):
    """Save description to a separate file and return its ID"""
    if pd.isna(description) or description.strip() == '':
        return None
        
    desc_id = hashlib.md5(str(description).encode()).hexdigest()[:10]
    filepath = os.path.join(descriptions_dir, f"{desc_id}.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(description))
    
    return desc_id

def format_salary(row):
    """Format salary from min/max amounts into readable string"""
    if pd.isna(row.get('min_amount')):
        return 'Not specified'
    
    min_amt = f"${int(row['min_amount']):,}" if pd.notna(row.get('min_amount')) else ''
    max_amt = f"${int(row['max_amount']):,}" if pd.notna(row.get('max_amount')) else ''
    currency = row['currency'] if pd.notna(row.get('currency')) else 'CAD'  # Default to CAD for Toronto
    interval = row['interval'] if pd.notna(row.get('interval')) else 'yearly'
    
    if min_amt and max_amt:
        return f"{min_amt} - {max_amt} {currency} {interval}"
    elif min_amt:
        return f"{min_amt} {currency} {interval}"
    else:
        return 'Not specified'

def export_to_sheets(jobs_data, authtoken):
    """Export jobs data to Google Sheets"""
    try:
        headers = {
            "Authorization": f"Bearer {authtoken}",
            "Content-Type": "application/json"
        }
        
        # Format the data for sheets
        data = {
            "jobs": jobs_data
        }
        
        response = requests.post(
            "https://scripty.me/api/assistant/sheets/job-search",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_jobs(job_title, location, authtoken=None):
    """Main function to search for jobs"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        base_dir = get_base_directory()
        search_dir = os.path.join(base_dir, f"search_{timestamp}")
        os.makedirs(search_dir, exist_ok=True)

        city = location.split(',')[0].strip()
        country = "Canada" if "ON" in location.upper() else "USA"
        
        search_term = f'"{job_title}"'
        google_search_term = f"{job_title} jobs in {city}"

        print(f"Searching for {job_title} jobs in {location}...")
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
            search_term=search_term,
            location=location,
            google_search_term=google_search_term,
            country_indeed=country,
            results_wanted=100,
            hours_old=72,
            description_format="markdown",
            fetch_full_description=True,
            return_as_df=True,
            delay=[2, 5],
            random_headers=True
        )
        
        # Convert jobs DataFrame to records and back to ensure numpy arrays are converted
        jobs_records = jobs.to_dict('records')
        filtered_jobs = pd.DataFrame(jobs_records)
        
        # Convert date_posted to string format, handling both datetime and string inputs
        if 'date_posted' in filtered_jobs.columns:
            filtered_jobs['date_posted'] = pd.to_datetime(filtered_jobs['date_posted']).dt.strftime('%Y-%m-%d')
        
        filtered_jobs['salary'] = filtered_jobs.apply(format_salary, axis=1)
        filtered_jobs['status'] = 'Not Applied'
        
        relevant_columns = [
            'title', 'company', 'location', 'date_posted', 'job_type',
            'is_remote', 'company_industry', 'job_url', 'salary', 'status'
        ]
        
        existing_columns = [col for col in relevant_columns if col in filtered_jobs.columns]
        filtered_jobs = filtered_jobs[existing_columns]
        
        filtered_jobs = filtered_jobs.drop_duplicates(
            subset=['title', 'company', 'job_url'], 
            keep='first'
        )
        
        if 'date_posted' in filtered_jobs.columns:
            filtered_jobs = filtered_jobs.sort_values('date_posted', ascending=False)
        
        csv_path = os.path.join(search_dir, "jobs.csv")
        filtered_jobs.to_csv(csv_path, index=False)
        
        metadata = {
            'timestamp': timestamp,
            'total_jobs': len(filtered_jobs),
            'search_term': search_term,
            'location': location,
            'date_range': '3 days'
        }
        with open(os.path.join(search_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)

        results = filtered_jobs.to_dict('records')
        
        result = {
            "success": True,
            "jobs_found": len(filtered_jobs),
            "save_location": search_dir,
            "results": results
        }
        
        if authtoken:
            sheets_result = export_to_sheets(results, authtoken)
            result["sheets_export"] = sheets_result
            
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
# API definition
object = {
    "name": "job_search",
    "description": "Search for jobs across multiple platforms and save results to CSV and Google Sheets",
    "parameters": {
        "type": "object",
        "properties": {
            "job_title": {
                "type": "string",
                "description": "Job title to search for (e.g., 'software engineer', 'data scientist')"
            },
            "location": {
                "type": "string",
                "description": "Location to search in (e.g., 'Toronto, ON', 'San Francisco, CA')"
            },
            "export_to_sheets": {
                "type": "boolean",
                "description": "Whether to export results to Google Sheets (requires Google authentication)",
                "default": True
            }
        },
        "required": ["job_title", "location"]
    }
}

# Required modules
modules = ['python-jobspy', 'pandas', 'requests']

async def func(args):
    """Handler function for the API"""
    try:
        if not args.get("job_title"):
            return json.dumps({
                "success": False,
                "error": "Job title is required"
            })
            
        if not args.get("location"):
            return json.dumps({
                "success": False,
                "error": "Location is required"
            })
            
        result = search_jobs(args["job_title"], args["location"], authtoken)
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
