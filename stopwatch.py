import sys
import json
import asyncio
import customtkinter as ctk
import time
import os
import subprocess
from pathlib import Path

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ModernStopwatch:
    """A modern stopwatch with CustomTkinter interface"""
    def __init__(self):
        # Create and configure the main window
        self.window = ctk.CTk()
        self.window.title("Stopwatch")
        
        # Center the window on screen
        window_width = 450
        window_height = 400
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.window.configure(fg_color="#1a1a1a")
        
        # Initialize state variables
        self.time = 0
        self.running = False
        self.laps = []
        
        self.setup_gui()
    
    def setup_gui(self):
        """Set up all GUI elements"""
        # Main container
        container = ctk.CTkFrame(self.window, fg_color="#2d2d2d")
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Time display frame
        time_frame = ctk.CTkFrame(container, fg_color="#363636")
        time_frame.pack(pady=20, padx=20, fill="x")
        
        # Time display label
        self.time_label = ctk.CTkLabel(
            time_frame,
            text="00:00:00.00",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold")
        )
        self.time_label.pack(pady=20)
        
        # Control buttons frame
        button_frame = ctk.CTkFrame(container, fg_color="#363636")
        button_frame.pack(pady=10, padx=20, fill="x")
        
        # Start button
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start",
            command=self.start_pause,
            font=ctk.CTkFont(size=14),
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            width=120,
            height=40
        )
        self.start_button.pack(side="left", padx=10, pady=10, expand=True)
        
        # Lap button
        self.lap_button = ctk.CTkButton(
            button_frame,
            text="Lap",
            command=self.lap,
            font=ctk.CTkFont(size=14),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=120,
            height=40,
            state="disabled"
        )
        self.lap_button.pack(side="left", padx=10, pady=10, expand=True)
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self.reset,
            font=ctk.CTkFont(size=14),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=120,
            height=40,
            state="disabled"
        )
        self.reset_button.pack(side="left", padx=10, pady=10, expand=True)
        
        # Lap times frame with scrollable area
        self.setup_lap_display(container)

    def setup_lap_display(self, parent):
        """Set up the scrollable lap times display"""
        # Title for lap times
        lap_title = ctk.CTkLabel(
            parent,
            text="Lap Times",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lap_title.pack(pady=(20, 10))
        
        # Scrollable frame for lap times
        self.lap_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="#363636",
            height=150
        )
        self.lap_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    def start_pause(self):
        """Toggle between start and pause states"""
        if not self.running:
            self.running = True
            self.start_button.configure(
                text="Pause",
                fg_color="#f1c40f",
                hover_color="#f39c12"
            )
            self.lap_button.configure(state="normal")
            self.reset_button.configure(state="normal")
            self.update()
        else:
            self.running = False
            self.start_button.configure(
                text="Start",
                fg_color="#9b59b6",
                hover_color="#8e44ad"
            )
    
    def update(self):
        """Update the time display"""
        if self.running:
            self.time += 0.01
            self.update_display()
            self.window.after(10, self.update)
    
    def update_display(self):
        """Update the time display label"""
        hours = int(self.time // 3600)
        minutes = int((self.time % 3600) // 60)
        seconds = int(self.time % 60)
        centiseconds = int((self.time * 100) % 100)
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        self.time_label.configure(text=time_str)
    
    def lap(self):
        """Record lap time"""
        current_time = self.time_label.cget("text")
        lap_label = ctk.CTkLabel(
            self.lap_frame,
            text=f"Lap {len(self.laps) + 1}: {current_time}",
            font=ctk.CTkFont(size=14),
            fg_color="#404040",
            corner_radius=6
        )
        lap_label.pack(pady=5, padx=10, fill="x")
        self.laps.append(current_time)
    
    def reset(self):
        """Reset the stopwatch"""
        self.running = False
        self.time = 0
        self.time_label.configure(text="00:00:00.00")
        self.start_button.configure(
            text="Start",
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        self.lap_button.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        
        # Clear lap times
        self.laps.clear()
        for widget in self.lap_frame.winfo_children():
            widget.destroy()
    
    def close(self):
        """Close the stopwatch window"""
        self.window.quit()
        self.window.destroy()

    def run(self):
        """Start the application"""
        self.window.mainloop()

async def func(args):
    """Handle stopwatch commands - only open and close"""
    try:
        command = args.get('command', '').lower()
        
        if command == 'open':
            # Create and run a separate stopwatch process
            stopwatch_script = Path("stopwatch_background.py")  # Simplified path
            with open(stopwatch_script, 'w') as f:
                f.write('''
import customtkinter as ctk

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ModernStopwatch:
    """A modern stopwatch with CustomTkinter interface"""
''')
                # Write the entire ModernStopwatch class as a string
                f.write('''    def __init__(self):
        # Create and configure the main window
        self.window = ctk.CTk()
        self.window.title("Stopwatch")
        
        # Center the window on screen
        window_width = 450
        window_height = 400
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.window.configure(fg_color="#1a1a1a")
        
        # Initialize state variables
        self.time = 0
        self.running = False
        self.laps = []
        
        self.setup_gui()
    
    def setup_gui(self):
        """Set up all GUI elements"""
        # Main container
        container = ctk.CTkFrame(self.window, fg_color="#2d2d2d")
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Time display frame
        time_frame = ctk.CTkFrame(container, fg_color="#363636")
        time_frame.pack(pady=20, padx=20, fill="x")
        
        # Time display label
        self.time_label = ctk.CTkLabel(
            time_frame,
            text="00:00:00.00",
            font=ctk.CTkFont(family="Arial", size=48, weight="bold")
        )
        self.time_label.pack(pady=20)
        
        # Control buttons frame
        button_frame = ctk.CTkFrame(container, fg_color="#363636")
        button_frame.pack(pady=10, padx=20, fill="x")
        
        # Start button
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start",
            command=self.start_pause,
            font=ctk.CTkFont(size=14),
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            width=120,
            height=40
        )
        self.start_button.pack(side="left", padx=10, pady=10, expand=True)
        
        # Lap button
        self.lap_button = ctk.CTkButton(
            button_frame,
            text="Lap",
            command=self.lap,
            font=ctk.CTkFont(size=14),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=120,
            height=40,
            state="disabled"
        )
        self.lap_button.pack(side="left", padx=10, pady=10, expand=True)
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self.reset,
            font=ctk.CTkFont(size=14),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=120,
            height=40,
            state="disabled"
        )
        self.reset_button.pack(side="left", padx=10, pady=10, expand=True)
        
        # Lap times frame with scrollable area
        self.setup_lap_display(container)

    def setup_lap_display(self, parent):
        """Set up the scrollable lap times display"""
        # Title for lap times
        lap_title = ctk.CTkLabel(
            parent,
            text="Lap Times",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lap_title.pack(pady=(20, 10))
        
        # Scrollable frame for lap times
        self.lap_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="#363636",
            height=150
        )
        self.lap_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    def start_pause(self):
        """Toggle between start and pause states"""
        if not self.running:
            self.running = True
            self.start_button.configure(
                text="Pause",
                fg_color="#f1c40f",
                hover_color="#f39c12"
            )
            self.lap_button.configure(state="normal")
            self.reset_button.configure(state="normal")
            self.update()
        else:
            self.running = False
            self.start_button.configure(
                text="Start",
                fg_color="#9b59b6",
                hover_color="#8e44ad"
            )
    
    def update(self):
        """Update the time display"""
        if self.running:
            self.time += 0.01
            self.update_display()
            self.window.after(10, self.update)
    
    def update_display(self):
        """Update the time display label"""
        hours = int(self.time // 3600)
        minutes = int((self.time % 3600) // 60)
        seconds = int(self.time % 60)
        centiseconds = int((self.time * 100) % 100)
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        self.time_label.configure(text=time_str)
    
    def lap(self):
        """Record lap time"""
        current_time = self.time_label.cget("text")
        lap_label = ctk.CTkLabel(
            self.lap_frame,
            text=f"Lap {len(self.laps) + 1}: {current_time}",
            font=ctk.CTkFont(size=14),
            fg_color="#404040",
            corner_radius=6
        )
        lap_label.pack(pady=5, padx=10, fill="x")
        self.laps.append(current_time)
    
    def reset(self):
        """Reset the stopwatch"""
        self.running = False
        self.time = 0
        self.time_label.configure(text="00:00:00.00")
        self.start_button.configure(
            text="Start",
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        self.lap_button.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        
        # Clear lap times
        self.laps.clear()
        for widget in self.lap_frame.winfo_children():
            widget.destroy()
    
    def run(self):
        """Start the application"""
        self.window.mainloop()
''')
                
                f.write('''
stopwatch = ModernStopwatch()
stopwatch.run()
''')

            subprocess.Popen([sys.executable, str(stopwatch_script)],
                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return json.dumps({"message": "Stopwatch opened"})
            
        elif command == 'close':
            # This will close any existing stopwatch windows
            if ctk._CTk__cls_windows:
                for window in ctk._CTk__cls_windows:
                    window.destroy()
            return json.dumps({"message": "Stopwatch closed"})
            
        else:
            return json.dumps({
                "error": "Invalid command. Use 'open' or 'close'"
            })
            
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

object = {
    "name": "stopwatch",
    "description": "Open or close a modern stopwatch window. Examples: 'Open stopwatch', 'Close timer', 'Launch stopwatch'",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": ["open", "close"],
                "description": "Open or close the stopwatch"
            }
        },
        "required": ["command"]
    }
}