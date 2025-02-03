import sys
import json
import datetime
import win32com.client
from winotify import Notification
import sqlite3
from pathlib import Path
import os

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

    def set_notification(self, message: str, timestamp: str) -> dict:
        """Set a new notification using Windows Task Scheduler"""
        try:
            # Parse timestamp
            if len(timestamp) <= 5:  # HH:MM format
                today = datetime.datetime.now().date()
                time_obj = datetime.datetime.strptime(timestamp, "%H:%M").time()
                target_time = datetime.datetime.combine(today, time_obj)
            else:  # YYYY-MM-DD HH:MM format
                target_time = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

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

            # Create Windows scheduled task
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            
            root_folder = scheduler.GetFolder("\\")
            task_def = scheduler.NewTask(0)

            # Create trigger
            trigger = task_def.Triggers.Create(1)  # One-time trigger
            trigger.StartBoundary = target_time.isoformat()

            # Create action
            action = task_def.Actions.Create(0)
            action.Type = 0  # TASK_ACTION_EXEC

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
            script_path = Path.home() / "AppData" / "Local" / f"{task_name}.py"
            with open(script_path, 'w') as f:
                f.write(notification_script)

            action.Path = sys.executable
            action.Arguments = str(script_path)

            # Set additional settings
            task_def.Settings.Enabled = True
            task_def.Settings.DeleteExpiredTaskAfter = "PT0S"  # Delete after execution

            # Register task
            root_folder.RegisterTaskDefinition(
                task_name,
                task_def,
                6,  # TASK_CREATE_OR_UPDATE
                None,  # No user needed for system task
                None,  # No password
                0  # TASK_LOGON_NONE
            )

            return {"message": f"Notification scheduled for {target_time}"}

        except Exception as e:
            return {"error": str(e)}

    def cancel_notification(self) -> dict:
        """Cancel all pending notifications"""
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder("\\")

            # Cancel all tasks
            with sqlite3.connect(self.db_path) as conn:
                tasks = conn.execute("SELECT task_name FROM notifications").fetchall()
                for (task_name,) in tasks:
                    try:
                        root_folder.DeleteTask(task_name, 0)
                        # Clean up notification script
                        script_path = Path.home() / "AppData" / "Local" / f"{task_name}.py"
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
    "description": "Set or cancel Windows system notifications that persist through system restarts. Uses Windows Task Scheduler for reliability.",
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
                "description": "Time for the notification in either 'HH:MM' format for same-day or 'YYYY-MM-DD HH:MM' for future dates"
            }
        },
        "required": ["operation"]
    }
}

# Required Python packages
modules = ['pywin32', 'winotify']
