import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
import json
import os
import threading
from llama_cpp import Llama
import requests
import base64
import time
import re
import traceback  # Added for detailed error tracking
import sys  # Added for error handling


class EmailDrafter:
    def __init__(self, root):
        self.root = root
        self.root.title("Email Draft Creator")
        self.model = None
        self.model_path = "openhermes-2.5-mistral-7b.gguf"
        self.setup_ui()
        self.load_saved_credentials()
        self.mail = None
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Credentials section
        ttk.Label(main_frame, text="Gmail Credentials", font=('Helvetica', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(main_frame, text="Gmail Address:").grid(row=1, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).grid(row=1, column=1, padx=5)

        ttk.Label(main_frame, text="App Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=40).grid(row=2, column=1, padx=5)

        # Date section
        ttk.Label(main_frame, text="Process Emails From:", font=('Helvetica', 12, 'bold')).grid(row=3, column=0, columnspan=2, pady=10)

        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=4, column=0, columnspan=2, pady=5)
        ttk.Button(date_frame, text="Today", command=lambda: self.set_date(0)).grid(row=0, column=0, padx=5)
        ttk.Button(date_frame, text="Yesterday", command=lambda: self.set_date(1)).grid(row=0, column=1, padx=5)
        ttk.Button(date_frame, text="Last 3 Days", command=lambda: self.set_date(3)).grid(row=0, column=2, padx=5)

        ttk.Label(main_frame, text="Or enter specific date (YYYY-MM-DD):").grid(row=5, column=0, columnspan=2, pady=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(main_frame, textvariable=self.date_var, width=40).grid(row=6, column=0, columnspan=2, pady=2)

        # Save credentials checkbox
        self.save_creds_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="Save credentials for next time", 
                       variable=self.save_creds_var).grid(row=7, column=0, columnspan=2, pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress.grid(row=8, column=0, columnspan=2, sticky="ew", pady=5)

        # Process button
        self.process_button = ttk.Button(main_frame, text="Process Emails", command=self.start_processing)
        self.process_button.grid(row=9, column=0, columnspan=2, pady=10)

        # Status display
        self.status_var = tk.StringVar(value="Ready to process emails...")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, wraplength=350)
        self.status_label.grid(row=10, column=0, columnspan=2, pady=5)

        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def get_email_address(self, header_value):
        """Extract clean email address from header"""
        try:
            matches = re.findall(r'<(.+?)>', header_value)
            if matches:
                return matches[0]
            return header_value.strip()
        except Exception as e:
            print(f"Error extracting email address from {header_value}: {e}")
            return header_value

    def is_automated_sender(self, email_address):
        """Check if sender is automated"""
        try:
            automated_patterns = [
                r'noreply@',
                r'no-reply@',
                r'donotreply@',
                r'notifications?@',
                r'updates?@',
                r'info@',
                r'system@',
                r'alert@'
            ]
            clean_email = self.get_email_address(email_address)
            return any(re.search(pattern, clean_email.lower()) for pattern in automated_patterns)
        except Exception as e:
            print(f"Error checking automated sender: {e}")
            return False
    

    def connect_to_gmail(self):
        """Establish IMAP connection"""
        try:
            if self.mail is None:
                print("Connecting to Gmail...")
                self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
                self.mail.login(self.email_var.get(), self.password_var.get())
                print("Successfully connected to Gmail")
            return self.mail
        except Exception as e:
            print(f"Error connecting to Gmail: {e}")
            raise

    def create_draft(self, original_message, reply_content):
        """Create a draft reply using IMAP"""
        try:
            print("\nCreating draft:")
            print(f"Subject: Re: {original_message['subject']}")
            print(f"To: {original_message['from']}")
            print(f"Reply length: {len(reply_content)}")
            
            # Format draft message
            draft = MIMEText(reply_content)
            draft['Subject'] = f"Re: {original_message['subject']}"
            draft['To'] = original_message['from']
            draft['From'] = self.email_var.get()
            
            # Only add these if they exist
            if 'message-id' in original_message:
                draft['In-Reply-To'] = original_message['message-id']
                draft['References'] = original_message.get('references', '') + ' ' + original_message['message-id']
            
            # Print draft details for debugging
            print("\nDraft details:")
            for key in draft.keys():
                print(f"{key}: {draft[key]}")
            
            # Append to Drafts folder
            result = self.mail.append('[Gmail]/Drafts', '', 
                              imaplib.Time2Internaldate(time.time()), 
                              draft.as_string().encode())
            print(f"IMAP append result: {result}")
            return True
            
        except Exception as e:
            print("\nError details for draft creation:")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            print("Stack trace:")
            traceback.print_exc()
            return False

    def set_date(self, days_ago):
        """Set the date field to X days ago"""
        date = datetime.now() - timedelta(days=days_ago)
        self.date_var.set(date.strftime('%Y-%m-%d'))

    def load_saved_credentials(self):
        """Load saved credentials if they exist"""
        if os.path.exists('credentials.json'):
            try:
                with open('credentials.json', 'r') as f:
                    creds = json.load(f)
                    self.email_var.set(creds.get('email', ''))
                    self.password_var.set(creds.get('password', ''))
            except Exception as e:
                print(f"Error loading credentials: {e}")

    def save_credentials(self):
        """Save credentials if checkbox is checked"""
        if self.save_creds_var.get():
            try:
                with open('credentials.json', 'w') as f:
                    json.dump({
                        'email': self.email_var.get(),
                        'password': self.password_var.get()
                    }, f)
            except Exception as e:
                print(f"Error saving credentials: {e}")

    def start_processing(self):
        """Start processing in a separate thread"""
        self.process_button.config(state='disabled')
        thread = threading.Thread(target=self.process_emails)
        thread.daemon = True
        thread.start()

    def download_model(self):
        """Download the model if it doesn't exist"""
        if not os.path.exists(self.model_path):
            self.status_var.set("Downloading model... This may take a while...")
            self.root.update()
            
            url = "https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/openhermes-2.5-mistral-7b.Q4_K_M.gguf"
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(self.model_path, 'wb') as f:
                downloaded = 0
                for data in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                    downloaded += len(data)
                    f.write(data)
                    progress = (downloaded / total_size) * 100
                    self.progress_var.set(progress)
                    self.status_var.set(f"Downloading model: {progress:.1f}%")
                    self.root.update()

    def load_model(self):
        """Load the OpenHermes model"""
        if self.model is None:
            self.status_var.set("Loading model...")
            self.root.update()
            
            try:
                if not os.path.exists(self.model_path):
                    self.download_model()
                
                self.model = Llama(
                    model_path=self.model_path,
                    n_ctx=32768,
                    n_gpu_layers=-1,  # Use all layers on GPU
                    n_threads=4,
                    verbose=True
                )

                self.status_var.set("Model loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")
                raise

    def classify_email(self, subject, body, from_header):
        """Classify if email needs a reply using OpenHermes"""
        # Quick check for automated senders
        if self.is_automated_sender(from_header):
            return False
            
        prompt = f"""<|im_start|>system
You are an email assistant that determines if emails need replies.
<|im_end|>
<|im_start|>user
Analyze this email and determine if it needs a reply. Respond with ONLY "NEEDS_REPLY" or "NO_REPLY".

Rules:
1. NEEDS_REPLY for:
   - Personal emails requiring response
   - Business communications needing action
   - Direct questions or requests
   - Emails from real people expecting replies
2. NO_REPLY for:
   - Marketing newsletters
   - Automated notifications
   - FYI/broadcast messages
   - System alerts

From: {from_header}
Subject: {subject}
Body: {body}
<|im_end|>
<|im_start|>assistant"""

        response = self.model(prompt, max_tokens=50, stop=["<|im_end|>"])
        return "NEEDS_REPLY" in response['choices'][0]['text'].upper()

    def generate_draft(self, subject, body, from_header, to_addr):
        """Generate draft reply using OpenHermes"""
        try:
            prompt = f"""<|im_start|>system
    You are an email assistant helping {to_addr} write replies.
    <|im_end|>
    <|im_start|>user
    Write a reply to this email. The reply should be from {to_addr} responding to {from_header}.
    Note: Use the sender's name when appropriate in the response.

    Original Email:
    From: {from_header}
    To: {to_addr}
    Subject: {subject}
    Body: {str(body)}  # Force string conversion

    Guidelines:
    1. Write from {to_addr}'s perspective responding to the sender
    2. Use the sender's name when appropriate to make the response personal
    3. Match the tone of the original email
    4. Address all questions or points requiring response
    5. Be concise but thorough
    6. Make it sound natural and human-written
    <|im_end|>
    <|im_start|>assistant"""

            response = self.model(prompt, max_tokens=500, stop=["<|im_end|>"])
            result = response['choices'][0]['text'].strip()
            if not result:
                return "Thank you for your email. I will respond to your message shortly."
            return result
        except Exception as e:
            print(f"Error generating draft: {e}")
            return "Thank you for your email. I will respond to your message shortly."
        
    def process_emails(self):
        """Main function to process emails"""
        try:
            print("\nStarting email processing...")

            # Basic validation
            email_addr = self.email_var.get().strip()
            password = self.password_var.get().strip()
            date_str = self.date_var.get().strip()

            if not all([email_addr, password, date_str]):
                messagebox.showerror("Error", "Please fill in all fields")
                return

            # Load model
            if self.model is None:
                self.load_model()

            # Save credentials if requested
            self.save_credentials()

            # Connect to Gmail
            self.status_var.set("Connecting to Gmail...")
            self.root.update()

            self.mail = self.connect_to_gmail()
            self.mail.select("inbox")

            # Search for emails
            search_date = datetime.strptime(date_str, '%Y-%m-%d')
            search_criterion = search_date.strftime('%d-%b-%Y')
            result, messages = self.mail.search(None, f'(SINCE "{search_criterion}" UNSEEN)')

            if result != 'OK':
                raise Exception(f"Failed to search emails: {result}")

            email_ids = messages[0].split()
            total_emails = len(email_ids)
            needs_reply = 0
            drafts_created = 0

            print(f"\nFound {total_emails} unread emails since {date_str}")
            self.status_var.set(f"Found {total_emails} emails to process...")
            self.root.update()

            # Process emails
            for i, email_id in enumerate(email_ids, 1):
                print(f"\nProcessing email {i} of {total_emails}")
                self.progress_var.set((i / total_emails) * 100)

                try:
                    if isinstance(email_id, bytes):
                        email_id = email_id.decode('utf-8')

                    # Fetch email with error handling
                    result, msg_data = self.mail.fetch(email_id, "(RFC822)")
                    if result != 'OK' or not msg_data:
                        print(f"Failed to fetch email {email_id}")
                        continue

                    # Extract email data
                    first_part = next((part for part in msg_data if isinstance(part, tuple)), None)
                    if not first_part:
                        print(f"Unexpected format in msg_data for email {email_id}: {msg_data}")
                        continue

                    email_body = first_part[1]
                    if not isinstance(email_body, bytes):
                        print(f"Converting email body from {type(email_body)} to bytes")
                        email_body = str(email_body).encode('utf-8')

                    message = email.message_from_bytes(email_body)

                    # Extract email details
                    subject = self.extract_subject(message)
                    from_header = message.get("from", "")
                    body = self.extract_email_body(message)

                    print(f"\nEmail details:")
                    print(f"From: {from_header}")
                    print(f"Subject: {subject}")
                    print(f"Body length: {len(body)}")

                    self.status_var.set(f"Processing {i}/{total_emails}\nCurrent: {subject}")
                    self.root.update()

                    # Classify and generate draft if needed
                    if self.classify_email(subject, body, from_header):
                        print("Email classified as needing reply")
                        needs_reply += 1
                        draft_content = self.generate_draft(subject, body, from_header, email_addr)
                        print(f"Generated draft content length: {len(draft_content)}")

                        if self.create_draft(message, draft_content):
                            print("Draft created successfully")
                            drafts_created += 1
                        else:
                            print("Failed to create draft")

                except Exception as e:
                    print(f"Error processing email ID {email_id}: {str(e)}")
                    traceback.print_exc()
                    continue

            # Final status
            final_status = f"""Processing Complete!
    Total emails: {total_emails}
    Needs reply: {needs_reply}
    Drafts created: {drafts_created}"""
            print(f"\n{final_status}")
            self.status_var.set(final_status)
            self.mail.logout()
            self.mail = None

        except Exception as e:
            print("\nGlobal error occurred:")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred while processing emails.")
        finally:
            self.process_button.config(state='normal')
            self.progress_var.set(0)
    # Helper methods

    def extract_subject(self, message):
        """Extract the subject from an email message"""
        try:
            subject = message.get("subject", "(No Subject)")
            if subject:
                subject_header = decode_header(subject)[0]
                subject_text, charset = subject_header
                if isinstance(subject_text, bytes):
                    subject = subject_text.decode(charset or 'utf-8', errors='ignore')
                else:
                    subject = str(subject_text)
            return subject
        except Exception as e:
            print(f"Error extracting subject: {e}")
            return "(No Subject)"


    def extract_email_body(self, message):
        """Extract the body from an email message"""
        body = ""
        try:
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode('utf-8', errors='ignore')
                            break
            else:
                payload = message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error extracting email body: {e}")
        return body

def main():
    root = tk.Tk()
    app = EmailDrafter(root)
    root.mainloop()

if __name__ == "__main__":
    main()