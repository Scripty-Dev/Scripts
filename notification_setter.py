import sys
import json
import datetime
from pathlib import Path
from plyer import notification
try:
    import win32com.client
except ImportError:
    from win32.com import client as win32com_client
    win32com = win32com_client

async def func(args):
    """Set or cancel Windows notifications using Task Scheduler"""
    try:
        operation = args.get("operation")
        
        # Get Python executable path and create scheduler
        python_path = sys.executable
        scheduler = win32com.Dispatch('Schedule.Service')
        scheduler.Connect()
        root_folder = scheduler.GetFolder('\\')
        
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
            # Get all tasks and cancel ones with our prefix
            tasks = root_folder.GetTasks(0)  # 0 means get all tasks
            for task in tasks:
                if task.Name.startswith('PyNotify_'):
                    root_folder.DeleteTask(task.Name, 0)
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
        
        # Create the task with properly resolved paths
        command = f'"{python_path}" "{script_path}" "{message}"'
        scheduler.GetFolder('\\').NewTask(
            0,
            task_name,
            command,
            target_time.strftime('%H:%M'),
            target_time.strftime('%Y/%m/%d')
        )

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
modules = ['plyer', 'pywin32', 'pypiwin32']
