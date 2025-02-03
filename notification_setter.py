import sys
import json
import datetime
import subprocess
from pathlib import Path
import os
from plyer import notification

async def func(args):
    """
    Set or cancel notifications using Task Scheduler but keeping plyer for the actual notifications.
    Uses a single reusable script for all notifications.
    """
    try:
        operation = args.get("operation")
        scripts_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        notify_script = scripts_dir / "notification_runner.py"
        
        # Create the notification runner script if it doesn't exist
        if not notify_script.exists():
            with open(notify_script, 'w') as f:
                f.write('''
import sys
from plyer import notification

if len(sys.argv) > 1:
    message = sys.argv[1]
    notification.notify(
        title='Reminder',
        message=message,
        app_name='PythonReminder',
        timeout=10
    )
''')
        
        if operation == "cancel":
            # Use schtasks to delete all tasks matching our pattern
            subprocess.run(['schtasks', '/delete', '/tn', 'PythonNotification*', '/f'], 
                         capture_output=True)
            return json.dumps({"message": "Notifications cancelled"})
            
        message = args.get("message", "")
        timestamp = args.get("time", "")
        
        if not message or not timestamp:
            return json.dumps({"error": "Message and time required for setting notification"})

        # Parse the time
        if len(timestamp) <= 5:
            today = datetime.datetime.now().date()
            time_obj = datetime.datetime.strptime(timestamp, "%H:%M").time()
            target_time = datetime.datetime.combine(today, time_obj)
        else:
            target_time = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

        if target_time < datetime.datetime.now():
            return json.dumps({"error": "Cannot set notification in the past"})

        # Create unique task name
        task_name = f"PythonNotification_{target_time.strftime('%Y%m%d%H%M%S')}"
        
        # Create the scheduled task
        cmd = [
            'schtasks', '/create', '/tn', task_name,
            '/tr', f'"{sys.executable}" "{notify_script}" "{message}"',
            '/sc', 'once',
            '/st', target_time.strftime('%H:%M'),
            '/sd', target_time.strftime('%Y/%m/%d'),
            '/f'  # Force creation
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return json.dumps({"error": f"Failed to create task: {result.stderr}"})

        return json.dumps({"message": f"Notification scheduled for {target_time}"})
        
    except Exception as e:
        return json.dumps({"error": str(e)})

# Export object for function configuration
object = {
    "name": "notification_setter",
    "description": "Set or cancel system notifications that persist through system restarts.",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["set", "cancel"],
                "description": "Operation to perform"
            },
            "message": {
                "type": "string", 
                "description": "Message to display in the notification"
            },
            "time": {
                "type": "string", 
                "description": "Time in HH:MM or YYYY-MM-DD HH:MM format"
            }
        },
        "required": ["operation"]
    }
}

# Required Python packages
modules = ['plyer']
