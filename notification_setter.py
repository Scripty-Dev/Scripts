import sys
import json
import datetime
import subprocess
from pathlib import Path
from plyer import notification

async def func(args):
    """Set or cancel Windows notifications using Task Scheduler"""
    try:
        operation = args.get("operation")
        
        # Fixed path in AppData for our notification script
        script_path = Path.home() / "AppData" / "Local" / "notification_display.py"
        
        # Create the notification display script if it doesn't exist
        if not script_path.exists():
            with open(script_path, 'w') as f:
                f.write('''
from plyer import notification
import sys

if len(sys.argv) != 2:
    sys.exit(1)

notification.notify(
    title='Reminder',
    message=sys.argv[1],
    app_name='PythonReminder',
    timeout=10
)
''')

        if operation == "cancel":
            # Cancel all tasks matching our prefix
            result = subprocess.run(
                ['schtasks', '/delete', '/tn', 'PyNotify*', '/f'],
                capture_output=True,
                text=True
            )
            return json.dumps({"message": "All notifications cancelled"})

        message = args.get("message", "")
        timestamp = args.get("time", "")
        
        if not message or not timestamp:
            return json.dumps({"error": "Message and time required"})

        # Parse time
        try:
            if len(timestamp) <= 5:  # HH:MM format
                today = datetime.datetime.now().date()
                time_obj = datetime.datetime.strptime(timestamp, "%H:%M").time()
                target_time = datetime.datetime.combine(today, time_obj)
            else:  # YYYY-MM-DD HH:MM format
                target_time = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

            if target_time < datetime.datetime.now():
                return json.dumps({"error": "Cannot set notification in the past"})
        except ValueError as e:
            return json.dumps({"error": f"Invalid time format: {str(e)}"})

        # Create unique task name
        task_name = f"PyNotify_{target_time.strftime('%Y%m%d%H%M%S')}"
        
        # Set up the scheduled task
        cmd = [
            'schtasks', '/create',
            '/tn', task_name,
            '/tr', f'python "{script_path}" "{message}"',
            '/sc', 'once',
            '/st', target_time.strftime('%H:%M'),
            '/sd', target_time.strftime('%Y/%m/%d'),
            '/f'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            return json.dumps({"error": f"Failed to create notification: {error_msg}"})

        return json.dumps({
            "message": f"Notification scheduled for {target_time.strftime('%Y-%m-%d %H:%M')}"
        })

    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})

# Export object for function configuration
object = {
    "name": "notification_setter",
    "description": "Schedule Windows notifications that persist through system restarts",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["set", "cancel"],
                "description": "Set a new notification or cancel existing ones"
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
