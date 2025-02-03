import sys
import json
import datetime
import subprocess
from pathlib import Path
import os
from plyer import notification

async def func(args):
    """
    Set or cancel notifications using Task Scheduler with plyer.
    Runs in background without visible terminal.
    """
    try:
        operation = args.get("operation")
        
        # Use AppData for the scripts
        scripts_dir = Path.home() / "AppData" / "Local" / "NotificationScripts"
        scripts_dir.mkdir(exist_ok=True)
        notify_script = scripts_dir / "notification_runner.py"
        
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

        # Create the notification script
        with open(notify_script, 'w') as f:
            f.write(f'''
import time
from plyer import notification
import datetime

target_time = datetime.datetime({target_time.year}, {target_time.month}, {target_time.day}, {target_time.hour}, {target_time.minute})
delay = (target_time - datetime.datetime.now()).total_seconds()
if delay > 0:
    time.sleep(delay)

notification.notify(
    title='Reminder',
    message="""{message}""",
    app_name='PythonReminder',
    timeout=10
)
''')

        # Create unique task name
        task_name = f"PythonNotification_{target_time.strftime('%Y%m%d%H%M%S')}"
        
        # Start the script in background using pythonw.exe
        pythonw_path = str(Path(sys.executable).parent / "pythonw.exe")
        subprocess.Popen(
            [pythonw_path, str(notify_script)],
            creationflags=subprocess.CREATE_NO_WINDOW,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return json.dumps({"message": f"Notification scheduled for {target_time}"})
        
    except Exception as e:
        return json.dumps({"error": str(e)})

# Export object for function configuration
object = {
    "name": "notification_setter",
    "description": "Set or cancel system notifications.",
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
