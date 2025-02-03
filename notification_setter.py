import sys
import json
import datetime
import sqlite3
from pathlib import Path
import os
import subprocess
import re

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
        """Parse time string in common formats"""
        timestamp = timestamp.lower().strip()
        now = datetime.datetime.now()
        
        # Handle "today" and "tomorrow" keywords
        if timestamp == "today":
            return now
        if timestamp.startswith("tomorrow"):
            base_date = now.date() + datetime.timedelta(days=1)
            if len(timestamp) > 8:  # has time component
                time_part = timestamp[9:].strip()
            else:
                time_part = now.strftime("%H:%M")
        else:
            base_date = now.date()
            time_part = timestamp

        # Try to parse time in various formats
        time_formats = [
            ("%H:%M", r'^\d{1,2}:\d{2}$'),
            ("%I:%M%p", r'^\d{1,2}:\d{2}[ap]m$'),
            ("%I%p", r'^\d{1,2}[ap]m$'),
            ("%Y-%m-%d %H:%M", r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'),
        ]

        # Clean up the time string
        time_part = time_part.replace(" ", "")  # remove spaces
        if time_part[-2:].lower() in ['am', 'pm']:
            if ':' not in time_part:
                time_part = time_part[:-2] + ":00" + time_part[-2:]

        # Try each format
        for fmt, pattern in time_formats:
            if re.match(pattern, time_part):
                try:
                    if "-%d" in fmt:  # Full date format
                        return datetime.datetime.strptime(time_part, fmt)
                    else:  # Time only format
                        time_obj = datetime.datetime.strptime(time_part, fmt).time()
                        return datetime.datetime.combine(base_date, time_obj)
                except ValueError:
                    continue

        raise ValueError(f"Could not parse time: {timestamp}")

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
                    (message, target_time.isoformat(), task_name)
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
                '/sd', target_time.strftime('%d/%m/%Y'),
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
    Supports various time formats including 'today', 'tomorrow 5pm', '5:30pm', etc.
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
    "description": "Set or cancel Windows system notifications that persist through system restarts. Supports various time formats.",
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
                "description": "Time for the notification. Supports formats like: 'today', 'tomorrow 5pm', '5:30pm', '14:30', '2024-02-05 15:30'"
            }
        },
        "required": ["operation"]
    }
}

# Required Python packages
modules = ['winotify']
