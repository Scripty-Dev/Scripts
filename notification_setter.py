import sys
import json
import datetime
import subprocess
from plyer import notification
from pathlib import Path
import os
import signal
import psutil

def find_notification_process():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' and any('notification_background.py' in cmd for cmd in proc.info['cmdline'] or []):
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return None

async def func(args):
    try:
        operation = args.get("operation")
        
        if operation == "cancel":
            pid = find_notification_process()
            if pid:
                try:
                    os.kill(pid, signal.SIGTERM)
                    return json.dumps({"message": "Notification cancelled"})
                except:
                    return json.dumps({"error": "Failed to cancel notification"})
            return json.dumps({"error": "No active notification found"})
            
        message = args.get("message", "")
        timestamp = args.get("time", "")
        
        if not message or not timestamp:
            return json.dumps({"error": "Message and time required for setting notification"})

        if len(timestamp) <= 5:
            today = datetime.datetime.now().date()
            time_obj = datetime.datetime.strptime(timestamp, "%H:%M").time()
            target_time = datetime.datetime.combine(today, time_obj)
        else:
            target_time = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")

        delay = (target_time - datetime.datetime.now()).total_seconds()
        if delay < 0:
            return json.dumps({"error": "Cannot set notification in the past"})

        notify_script = Path(os.path.dirname(os.path.abspath(__file__))) / "notification_background.py"
        with open(notify_script, 'w') as f:
            f.write(f'''
import time
from plyer import notification
time.sleep({delay})
notification.notify(
    title='Reminder',
    message="""{message}""",
    app_name='PythonReminder',
    timeout=10
)
''')

        subprocess.Popen([sys.executable, str(notify_script)],
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        
        return json.dumps({"message": f"Notification scheduled for {target_time}"})
        
    except Exception as e:
        return json.dumps({"error": str(e)})

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
            "message": {"type": "string", "description": "Notification message"},
            "time": {"type": "string", "description": "Time in HH:MM or YYYY-MM-DD HH:MM format"}
        },
        "required": ["operation"]
    }
}

modules = ['plyer', 'psutil']
