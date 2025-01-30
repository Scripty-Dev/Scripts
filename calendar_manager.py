import json
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import platform
from tzlocal import get_localzone

def get_user_timezone():
    try:
        local_tz = get_localzone()
        # Extract the IANA timezone string
        if hasattr(local_tz, 'key'):
            return local_tz.key
        elif hasattr(local_tz, 'zone'):
            return local_tz.zone
        else:
            return str(local_tz)  # Fallback to string representation
    except:
        return 'UTC'

def parse_time(time_str):
    local_tz = ZoneInfo(get_user_timezone())
    now = datetime.now(local_tz)
    
    if time_str.lower().startswith("tomorrow"):
        time_part = time_str.split(" ", 1)[1]
        try:
            # Try parsing as 24-hour format
            time_obj = datetime.strptime(time_part, "%H:%M")
        except ValueError:
            # Try parsing as 12-hour format
            time_obj = datetime.strptime(time_part, "%I:%M %p")
        
        tomorrow = now + timedelta(days=1)
        naive_time = datetime.combine(tomorrow.date(), time_obj.time())
        return naive_time.replace(tzinfo=local_tz)
    
    try:
        parsed_time = datetime.fromisoformat(time_str)
        if parsed_time.tzinfo is None:
            return parsed_time.replace(tzinfo=local_tz)
        return parsed_time
    except ValueError:
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
        except ValueError:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
        naive_time = datetime.combine(now.date(), time_obj.time())
        return naive_time.replace(tzinfo=local_tz)

def create_calendar_event(summary, start_time, end_time=None, description=None):
    try:
        # Get the IANA timezone string
        timezone = get_user_timezone()
        
        # Parse times and ensure they're timezone-aware
        start_time_dt = parse_time(start_time)
        if end_time:
            end_time_dt = parse_time(end_time)
        else:
            end_time_dt = start_time_dt + timedelta(hours=1)
        
        data = {
            "summary": summary,
            "startTime": start_time_dt.isoformat(),
            "endTime": end_time_dt.isoformat(),
            "timeZone": timezone
        }
        
        if description:
            data["description"] = description
        
        headers = {
            "Authorization": f"Bearer {authtoken}"
        }
        
        response = requests.post(
            "https://scripty.me/api/assistant/calendar/events",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_calendar_events():
    try:
        headers = {
            "Authorization": f"Bearer {authtoken}"
        }
        response = requests.get(
            "https://scripty.me/api/assistant/calendar/events",
            headers=headers
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
            required_fields = ["summary", "start_time"]
            missing_fields = [field for field in required_fields if field not in args]
            if missing_fields:
                return json.dumps({
                    "success": False, 
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
            
            return json.dumps(create_calendar_event(
                args["summary"],
                args["start_time"],
                args.get("end_time"),
                args.get("description")
            ))
        
        else:
            return json.dumps({
                "success": False, 
                "error": f"Unknown action: {action}"
            })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

# Function definition for the API
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
                "description": "Event description (optional for create_event)"
            },
            "start_time": {
                "type": "string",
                "description": "Event start time in natural language or ISO format (e.g., 'tomorrow 5:00 PM' or '2024-01-30T15:00:00')"
            },
            "end_time": {
                "type": "string",
                "description": "Event end time in natural language or ISO format (e.g., 'tomorrow 6:00 PM' or '2024-01-30T16:00:00'). If not provided, defaults to 1 hour after start_time."
            }
        },
        "required": ["action"]
    }
}

modules = ['requests', 'tzlocal']
