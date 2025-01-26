import sys
import json
import tkinter as tk
from tkinter import ttk, messagebox
import base64
import pyperclip
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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

class PasswordManagerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Password Manager")
        self.window.geometry("400x500")
        
        self.manager = PasswordManager()
        self.setup_login_screen()
        
    def setup_login_screen(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Enter Master Password:").grid(row=0, column=0, pady=5)
        self.master_password = ttk.Entry(frame, show="*")
        self.master_password.grid(row=1, column=0, pady=5)
        
        ttk.Button(frame, text="Login", command=self.login).grid(row=2, column=0, pady=20)
        
    def login(self):
        try:
            self.manager.initialize(self.master_password.get())
            self.manager.load_passwords()
            self.setup_main_screen()
        except:
            messagebox.showerror("Error", "Invalid password!")
            
    def setup_main_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()
            
        frame = ttk.Frame(self.window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.tree = ttk.Treeview(frame, columns=("Service", "Username"), show="headings")
        self.tree.heading("Service", text="Service")
        self.tree.heading("Username", text="Username")
        self.tree.grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Add New Password").grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Label(frame, text="Service:").grid(row=2, column=0)
        self.service_entry = ttk.Entry(frame)
        self.service_entry.grid(row=2, column=1)
        
        ttk.Label(frame, text="Username:").grid(row=3, column=0)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=3, column=1)
        
        ttk.Label(frame, text="Password:").grid(row=4, column=0)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=4, column=1)
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Add Password", command=self.add_password).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Copy Password", command=self.copy_password).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete Password", command=self.delete_password).grid(row=0, column=2, padx=5)
        
        self.update_password_list()
        
    def add_password(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if service and username and password:
            self.manager.add_password(service, username, password)
            self.update_password_list()
            self.service_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            
    def copy_password(self):
        selection = self.tree.selection()
        if selection:
            service = self.tree.item(selection[0])["values"][0]
            password_info = self.manager.get_password(service)
            if password_info:
                pyperclip.copy(password_info["password"])
                messagebox.showinfo("Success", "Password copied to clipboard!")
                
    def delete_password(self):
        selection = self.tree.selection()
        if selection:
            service = self.tree.item(selection[0])["values"][0]
            del self.manager.passwords[service]
            self.manager._save_passwords()
            self.update_password_list()
            
    def update_password_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for service in self.manager.list_services():
            password_info = self.manager.get_password(service)
            self.tree.insert("", tk.END, values=(service, password_info["username"]))
            
    def run(self):
        self.window.mainloop()

async def func(args):
    """Run the password manager GUI application"""
    app = PasswordManagerGUI()
    app.run()
    return json.dumps({"message": "Password manager closed"})

object = {
    "name": "password_manager",
    "description": "Launch an encrypted password manager GUI application",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1])
                import asyncio
                result = asyncio.run(func(args))
                print(result)
            except Exception as e:
                print(json.dumps({"error": str(e)}))
