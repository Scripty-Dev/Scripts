import customtkinter as ctk
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

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

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

class ModernLinkedInGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("LinkedIn Auto Apply")
        self.window.geometry("800x600")
        self.window.configure(fg_color="#1a1a1a")
        
        self.linkedin = LinkedInAutoApply()
        self.setup_login_screen()
        
    def setup_login_screen(self):
        # Create main container
        container = ctk.CTkFrame(self.window, fg_color="#2d2d2d")
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(container, text="LinkedIn Auto Apply", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Subtitle
        subtitle = ctk.CTkLabel(container, text="Login to LinkedIn", 
                              font=ctk.CTkFont(size=16))
        subtitle.pack(pady=10)
        
        # Login frame
        login_frame = ctk.CTkFrame(container, fg_color="#363636")
        login_frame.pack(pady=20, padx=20, fill="x")
        
        # Email entry
        self.email = ctk.CTkEntry(login_frame, placeholder_text="Email",
                                width=300)
        self.email.pack(pady=10)
        
        # Password entry
        self.password = ctk.CTkEntry(login_frame, show="•", width=300,
                                   placeholder_text="Password")
        self.password.pack(pady=10)
        
        # Start button
        start_btn = ctk.CTkButton(login_frame, text="Start Auto Apply",
                                command=self.start_apply,
                                fg_color="#9b59b6",
                                hover_color="#8e44ad",
                                width=200)
        start_btn.pack(pady=20)
        
        # Status frame
        self.status_frame = ctk.CTkFrame(container, fg_color="#363636")
        self.status_frame.pack(pady=20, padx=20, fill="x", expand=True)
        
        self.status_label = ctk.CTkLabel(self.status_frame, 
                                       text="Ready to start...",
                                       font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self.status_frame)
        self.progress.pack(pady=10, padx=20, fill="x")
        self.progress.set(0)
        
    def update_status(self, message, progress=None):
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress.set(progress)
        self.window.update()
        
    def show_error(self, message):
        error_window = ctk.CTkToplevel(self.window)
        error_window.title("Error")
        error_window.geometry("300x150")
        
        label = ctk.CTkLabel(error_window, text=message,
                           font=ctk.CTkFont(size=16))
        label.pack(pady=20)
        
        btn = ctk.CTkButton(error_window, text="OK",
                           command=error_window.destroy,
                           fg_color="#e74c3c",
                           hover_color="#c0392b")
        btn.pack(pady=20)
        
    def show_success(self, message):
        success_window = ctk.CTkToplevel(self.window)
        success_window.title("Success")
        success_window.geometry("300x150")
        
        label = ctk.CTkLabel(success_window, text=message,
                           font=ctk.CTkFont(size=16))
        label.pack(pady=20)
        
        btn = ctk.CTkButton(success_window, text="OK",
                           command=success_window.destroy,
                           fg_color="#2ecc71",
                           hover_color="#27ae60")
        btn.pack(pady=20)
        
    async def start_apply(self):
        credentials = {
            'email': self.email.get(),
            'password': self.password.get()
        }
        
        if not credentials['email'] or not credentials['password']:
            self.show_error("Please enter both email and password")
            return
            
        try:
            self.update_status("Setting up browser...", 0.1)
            self.linkedin.setup_driver()
            
            self.update_status("Finding resume...", 0.2)
            if not self.linkedin.find_resume():
                self.show_error("No resume file found in Downloads folder")
                return
                
            self.update_status("Parsing resume...", 0.3)
            parser = ResumeParser(self.linkedin.resume_path)
            job_titles = parser.extract_job_titles()
            logging.info(f"Extracted job titles: {job_titles}")
            
            self.update_status("Logging in to LinkedIn...", 0.4)
            if not self.linkedin.login(credentials['email'], credentials['password']):
                self.show_error("LinkedIn login failed")
                return
                
            applications = 0
            total_jobs = len(job_titles) * 5  # 5 applications per title
            current_job = 0
            
            for title in job_titles:
                self.update_status(f"Searching for {title} positions...", 
                                 0.5 + (current_job/total_jobs)*0.5)
                
                if not self.linkedin.search_jobs([title]):
                    continue
                    
                time.sleep(3)
                job_cards = self.linkedin.driver.find_elements(
                    By.CSS_SELECTOR, '.jobs-search__results-list li'
                )
                
                if not job_cards:
                    continue
                    
                for job_card in job_cards[:5]:
                    try:
                        current_job += 1
                        self.update_status(
                            f"Applying to job {current_job}/{total_jobs}...",
                            0.5 + (current_job/total_jobs)*0.5
                        )
                        
                        if self.linkedin.apply_to_job(job_card):
                            applications += 1
                            time.sleep(2)
                    except Exception as e:
                        logging.error(f"Error applying to job: {str(e)}")
                        continue
            
            self.show_success(f"Successfully applied to {applications} jobs!")
            self.update_status("Complete!", 1.0)
            
        except Exception as e:
            self.show_error(f"An error occurred: {str(e)}")
        finally:
            if self.linkedin.driver:
                self.linkedin.driver.quit()
    
    def run(self):
        self.window.mainloop()

async def main():
    app = ModernLinkedInGUI()
    app.run()

if __name__ == '__main__':
    asyncio.run(main())

modules = ['customtkinter', 'undetected-chromedriver', 'selenium', 'PyPDF2', 'python-docx']