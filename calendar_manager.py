import json
import requests
import pytz
from datetime import datetime
from dateutil import parser

# Function to get the user's local timezone
def get_user_timezone():
    try:
        return str(pytz.tzlocal())
    except:
        return 'UTC'

# Function to fetch calendar events
def get_calendar_events():
    try:
        response = requests.get(
            f"https://scripty.me/api/assistant/calendar/events?token={config['token']}"
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

# Function to create a calendar event
def create_calendar_event(summary, start_time, end_time, description=None):
    try:
        # Get user's local timezone
        timezone = get_user_timezone()
        
        # Parse natural language time strings into ISO format
        start_time_iso = parser.parse(start_time).isoformat()
        end_time_iso = parser.parse(end_time).isoformat()
        
        # Prepare the data payload
        data = {
            "summary": summary,
            "startTime": start_time_iso,
            "endTime": end_time_iso,
            "timeZone": timezone
        }
        
        # Add description if provided
        if description:
            data["description"] = description
        
        # Send the request to create the event
        response = requests.post(
            f"https://scripty.me/api/assistant/calendar/events?token={config['token']}", 
            json=data
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

# Main function to handle actions
async def func(args):
    try:
        action = args.get("action")
        if not action:
            return json.dumps({"success": False, "error": "Action is required"})
            
        if action == "get_events":
            return json.dumps(get_calendar_events())
        
        elif action == "create_event":
            required_fields = ["summary", "start_time", "end_time"]
            missing_fields = [field for field in required_fields if field not in args]
            if missing_fields:
                return json.dumps({
                    "success": False, 
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
            
            return json.dumps(create_calendar_event(
                args["summary"],
                args["start_time"],
                args["end_time"],
                args.get("description")  # Optional field
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
                "description": "Event end time in natural language or ISO format (e.g., 'tomorrow 6:00 PM' or '2024-01-30T16:00:00')"
            }
        },
        "required": ["action"]
    }
}

# Required modules
modules = ['requests', 'pytz', 'dateutil']
