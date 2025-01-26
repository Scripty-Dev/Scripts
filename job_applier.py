import requests
import logging
import time
import json
import sys
import asyncio
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import PyPDF2
import io
import docx

logging.basicConfig(level=logging.INFO)

def extract_resume_text(file_content, file_type):
    try:
        if file_type == 'pdf':
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        elif file_type == 'docx':
            doc = docx.Document(io.BytesIO(file_content))
            return " ".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            return None
    except Exception as e:
        logging.error(f"Error extracting resume text: {str(e)}")
        return None

def parse_resume(text):
    # Basic parsing - expand with more sophisticated NLP as needed
    sections = {
        'skills': set(),
        'experience': [],
        'education': [],
        'contact': {}
    }
    
    # Add your parsing logic here based on common resume formats
    # This is a simplified version - consider using NLP libraries for better results
    
    return sections

async def apply_linkedin_jobs(resume_data, search_terms):
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        jobs = []
        url = f'https://www.linkedin.com/jobs/search/?keywords={"+".join(search_terms)}'
        
        driver.get(url)
        time.sleep(2)
        
        job_cards = wait_and_find_all(driver, By.CLASS_NAME, 'job-card-container')
        
        for card in job_cards[:5]:  # Limit to 5 jobs for demonstration
            try:
                title = card.find_element(By.CLASS_NAME, 'job-card-list__title').text
                company = card.find_element(By.CLASS_NAME, 'job-card-container__company-name').text
                link = card.find_element(By.CLASS_NAME, 'job-card-list__title').get_attribute('href')
                
                # Match resume skills with job requirements
                job_desc = card.find_element(By.CLASS_NAME, 'job-card-list__description').text
                skill_match = len([skill for skill in resume_data['skills'] 
                                 if skill.lower() in job_desc.lower()])
                
                jobs.append({
                    'platform': 'LinkedIn',
                    'title': title,
                    'company': company,
                    'url': link,
                    'skill_match': f"{skill_match} skills matched"
                })
                
            except Exception as e:
                continue
                
        return jobs
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()

async def apply_indeed_jobs(resume_data, search_terms):
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        jobs = []
        url = f'https://www.indeed.com/jobs?q={"+".join(search_terms)}'
        
        driver.get(url)
        time.sleep(2)
        
        job_cards = wait_and_find_all(driver, By.CLASS_NAME, 'job_seen_beacon')
        
        for card in job_cards[:5]:  # Limit to 5 jobs
            try:
                title = card.find_element(By.CLASS_NAME, 'jobTitle').text
                company = card.find_element(By.CLASS_NAME, 'companyName').text
                link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')
                
                # Match resume skills with job description
                job_desc = card.find_element(By.CLASS_NAME, 'job-snippet').text
                skill_match = len([skill for skill in resume_data['skills'] 
                                 if skill.lower() in job_desc.lower()])
                
                jobs.append({
                    'platform': 'Indeed',
                    'title': title,
                    'company': company,
                    'url': link,
                    'skill_match': f"{skill_match} skills matched"
                })
                
            except Exception as e:
                continue
                
        return jobs
        
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()

async def func(args):
    try:
        resume_file = args.get('resume')
        search_terms = args.get('search_terms', [])
        
        if not resume_file or not search_terms:
            return json.dumps({"error": "Resume file and search terms required"})
            
        # Extract and parse resume
        resume_text = extract_resume_text(resume_file['content'], resume_file['type'])
        if not resume_text:
            return json.dumps({"error": "Unable to extract resume text"})
            
        resume_data = parse_resume(resume_text)
        
        results = {
            "message": f"Job search results for: {', '.join(search_terms)}",
            "results": []
        }
        
        # Get jobs from both platforms
        linkedin_jobs = await apply_linkedin_jobs(resume_data, search_terms)
        if isinstance(linkedin_jobs, list):
            results["results"].extend(linkedin_jobs)
            
        indeed_jobs = await apply_indeed_jobs(resume_data, search_terms)
        if isinstance(indeed_jobs, list):
            results["results"].extend(indeed_jobs)
            
        return json.dumps(results)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "job_applicator",
    "description": "Search and apply for jobs on LinkedIn and Indeed based on resume analysis",
    "parameters": {
        "type": "object",
        "properties": {
            "resume": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "format": "binary"},
                    "type": {"type": "string", "enum": ["pdf", "docx"]}
                },
                "required": ["content", "type"]
            },
            "search_terms": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Job search keywords"
            }
        },
        "required": ["resume", "search_terms"]
    }
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1])
                result = asyncio.run(func(args))
                print(result)
            except Exception as e:
                print(json.dumps({"error": str(e)}))
