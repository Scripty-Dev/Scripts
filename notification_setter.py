import sys
import json
import datetime
import sqlite3
from pathlib import Path
import os
import dateparser
import subprocess

class NotificationManager:
    def __init__(self):
        self.db_path = Path.home() / "AppData" / "Local" / "notifications.db"
        self.setup_database()
        
    def setup_database(self):
        """Create database and tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY,
                    message TEXT NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    task_name TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def parse_time(self, timestamp: str) -> datetime.datetime:
        """Parse time string in natural language format"""
        parsed_time = dateparser.parse(timestamp, settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.datetime.now()
        })
        
        if not parsed_time:
            raise ValueError(f"Could not parse time: {timestamp}")
            
        # If only time was provided (e.g., "5:00" or "5pm"), assume today
        if len(timestamp) <= 5 and ":" in timestamp:
            today = datetime.datetime.now().date()
            time_obj = parsed_time.time()
            parsed_time = datetime.datetime.combine(today, time_obj)
            
        return parsed_time

    def set_notification(self, message: str, timestamp: str) -> dict:
        """Set a new notification using Windows Task Scheduler"""
        try:
            target_time = self.parse_time(timestamp)

            if target_time < datetime.datetime.now():
                return {"error": "Cannot set notification in the past"}

            # Create unique task name
            task_name = f"PythonNotification_{target_time.strftime('%Y%m%d%H%M%S')}"

            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO notifications (message, scheduled_time, task_name) VALUES (?, ?, ?)",
                    (message, target_time, task_name)
                )

            # Create notification script
            notification_script = f'''
from winotify import Notification
toast = Notification(
    app_id="Python Reminder",
    title="Reminder",
    msg="{message}",
    duration="long"
)
toast.show()
'''
            
            # Save notification script
            scripts_dir = Path.home() / "AppData" / "Local" / "NotificationScripts"
            scripts_dir.mkdir(exist_ok=True)
            script_path = scripts_dir / f"{task_name}.py"
            with open(script_path, 'w') as f:
                f.write(notification_script)

            # Create scheduled task using schtasks
            cmd = [
                'schtasks', '/create', '/tn', task_name,
                '/tr', f'"{sys.executable}" "{script_path}"',
                '/sc', 'once',
                '/st', target_time.strftime('%H:%M'),
                '/sd', target_time.strftime('%m/%d/%Y'),
                '/f'  # Force creation
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to create task: {result.stderr}")

            return {"message": f"Notification scheduled for {target_time}"}

        except Exception as e:
            return {"error": str(e)}

    def cancel_notification(self) -> dict:
        """Cancel all pending notifications"""
        try:
            # Cancel all tasks
            with sqlite3.connect(self.db_path) as conn:
                tasks = conn.execute("SELECT task_name FROM notifications").fetchall()
                for (task_name,) in tasks:
                    try:
                        # Delete task using schtasks
                        subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], 
                                    capture_output=True)
                        # Clean up notification script
                        script_path = Path.home() / "AppData" / "Local" / "NotificationScripts" / f"{task_name}.py"
                        if script_path.exists():
                            os.remove(script_path)
                    except:
                        pass
                conn.execute("DELETE FROM notifications")

            return {"message": "Notifications cancelled successfully"}
        except Exception as e:
            return {"error": str(e)}

async def func(args):
    """
    Set or cancel Windows system notifications using Task Scheduler.
    Supports natural language time inputs like 'tomorrow 5pm' or 'next monday 5:30pm'.
    Notifications persist through system restarts and are managed via SQLite database.
    """
    try:
        manager = NotificationManager()
        operation = args.get("operation")
        
        if operation == "cancel":
            return json.dumps(manager.cancel_notification())
            
        message = args.get("message", "")
        timestamp = args.get("time", "")
        
        if not message or not timestamp:
            return json.dumps({"error": "Message and time required for setting notification"})
            
        return json.dumps(manager.set_notification(message, timestamp))
        
    except Exception as e:
        return json.dumps({"error": str(e)})

# Export object for function configuration
object = {
    "name": "notification_setter",
    "description": "Set or cancel Windows system notifications that persist through system restarts. Supports natural language time inputs.",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["set", "cancel"],
                "description": "Operation to perform - 'set' to create a new notification, 'cancel' to remove all pending notifications"
            },
            "message": {
                "type": "string",
                "description": "Message to display in the notification"
            },
            "time": {
                "type": "string",
                "description": "Time for the notification. Supports natural language like 'tomorrow 5pm', 'next monday 5:30pm', as well as formal formats like 'HH:MM' or 'YYYY-MM-DD HH:MM'"
            }
        },
        "required": ["operation"]
    }
}

# Required Python packages
modules = ['winotify', 'dateparser']
