import json
import requests
import dateparser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import platform
from tzlocal import get_localzone

def get_user_timezone():
    """Get the user's local timezone"""
    try:
        local_tz = get_localzone()
        if hasattr(local_tz, 'key'):
            return local_tz.key
        elif hasattr(local_tz, 'zone'):
            return local_tz.zone
        else:
            return str(local_tz)
    except:
        return 'UTC'

def parse_time(time_str):
    """
    Parse time string using multiple methods, with better handling for date-only expressions
    """
    local_tz = ZoneInfo(get_user_timezone())
    now = datetime.now(local_tz)

    # Special handling for date-only expressions
    if time_str.lower() in ['today', 'tomorrow', 'yesterday']:
        base_date = now
        if time_str.lower() == 'tomorrow':
            base_date += timedelta(days=1)
        elif time_str.lower() == 'yesterday':
            base_date -= timedelta(days=1)
        return base_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Try dateparser first
    parsed_date = dateparser.parse(
        time_str,
        settings={
            'TIMEZONE': str(local_tz),
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future'
        }
    )
    
    if parsed_date:
        return parsed_date

    # Handle specific time formats
    try:
        # Try parsing as ISO format
        parsed_time = datetime.fromisoformat(time_str)
        if parsed_time.tzinfo is None:
            return parsed_time.replace(tzinfo=local_tz)
        return parsed_time
    except ValueError:
        try:
            # Try parsing as 24-hour time
            time_obj = datetime.strptime(time_str, "%H:%M")
            naive_time = datetime.combine(now.date(), time_obj.time())
            return naive_time.replace(tzinfo=local_tz)
        except ValueError:
            try:
                # Try parsing as 12-hour time
                time_obj = datetime.strptime(time_str, "%I:%M %p")
                naive_time = datetime.combine(now.date(), time_obj.time())
                return naive_time.replace(tzinfo=local_tz)
            except ValueError:
                raise ValueError(f"Could not parse time string: {time_str}")

def create_calendar_event(summary, start_time, end_time=None, description=None):
    """
    Create a new calendar event
    """
    try:
        timezone = get_user_timezone()
        start_time_dt = parse_time(start_time)
        
        # If no end time provided, default to start time + 1 hour
        if end_time is None:
            end_time_dt = start_time_dt + timedelta(hours=1)
        else:
            end_time_dt = parse_time(end_time)
        
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
    """
    Get all calendar events
    """
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

def get_free_slots(start_date=None, end_date=None, min_duration=30):
    """
    Get free time slots in calendar.
    start_date: can be 'today', 'tomorrow', or other natural language date expressions
    end_date: same as start_date
    min_duration: minimum duration of free slot in minutes
    """
    try:
        timezone = get_user_timezone()
        local_tz = ZoneInfo(timezone)
        now = datetime.now(local_tz)
        
        if not start_date:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            try:
                start_date = parse_time(start_date)
            except ValueError as e:
                return {"success": False, "error": str(e)}
        
        if not end_date:
            # Default to end of current week
            days_until_sunday = (6 - now.weekday()) % 7
            end_date = (now + timedelta(days=days_until_sunday)).replace(
                hour=23, minute=59, second=59, microsecond=0
            )
        else:
            try:
                end_date = parse_time(end_date)
            except ValueError as e:
                return {"success": False, "error": str(e)}
        
        headers = {
            "Authorization": f"Bearer {authtoken}"
        }
        response = requests.get(
            "https://scripty.me/api/assistant/calendar/events",
            headers=headers
        )
        response.raise_for_status()
        events = response.json().get('items', [])
        
        busy_slots = []
        for event in events:
            event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
            event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
            
            if event_start.tzinfo is None:
                event_start = event_start.replace(tzinfo=local_tz)
            if event_end.tzinfo is None:
                event_end = event_end.replace(tzinfo=local_tz)
                
            if event_end > start_date and event_start < end_date:
                busy_slots.append((event_start, event_end))
        
        busy_slots.sort(key=lambda x: x[0])
        
        free_slots = []
        current_time = max(start_date, now)
        
        for busy_start, busy_end in busy_slots:
            if current_time + timedelta(minutes=min_duration) <= busy_start:
                free_slots.append({
                    "start": current_time.isoformat(),
                    "end": busy_start.isoformat()
                })
            current_time = max(current_time, busy_end)
        
        if current_time + timedelta(minutes=min_duration) <= end_date:
            free_slots.append({
                "start": current_time.isoformat(),
                "end": end_date.isoformat()
            })
            
        return {
            "success": True,
            "free_slots": free_slots,
            "timezone": timezone,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def func(args):
    """
    Main function to handle different calendar actions
    """
    try:
        action = args.get("action")
        if not action:
            return json.dumps({"success": False, "error": "Action is required"})
        
        if action == "get_free_slots":
            return json.dumps(get_free_slots(
                args.get("start_date"),
                args.get("end_date"),
                int(args.get("min_duration", 30))
            ))
        elif action == "get_events":
            return json.dumps(get_calendar_events())
        elif action == "create_event":
            # Only validate start_time
            if "start_time" not in args:
                return json.dumps({
                    "success": False, 
                    "error": "Missing required field: start_time"
                })
            
            return json.dumps(create_calendar_event(
                args.get("summary", "New Event"),
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

# API definition with detailed parameter descriptions
object = {
    "name": "calendar_manager",
    "description": "Manage Google Calendar events and find free time slots. All times are handled in your local timezone.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: 'get_events' (list all events), 'create_event' (create new event), or 'get_free_slots' (find available time slots)",
                "enum": ["get_events", "create_event", "get_free_slots"]
            },
            "summary": {
                "type": "string",
                "description": "Event title (optional for create_event, defaults to 'New Event')"
            },
            "description": {
                "type": "string",
                "description": "Event description (optional for create_event)"
            },
            "start_time": {
                "type": "string",
                "description": "Event start time (required for create_event). Accepts multiple formats:\n- ISO format: '2024-01-30T15:00:00'\n- Natural language: 'tomorrow 3:00 PM', 'next monday at 2pm'\n- 24-hour time: '15:00'\n- 12-hour time: '3:00 PM'"
            },
            "end_time": {
                "type": "string",
                "description": "Event end time (required for create_event). Accepts same formats as start_time"
            },
            "start_date": {
                "type": "string",
                "description": "Start date for finding free slots (optional for get_free_slots). Accepts ISO format ('2024-01-30') or natural language ('today', 'tomorrow', 'next week'). Defaults to today"
            },
            "end_date": {
                "type": "string",
                "description": "End date for finding free slots (optional for get_free_slots). Accepts same formats as start_date. Defaults to end of current week"
            },
            "min_duration": {
                "type": "integer",
                "description": "Minimum duration in minutes for free time slots (optional for get_free_slots, defaults to 30)"
            }
        },
        "required": ["action"]
    }
}

modules = ['requests', 'tzlocal', 'dateparser']
