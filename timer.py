import sys
import json
import asyncio
import tkinter as tk
from tkinter import ttk
import time
import re
from plyer import notification  # Added import for notifications

class Timer:
    """
    A modern countdown timer with GUI interface.
    Features:
    - Visual countdown with circular progress indicator
    - Natural language time input parsing
    - Clean, modern interface with intuitive controls
    - System notifications when timer completes
    """
    def __init__(self, initial_time=0):
        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Timer")
        
        # Center the window on screen
        window_width = 500
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Initialize state variables
        self.time_left = initial_time  # Time remaining in seconds
        self.running = False
        self.original_time = initial_time
        
        # Set up the GUI elements
        self.setup_gui()
        
        # If initial time was provided, start the timer automatically
        if initial_time > 0:
            self.update_display()
            self.reset_button.configure(state='normal')
            self.start_pause()

    def setup_gui(self):
        """Set up all GUI elements with a clean, modern design"""
        # Main frame with light gray background
        self.root.configure(bg='#f0f0f0')
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Time input section at the top
        self.setup_time_input()
        
        # Create canvas for the timer ring
        self.canvas = tk.Canvas(
            self.main_frame, 
            width=300,
            height=300,
            bg='white',
            highlightthickness=0
        )
        self.canvas.grid(row=1, column=0, columnspan=3, pady=20)
        
        # Draw the background ring (gray)
        self.canvas.create_oval(
            25, 25, 275, 275,
            width=8,
            outline='#f0f0f0'
        )
        
        # Draw the progress ring (blue)
        self.progress_ring = self.canvas.create_arc(
            25, 25, 275, 275,
            start=90,
            extent=360,
            width=8,
            outline='#007bff',
            style=tk.ARC
        )
        
        # Time display in the center of the ring
        self.time_label = ttk.Label(
            self.canvas,
            text="00:00:00",
            font=('Arial', 36, 'bold'),
            background='white'
        )
        self.time_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Control buttons below the timer
        self.setup_control_buttons()

    def setup_time_input(self):
        """Create a modern time input section with three fields for hours, minutes, and seconds"""
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=0, column=0, columnspan=3, pady=20)
        
        # Style configuration for input elements
        style = ttk.Style()
        style.configure('Timer.TEntry', 
            padding=10,
            font=('Arial', 12)
        )
        style.configure('Timer.TLabel',
            font=('Arial', 12),
            padding=5
        )
        
        # Input validation function
        vcmd = (self.root.register(self.validate_number), '%P')
        
        # Create three input fields with labels
        self.hours_var = tk.StringVar(value="0")
        self.minutes_var = tk.StringVar(value="0")
        self.seconds_var = tk.StringVar(value="0")
        
        time_inputs = [
            ("Hours", self.hours_var),
            ("Minutes", self.minutes_var),
            ("Seconds", self.seconds_var)
        ]
        
        for col, (label, var) in enumerate(time_inputs):
            container = ttk.Frame(input_frame)
            container.grid(row=0, column=col, padx=15)
            
            entry = ttk.Entry(
                container,
                width=3,
                textvariable=var,
                validate='all',
                validatecommand=vcmd,
                style='Timer.TEntry',
                font=('Arial', 14)
            )
            entry.grid(row=0, column=0, padx=5)
            
            ttk.Label(
                container,
                text=label,
                style='Timer.TLabel'
            ).grid(row=1, column=0, pady=(5,0))
        
        # Start button
        style.configure('Set.TButton',
            font=('Arial', 12, 'bold'),
            padding=10
        )
        
        ttk.Button(
            input_frame,
            text="▶ Start",
            command=self.set_timer,
            style='Set.TButton'
        ).grid(row=0, column=3, padx=(30,0))

    def setup_control_buttons(self):
        """Create control buttons (Pause/Resume and Reset)"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        style = ttk.Style()
        style.configure('Timer.TButton',
            font=('Arial', 12, 'bold'),
            padding=10
        )
        
        # Pause/Resume button
        self.start_button = ttk.Button(
            button_frame,
            text="⏸️ Pause",
            command=self.start_pause,
            style='Timer.TButton',
            width=10
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Reset button
        self.reset_button = ttk.Button(
            button_frame,
            text="🔄 Restart",
            command=self.reset,
            style='Timer.TButton',
            width=10,
            state='disabled'
        )
        self.reset_button.grid(row=0, column=1, padx=5)

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
            self.reset_button.configure(state='normal')
            self.start_pause()  # Auto-start the timer
            
        except ValueError as e:
            print(f"Invalid input: {str(e)}")

    def start_pause(self):
        """Toggle between running and paused states"""
        if self.time_left == 0:
            return
            
        if not self.running:
            self.running = True
            self.start_button.configure(text="⏸️ Pause")
            self.update()
        else:
            self.running = False
            self.start_button.configure(text="▶ Resume")

    def update(self):
        """Update the timer countdown"""
        if self.running and self.time_left > 0:
            self.time_left -= 1
            self.update_display()
            if self.time_left > 0:
                self.root.after(1000, self.update)
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
        self.start_button.configure(text="▶ Start")
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
        self.start_button.configure(text="▶ Start")
        self.update_display()

    def run(self):
        """Start the timer application"""
        self.root.mainloop()

def parse_time_str(time_str):
    """
    Parse natural language time string into seconds.
    Examples: "5 minutes", "2 hours and 30 minutes", "90 seconds"
    """
    total_seconds = 0
    
    # Convert common words to standard forms
    time_str = time_str.lower()
    time_str = time_str.replace('hr', 'hour')
    time_str = time_str.replace('min', 'minute')
    time_str = time_str.replace('sec', 'second')
    
    # Find all number-unit pairs
    patterns = [
        (r'(\d+)\s*hours?', 3600),    # hours to seconds
        (r'(\d+)\s*minutes?', 60),     # minutes to seconds
        (r'(\d+)\s*seconds?', 1)       # seconds as is
    ]
    
    for pattern, multiplier in patterns:
        matches = re.findall(pattern, time_str)
        for match in matches:
            total_seconds += int(match) * multiplier
            
    return total_seconds

async def func(args):
    """Handle timer commands for Scripty integration"""
    try:
        command = args.get('command', '').lower()
        time_str = args.get('time', '')
        
        if command == 'open':
            # Handle "set timer for X minutes" type commands
            if time_str:
                seconds = parse_time_str(time_str)
                if seconds > 0:
                    timer = Timer(seconds)
                    timer.run()
                    return json.dumps({"message": f"Timer started for {time_str}"})
            # Just open timer window without setting time
            timer = Timer()
            timer.run()
            return json.dumps({"message": "Timer opened"})
            
        elif command == 'close':
            # Close any existing timer windows
            for widget in tk.Tk.winfo_children(tk._default_root) if tk._default_root else []:
                widget.destroy()
            if tk._default_root:
                tk._default_root.quit()
            return json.dumps({"message": "Timer closed"})
            
        else:
            return json.dumps({
                "error": "Invalid command. Use 'open' or 'close'"
            })
            
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

# Scripty integration configuration
object = {
    "name": "timer",
    "description": "Set and control a countdown timer. Examples: 'Set timer for 5 minutes', 'Start 2 hour timer', 'Set 30 minute timer', 'Open timer', 'Close timer'",
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