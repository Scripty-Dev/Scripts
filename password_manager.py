import customtkinter as ctk
import json
import base64
import pyperclip
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class PasswordManager:
    def __init__(self, file_path='passwords.enc'):
        self.file_path = file_path
        self.passwords = {}
        self.key = None
        self.fernet = None
        
    def _derive_key(self, master_password, salt=None):
        if salt is None:
            salt = b'defaultsalt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        return key
    
    def initialize(self, master_password):
        self.key = self._derive_key(master_password)
        self.fernet = Fernet(self.key)
    
    def add_password(self, service, username, password):
        if not self.fernet:
            raise ValueError("Please initialize with master password first")
        self.passwords[service] = {
            'username': username,
            'password': password
        }
        self._save_passwords()
        
    def get_password(self, service):
        if not self.fernet:
            raise ValueError("Please initialize with master password first")
        return self.passwords.get(service)
    
    def list_services(self):
        return list(self.passwords.keys())
    
    def _save_passwords(self):
        if not self.fernet:
            raise ValueError("Please initialize with master password first")
        encrypted_data = self.fernet.encrypt(json.dumps(self.passwords).encode())
        with open(self.file_path, 'wb') as f:
            f.write(encrypted_data)
    
    def load_passwords(self):
        if not self.fernet:
            raise ValueError("Please initialize with master password first")
        try:
            with open(self.file_path, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.passwords = json.loads(decrypted_data.decode())
        except FileNotFoundError:
            self.passwords = {}
        except Exception as e:
            raise ValueError("Invalid master password or corrupted file") from e

class ModernPasswordManagerGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Password Vault")
        self.window.geometry("800x600")
        self.window.configure(fg_color="#1a1a1a")
        
        self.manager = PasswordManager()
        self.setup_login_screen()
        
    def setup_login_screen(self):
        # Create a frame for login
        frame = ctk.CTkFrame(self.window, fg_color="#2d2d2d")
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(frame, text="Password Vault", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=30)
        
        # Subtitle
        subtitle = ctk.CTkLabel(frame, text="Enter Master Password", 
                              font=ctk.CTkFont(size=16))
        subtitle.pack(pady=10)
        
        # Password entry
        self.master_password = ctk.CTkEntry(frame, show="•", width=300,
                                          placeholder_text="Master Password")
        self.master_password.pack(pady=20)
        
        # Login button
        login_btn = ctk.CTkButton(frame, text="Login", 
                                 command=self.login,
                                 fg_color="#9b59b6",
                                 hover_color="#8e44ad",
                                 width=200)
        login_btn.pack(pady=20)
        
    def setup_main_screen(self):
        self.window.configure(fg_color="#1a1a1a")
        for widget in self.window.winfo_children():
            widget.destroy()
            
        # Create main container
        container = ctk.CTkFrame(self.window, fg_color="#2d2d2d")
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(container, text="Password Manager", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Create scrollable frame for password list
        scroll_frame = ctk.CTkScrollableFrame(container, fg_color="#363636")
        scroll_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.password_frames = {}
        for service in self.manager.list_services():
            self.create_password_entry(scroll_frame, service)
            
        # Add new password section
        add_frame = ctk.CTkFrame(container, fg_color="#2d2d2d")
        add_frame.pack(pady=20, padx=20, fill="x")
        
        # Entry fields
        self.service_entry = ctk.CTkEntry(add_frame, placeholder_text="Service",
                                        width=200)
        self.service_entry.pack(side="left", padx=5)
        
        self.username_entry = ctk.CTkEntry(add_frame, placeholder_text="Username",
                                         width=200)
        self.username_entry.pack(side="left", padx=5)
        
        self.password_entry = ctk.CTkEntry(add_frame, placeholder_text="Password",
                                         show="•", width=200)
        self.password_entry.pack(side="left", padx=5)
        
        # Add button
        add_btn = ctk.CTkButton(add_frame, text="Add Password",
                               command=self.add_password,
                               fg_color="#9b59b6",
                               hover_color="#8e44ad")
        add_btn.pack(side="left", padx=5)
        
    def create_password_entry(self, parent, service):
        frame = ctk.CTkFrame(parent, fg_color="#404040")
        frame.pack(pady=5, padx=10, fill="x")
        
        password_info = self.manager.get_password(service)
        
        service_label = ctk.CTkLabel(frame, text=service,
                                   font=ctk.CTkFont(weight="bold"))
        service_label.pack(side="left", padx=10)
        
        username_label = ctk.CTkLabel(frame, text=password_info["username"])
        username_label.pack(side="left", padx=10)
        
        copy_btn = ctk.CTkButton(frame, text="Copy Password",
                                command=lambda s=service: self.copy_password(s),
                                fg_color="#9b59b6",
                                hover_color="#8e44ad",
                                width=100)
        copy_btn.pack(side="right", padx=10)
        
        delete_btn = ctk.CTkButton(frame, text="Delete",
                                  command=lambda s=service: self.delete_password(s),
                                  fg_color="#e74c3c",
                                  hover_color="#c0392b",
                                  width=80)
        delete_btn.pack(side="right", padx=10)
        
        self.password_frames[service] = frame
            
    def login(self):
        try:
            self.manager.initialize(self.master_password.get())
            self.manager.load_passwords()
            self.setup_main_screen()
        except:
            self.show_error("Invalid password!")
            
    def add_password(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if service and username and password:
            self.manager.add_password(service, username, password)
            self.service_entry.delete(0, 'end')
            self.username_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
            self.setup_main_screen()
            
    def copy_password(self, service):
        password_info = self.manager.get_password(service)
        if password_info:
            pyperclip.copy(password_info["password"])
            self.show_success("Password copied to clipboard!")
            
    def delete_password(self, service):
        del self.manager.passwords[service]
        self.manager._save_passwords()
        self.password_frames[service].destroy()
        del self.password_frames[service]
            
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
        
    def run(self):
        self.window.mainloop()

if __name__ == '__main__':
    app = ModernPasswordManagerGUI()
    app.run()