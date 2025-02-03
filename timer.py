import sys
import json
import asyncio
import customtkinter as ctk
import time
import re
from plyer import notification
from dateutil import parser
from datetime import datetime, timedelta

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ModernTimer:
    """
    A modern countdown timer with GUI interface.
    Features:
    - Visual countdown with circular progress indicator
    - Natural language time input parsing
    - Modern dark theme interface
    - System notifications when timer completes
    """
    def __init__(self, initial_time=0):
        # Initialize the main window
        self.window = ctk.CTk()
        self.window.title("Timer")
        
        # Center the window on screen
        window_width = 500
        window_height = 600
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.window.configure(fg_color="#1a1a1a")
        
        # Initialize state variables
        self.time_left = initial_time
        self.running = False
        self.original_time = initial_time
        
        self.setup_gui()
        
        # If initial time was provided, start the timer automatically
        if initial_time > 0:
            self.update_display()
            self.reset_button.configure(state="normal")
            self.start_pause()

    def setup_gui(self):
        """Set up all GUI elements with a modern design"""
        # Main container
        container = ctk.CTkFrame(self.window, fg_color="#2d2d2d")
        container.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Time input section at the top
        self.setup_time_input(container)
        
        # Timer display frame
        timer_frame = ctk.CTkFrame(container, fg_color="#363636")
        timer_frame.pack(pady=20, padx=20, fill="x")
        
        # Create canvas for the timer ring
        self.canvas = ctk.CTkCanvas(
            timer_frame,
            width=300,
            height=300,
            bg='#363636',
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # Draw the background ring
        self.canvas.create_oval(
            25, 25, 275, 275,
            width=8,
            outline='#404040'
        )
        
        # Draw the progress ring (accent color)
        self.progress_ring = self.canvas.create_arc(
            25, 25, 275, 275,
            start=90,
            extent=360,
            width=8,
            outline='#9b59b6',
            style="arc"
        )
        
        # Time display in the center of the ring
        self.time_label = ctk.CTkLabel(
            timer_frame,
            text="00:00:00",
            font=ctk.CTkFont(family="Arial", size=36, weight="bold"),
            text_color="#ffffff"
        )
        self.time_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Control buttons below the timer
        self.setup_control_buttons(container)

    def setup_time_input(self, parent):
        """Create a modern time input section"""
        input_frame = ctk.CTkFrame(parent, fg_color="#363636")
        input_frame.pack(pady=20, padx=20, fill="x")
        
        # Create three input fields with labels
        self.hours_var = ctk.StringVar(value="0")
        self.minutes_var = ctk.StringVar(value="0")
        self.seconds_var = ctk.StringVar(value="0")
        
        time_inputs = [
            ("Hours", self.hours_var),
            ("Minutes", self.minutes_var),
            ("Seconds", self.seconds_var)
        ]
        
        fields_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        fields_frame.pack(pady=20, expand=True)
        
        for col, (label, var) in enumerate(time_inputs):
            container = ctk.CTkFrame(fields_frame, fg_color="transparent")
            container.grid(row=0, column=col, padx=15)
            
            entry = ctk.CTkEntry(
                container,
                width=70,
                height=40,
                textvariable=var,
                font=ctk.CTkFont(size=16),
                placeholder_text="00"
            )
            entry.grid(row=0, column=0, padx=5)
            
            ctk.CTkLabel(
                container,
                text=label,
                font=ctk.CTkFont(size=14)
            ).grid(row=1, column=0, pady=(5,0))
        
        # Start button
        ctk.CTkButton(
            input_frame,
            text="Set Timer",
            command=self.set_timer,
            font=ctk.CTkFont(size=14),
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            width=120,
            height=40
        ).pack(pady=20)

    def setup_control_buttons(self, parent):
        """Create control buttons with modern styling"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Pause/Resume button
        self.start_button = ctk.CTkButton(
            button_frame,
            text="⏸️ Pause",
            command=self.start_pause,
            font=ctk.CTkFont(size=14),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=120,
            height=40
        )
        self.start_button.pack(side="left", padx=10)
        
        # Reset button
        self.reset_button = ctk.CTkButton(
            button_frame,
            text="🔄 Restart",
            command=self.reset,
            font=ctk.CTkFont(size=14),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=120,
            height=40,
            state="disabled"
        )
        self.reset_button.pack(side="left", padx=10)

    def validate_number(self, value):
        """Validate input to ensure only numbers 0-99 are entered"""
        if value == "":
            return True
        try:
            num = int(value)
            return 0 <= num <= 99
        except ValueError:
            return False

    def set_timer(self):
        """Set the timer based on input values"""
        try:
            hours = int(self.hours_var.get() or 0)
            minutes = int(self.minutes_var.get() or 0)
            seconds = int(self.seconds_var.get() or 0)
            
            if minutes >= 60 or seconds >= 60:
                raise ValueError("Minutes and seconds must be less than 60")
                
            total_seconds = hours * 3600 + minutes * 60 + seconds
            
            if total_seconds == 0:
                return
                
            self.time_left = total_seconds
            self.original_time = total_seconds
            self.update_display()
            self.reset_button.configure(state="normal")
            self.start_pause()  # Auto-start the timer
            
        except ValueError as e:
            print(f"Invalid input: {str(e)}")

    def start_pause(self):
        """Toggle between running and paused states"""
        if self.time_left == 0:
            return
            
        if not self.running:
            self.running = True
            self.start_button.configure(
                text="⏸️ Pause",
                fg_color="#f1c40f",
                hover_color="#f39c12"
            )
            self.update()
        else:
            self.running = False
            self.start_button.configure(
                text="▶ Resume",
                fg_color="#2ecc71",
                hover_color="#27ae60"
            )

    def update(self):
        """Update the timer countdown"""
        if self.running and self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            if self.time_left > 0:
                self.window.after(1000, self.update)
            else:
                self.timer_complete()

    def update_display(self):
        """Update the visual elements (time display and progress ring)"""
        # Update time label
        hours = self.time_left // 3600
        minutes = (self.time_left % 3600) // 60
        seconds = self.time_left % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_label.configure(text=time_str)
        
        # Update progress ring
        if self.original_time > 0:
            progress = self.time_left / self.original_time
            degrees = progress * 360
            self.canvas.itemconfig(self.progress_ring, extent=degrees)

    def timer_complete(self):
        """Handle timer completion"""
        self.running = False
        self.start_button.configure(
            text="▶ Start",
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.time_label.configure(text="Time's Up!")
        self.canvas.itemconfig(self.progress_ring, extent=0)
        
        # Send system notification
        notification.notify(
            title='Timer Complete',
            message='Your timer has finished!',
            app_name='PythonTimer',
            timeout=10
        )

    def reset(self):
        """Reset the timer to original time"""
        self.running = False
        self.time_left = self.original_time
        self.start_button.configure(
            text="▶ Start",
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.update_display()

    def run(self):
        """Start the timer application"""
        self.window.mainloop()

def parse_time_str(time_str):
    """
    Parse natural language time string into seconds.
    Handles formats like:
    - '5 minutes'
    - '2h 30m'
    - '1 hour 30 minutes'
    - '90s'
    - '1:30:00'
    - '2.5 hours'
    """
    try:
        # Remove any leading/trailing whitespace
        time_str = time_str.strip().lower()
        
        # Try parsing HH:MM:SS format first
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = map(int, parts)
                return m * 60 + s
        
        # Handle abbreviated formats like "2h30m", "5m30s"
        abbreviated = re.match(r'^(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$', 
                             time_str.replace(' ', ''))
        if abbreviated:
            h, m, s = abbreviated.groups()
            total = 0
            if h: total += int(h) * 3600
            if m: total += int(m) * 60
            if s: total += int(s)
            if total > 0:
                return total
        
        # Handle decimal hours/minutes (e.g., "2.5 hours", "1.5 minutes")
        decimal = re.match(r'(\d*\.?\d+)\s*(hour|minute|second)s?', time_str)
        if decimal:
            value = float(decimal.group(1))
            unit = decimal.group(2)
            if unit == 'hour':
                return int(value * 3600)
            elif unit == 'minute':
                return int(value * 60)
            elif unit == 'second':
                return int(value)
        
        # Try parsing with dateutil for more natural language
        try:
            # Create a base time
            base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # Parse the relative time
            parsed_time = parser.parse(time_str, default=base_time, fuzzy=True)
            # Calculate the difference
            delta = parsed_time - base_time
            return int(delta.total_seconds())
        except:
            pass
        
        # Handle simple numeric input (assume minutes)
        if time_str.isdigit():
            return int(time_str) * 60
            
        raise ValueError("Could not parse time string")
        
    except Exception as e:
        print(f"Error parsing time: {str(e)}")
        return 0

async def func(args):
    """Handle timer commands for integration"""
    try:
        command = args.get('command', '').lower()
        time_str = args.get('time', '')
        
        if command == 'open':
            # Handle "set timer for X minutes" type commands
            if time_str:
                seconds = parse_time_str(time_str)
                if seconds > 0:
                    timer = ModernTimer(seconds)
                    timer.run()
                    return json.dumps({"message": f"Timer started for {time_str}"})
            # Just open timer window without setting time
            timer = ModernTimer()
            timer.run()
            return json.dumps({"message": "Timer opened"})
            
        elif command == 'close':
            # Close any existing timer windows
            if ctk._CTk__cls_windows:
                for window in ctk._CTk__cls_windows:
                    window.destroy()
            return json.dumps({"message": "Timer closed"})
            
        else:
            return json.dumps({
                "error": "Invalid command. Use 'open' or 'close'"
            })
            
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

# Integration configuration
object = {
    "name": "timer",
    "description": "Set and control a countdown timer. Examples: 'Set timer for 5 minutes', 'Start 2 hour timer', 'Open timer', 'Close timer'",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": ["open", "close"],
                "description": "Open or close the timer"
            },
            "time": {
                "type": "string",
                "description": "Time duration in natural language (e.g., '5 minutes', '2 hours')"
            }
        },
        "required": ["command"]
    }
}

modules = ['customtkinter', 'plyer', 'python-dateutil']