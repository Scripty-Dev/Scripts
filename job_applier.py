import tkinter as tk
from tkinter import ttk, messagebox
import logging
import time
import json
import os
from pathlib import Path
import asyncio
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import PyPDF2
import docx
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ResumeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def extract_text(self):
        if self.file_path.lower().endswith('.pdf'):
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
        elif self.file_path.lower().endswith('.docx'):
            doc = docx.Document(self.file_path)
            text = " ".join([paragraph.text for paragraph in doc.paragraphs])
        else:
            raise ValueError("Unsupported file format")
        return text
        
    def extract_job_titles(self):
        text = self.extract_text()
        # Common job titles in tech
        job_titles = [
            "software engineer", "software developer", "full stack", "backend", "frontend",
            "python developer", "java developer", "web developer", "data engineer",
            "devops engineer", "ml engineer", "data scientist"
        ]
        found_titles = []
        for title in job_titles:
            if title.lower() in text.lower():
                found_titles.append(title)
        return found_titles if found_titles else ["software engineer"]  # Default if none found

class LinkedInAutoApply:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.resume_path = None
        
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.headless = False
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        self.driver = uc.Chrome(options=options, version_main=131)
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self, email, password):
        try:
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)
            
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
            email_input.send_keys(email)
            
            password_input = self.driver.find_element(By.ID, 'password')
            password_input.send_keys(password)
            
            submit_button = self.driver.find_element(By.CSS_SELECTOR, '[type="submit"]')
            submit_button.click()
            
            time.sleep(3)
            return True
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            return False
            
    def search_jobs(self, keywords):
        try:
            search_url = f'https://www.linkedin.com/jobs/search/?keywords={"+".join(keywords)}&f_AL=true'  # Added Easy Apply filter
            self.driver.get(search_url)
            time.sleep(5)  # Increased wait time
            
            # Scroll to load more jobs
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            return True
        except Exception as e:
            logging.error(f"Job search failed: {str(e)}")
            return False
            
    def apply_to_job(self, job_card):
        try:
            # Click the job card
            title_element = job_card.find_element(By.CSS_SELECTOR, '.job-card-list__title')
            job_title = title_element.text
            logging.info(f"Applying to: {job_title}")
            
            title_element.click()
            time.sleep(2)
            
            # Click Easy Apply
            try:
                easy_apply_button = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.jobs-apply-button'))
                )
                easy_apply_button.click()
                time.sleep(2)
            except:
                logging.info("No Easy Apply button found")
                return False

            # Handle application steps
            while True:
                # Check for resume upload
                try:
                    resume_upload = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
                    if resume_upload and self.resume_path:
                        resume_upload.send_keys(self.resume_path)
                        logging.info("Uploaded resume")
                        time.sleep(2)
                except:
                    pass

                # Look for phone number field
                try:
                    phone_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="text"][id*="phoneNumber-nationalNumber"]')
                    if not phone_input.get_attribute('value'):
                        phone_input.send_keys('1234567890')  # Replace with actual phone
                        time.sleep(1)
                except:
                    pass

                # Try to find follow company checkbox and uncheck it
                try:
                    follow_checkbox = self.driver.find_element(By.CSS_SELECTOR, 'input[type="checkbox"][name="follow-company-checkbox"]')
                    if follow_checkbox.is_selected():
                        follow_checkbox.click()
                except:
                    pass

                # Check for next button
                try:
                    next_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Continue to next step"]'))
                    )
                    if not next_button.is_enabled():
                        logging.warning("Next button is disabled")
                        return False
                    next_button.click()
                    time.sleep(2)
                    continue
                except TimeoutException:
                    # Look for submit button if no next button
                    try:
                        submit_button = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Submit application"]'))
                        )
                        submit_button.click()
                        logging.info(f"Successfully applied to {job_title}")
                        time.sleep(2)
                        return True
                    except:
                        logging.warning("Could not find submit button")
                        return False

        except Exception as e:
            logging.error(f"Application failed: {str(e)}")
            return False
        
    def find_resume(self):
        downloads_path = str(Path(f'/Users/aarti/Downloads'))
        resume_files = [f for f in os.listdir(downloads_path) 
                       if f.lower().endswith(('.pdf', '.docx')) and 'resume' in f.lower()]
        
        if resume_files:
            self.resume_path = os.path.join(downloads_path, resume_files[0])
            logging.info(f"Found resume: {resume_files[0]}")
            return True
        return False

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LinkedIn Auto Apply")
        self.root.geometry("400x200")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (400/2)
        y = (screen_height/2) - (200/2)
        self.root.geometry(f'400x200+{int(x)}+{int(y)}')
        
        style = ttk.Style()
        style.configure('TLabel', padding=5)
        style.configure('TButton', padding=5)
        style.configure('TEntry', padding=5)
        
        login_frame = ttk.LabelFrame(self.root, text="LinkedIn Login", padding=10)
        login_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(login_frame, text="Email:").pack(fill="x")
        self.email = ttk.Entry(login_frame)
        self.email.pack(fill="x")
        
        ttk.Label(login_frame, text="Password:").pack(fill="x")
        self.password = ttk.Entry(login_frame, show="*")
        self.password.pack(fill="x")
        
        ttk.Button(self.root, text="Start Auto Apply", command=self.start_apply).pack(pady=20)
        
        self.credentials = None
        
    def start_apply(self):
        self.credentials = {
            'email': self.email.get(),
            'password': self.password.get()
        }
        self.root.quit()
        
    def get_credentials(self):
        self.root.mainloop()
        return self.credentials

async def main():
    login_window = LoginWindow()
    credentials = login_window.get_credentials()
    
    if not credentials:
        print("Login cancelled")
        return
        
    linkedin = LinkedInAutoApply()
    
    try:
        # Setup and find resume
        linkedin.setup_driver()
        if not linkedin.find_resume():
            messagebox.showerror("Error", "No resume file found in Downloads folder")
            return
            
        # Parse resume for job titles
        parser = ResumeParser(linkedin.resume_path)
        job_titles = parser.extract_job_titles()
        logging.info(f"Extracted job titles: {job_titles}")
        
        # Login
        if not linkedin.login(credentials['email'], credentials['password']):
            messagebox.showerror("Error", "Login failed")
            return
            
        # Search and apply
        applications = 0
        for title in job_titles:
            if not linkedin.search_jobs([title]):
                continue
                
            time.sleep(3)
            job_cards = linkedin.driver.find_elements(By.CSS_SELECTOR, '.jobs-search__results-list li')
            
            if not job_cards:
                continue
                
            for job_card in job_cards[:5]:
                try:
                    if linkedin.apply_to_job(job_card):
                        applications += 1
                        time.sleep(2)
                except Exception as e:
                    logging.error(f"Error applying to job: {str(e)}")
                    continue
        
        messagebox.showinfo("Complete", f"Applied to {applications} jobs")
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        if linkedin.driver:
            linkedin.driver.quit()

if __name__ == '__main__':
    asyncio.run(main())

modules = ['undetected-chromedriver', 'selenium', 'PyPDF2', 'python-docx', 'tkinter']