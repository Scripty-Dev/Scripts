import sys
import json
import asyncio
import tkinter as tk
from tkinter import ttk
import time
import os

class Stopwatch:
    """A simple stopwatch with GUI interface"""
    def __init__(self):
        # Create and configure the main window
        self.root = tk.Tk()
        self.root.title("Stopwatch")
        
        # Center the window on screen
        window_width = 450
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Initialize state variables
        self.time = 0
        self.running = False
        self.laps = []
        
        self.setup_gui()
    
    def setup_gui(self):
        """Set up all GUI elements"""
        # Main frame to hold all elements
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Time display label
        self.time_label = ttk.Label(
            self.main_frame,
            text="00:00:00.00",
            font=('Arial', 48)
        )
        self.time_label.grid(row=0, column=0, columnspan=3, pady=20)
        
        # Configure button style
        style = ttk.Style()
        style.configure('Primary.TButton', font=('Arial', 12))
        
        # Control buttons
        self.start_button = ttk.Button(
            self.main_frame,
            text="Start",
            command=self.start_pause,
            style='Primary.TButton',
            width=10
        )
        self.start_button.grid(row=1, column=0, padx=5)
        
        self.lap_button = ttk.Button(
            self.main_frame,
            text="Lap",
            command=self.lap,
            style='Primary.TButton',
            width=10,
            state='disabled'
        )
        self.lap_button.grid(row=1, column=1, padx=5)
        
        self.reset_button = ttk.Button(
            self.main_frame,
            text="Reset",
            command=self.reset,
            style='Primary.TButton',
            width=10,
            state='disabled'
        )
        self.reset_button.grid(row=1, column=2, padx=5)
        
        # Set up lap times display
        self.setup_lap_display()

    def setup_lap_display(self):
        """Set up the scrollable lap times display"""
        self.lap_frame = ttk.Frame(self.main_frame)
        self.lap_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.lap_canvas = tk.Canvas(self.lap_frame, height=100)
        self.scrollbar = ttk.Scrollbar(
            self.lap_frame, 
            orient="vertical", 
            command=self.lap_canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.lap_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.lap_canvas.configure(
                scrollregion=self.lap_canvas.bbox("all")
            )
        )
        
        self.lap_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.lap_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.lap_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def start_pause(self):
        """Toggle between start and pause states"""
        if not self.running:
            self.running = True
            self.start_button.configure(text="Pause")
            self.lap_button.configure(state='normal')
            self.reset_button.configure(state='normal')
            self.update()
        else:
            self.running = False
            self.start_button.configure(text="Start")
    
    def update(self):
        """Update the time display"""
        if self.running:
            self.time += 0.01
            self.update_display()
            self.root.after(10, self.update)
    
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
        lap_label = ttk.Label(
            self.scrollable_frame,
            text=f"Lap {len(self.laps) + 1}: {current_time}",
            font=('Arial', 10)
        )
        lap_label.pack(pady=2)
        self.laps.append(current_time)
    
    def reset(self):
        """Reset the stopwatch"""
        self.running = False
        self.time = 0
        self.time_label.configure(text="00:00:00.00")
        self.start_button.configure(text="Start")
        self.lap_button.configure(state='disabled')
        self.reset_button.configure(state='disabled')
        
        # Clear lap times
        self.laps.clear()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def close(self):
        """Close the stopwatch window"""
        self.root.quit()
        self.root.destroy()

    def run(self):
        """Start the application"""
        self.root.mainloop()

async def func(args):
    """Handle stopwatch commands - only open and close"""
    try:
        command = args.get('command', '').lower()
        
        if command == 'open':
            # Start new stopwatch window
            stopwatch = Stopwatch()
            stopwatch.run()
            return json.dumps({"message": "Stopwatch opened"})
            
        elif command == 'close':
            # This will close any existing stopwatch windows
            for widget in tk.Tk.winfo_children(tk._default_root) if tk._default_root else []:
                widget.destroy()
            if tk._default_root:
                tk._default_root.quit()
            return json.dumps({"message": "Stopwatch closed"})
            
        else:
            return json.dumps({
                "error": "Invalid command. Use 'open' or 'close'"
            })
            
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

object = {
    "name": "stopwatch",
    "description": "Open or close a stopwatch window. Examples: 'Open stopwatch', 'Close timer', 'Launch stopwatch'",
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

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1].replace("'", '"'))
                result = asyncio.run(func(args))
                print(result)
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"JSON Error: {str(e)}"}))
            except Exception as e:
                print(json.dumps({"error": f"Error: {str(e)}"}))