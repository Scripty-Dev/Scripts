import sys
import json
import asyncio
from datetime import datetime
import pytz

def get_timezone_time(timezone_name):
    """Get current time in specified timezone"""
    try:
        timezone = pytz.timezone(timezone_name)
        current_time = datetime.now(timezone)
        return current_time.strftime("%I:%M %p"), current_time.strftime("%Y-%m-%d")
    except pytz.exceptions.UnknownTimeZoneError:
        return None, None

def find_timezone(query):
    """Find timezone based on city/country name"""
    query = query.lower()
    matches = []
    
    for tz in pytz.all_timezones:
        # Check if query matches timezone name
        if query in tz.lower():
            matches.append(tz)
            continue
        
        # Check for common city/country names
        parts = tz.lower().replace('_', ' ').split('/')
        if any(query in part for part in parts):
            matches.append(tz)
    
    return matches

async def func(args):
    """Handle world clock queries"""
    try:
        location = args.get('location', '').strip()
        
        if not location:
            return json.dumps({"error": "Please specify a location"})
        
        # Find matching timezones
        matches = find_timezone(location)
        
        if not matches:
            return json.dumps({"error": f"Could not find timezone for {location}"})
        
        # Get time for all matches
        results = []
        for tz in matches:
            time_str, date_str = get_timezone_time(tz)
            if time_str and date_str:
                results.append({
                    "timezone": tz,
                    "time": time_str,
                    "date": date_str
                })
        
        if len(results) == 1:
            # Single match, return direct result
            result = results[0]
            return json.dumps({
                "message": f"Time in {result['timezone']}: {result['time']} ({result['date']})"
            })
        else:
            # Multiple matches, return all options
            return json.dumps({
                "message": f"Found {len(results)} matching locations:",
                "results": results
            })
            
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

object = {
    "name": "worldclock",
    "description": "Get current time in any location. Examples: 'What time is it in Tokyo?', 'Current time in London', 'Time in New York'",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City, country, or timezone name"
            }
        },
        "required": ["location"]
    }
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1].replace("'", '"'))
                result = asyncio.run(func(args))
                print(result)
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"JSON Error: {str(e)}"}))
            except Exception as e:
                print(json.dumps({"error": f"Error: {str(e)}"}))