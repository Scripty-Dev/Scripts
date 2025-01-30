import json
import requests
from tzlocal import get_localzone

def get_user_timezone():
    try:
        return str(get_localzone())
    except:
        return 'UTC'

def get_calendar_events():
    try:
        response = requests.get(
            f"https://scripty.me/api/assistant/calendar/events?token={config['token']}"
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_calendar_event(summary, description, start_time, end_time):
    try:
        # Get user's local timezone
        timezone = get_user_timezone()
        
        data = {
            "summary": summary,
            "description": description,
            "startTime": start_time,
            "endTime": end_time,
            "timeZone": timezone
        }
        
        response = requests.post(
            f"https://scripty.me/api/assistant/calendar/events?token={config['token']}", 
            json=data
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

async def func(args):
    try:
        action = args.get("action")
        if not action:
            return json.dumps({"success": False, "error": "Action is required"})

        if action == "get_events":
            return json.dumps(get_calendar_events())
        
        elif action == "create_event":
            required_fields = ["summary", "description", "start_time", "end_time"]
            missing_fields = [field for field in required_fields if field not in args]
            if missing_fields:
                return json.dumps({
                    "success": False, 
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
            
            return json.dumps(create_calendar_event(
                args["summary"],
                args["description"],
                args["start_time"],
                args["end_time"]
            ))
        
        else:
            return json.dumps({
                "success": False, 
                "error": f"Unknown action: {action}"
            })

    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

object = {
    "name": "calendar_manager",
    "description": "Manage Google Calendar events using server API. Times are automatically handled in your local timezone.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform (get_events or create_event)",
                "enum": ["get_events", "create_event"]
            },
            "summary": {
                "type": "string",
                "description": "Event title/summary (required for create_event)"
            },
            "description": {
                "type": "string",
                "description": "Event description (required for create_event)"
            },
            "start_time": {
                "type": "string",
                "description": "Event start time in ISO format (e.g., '2024-01-30T15:00:00')"
            },
            "end_time": {
                "type": "string",
                "description": "Event end time in ISO format (e.g., '2024-01-30T16:00:00')"
            }
        },
        "required": ["action"]
    }
}

modules = ['requests', 'tzlocal']
