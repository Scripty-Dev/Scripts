import sys
import json
import platform
import keyboard
from time import sleep

# Global for platform
PLATFORM = platform.system().lower()

async def func(args):
    """
    Controls media playback - can skip forward or backward
    """
    try:
        if 'action' in args:
            action = args['action'].lower()
            
            if action == "next":
                keyboard.send('next track')
                return json.dumps({"message": "Skipped to next track"})
                
            elif action == "previous":
                keyboard.send('previous track')
                return json.dumps({"message": "Skipped to previous track"})
                
            return json.dumps({"error": "Invalid action. Use 'next' or 'previous'"})
            
        return json.dumps({"error": "Please specify 'action' in the arguments"})
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "controlMedia",
    "description": f"Control media playback on {PLATFORM.capitalize()}. Required format: {{\"action\": string}} where string is either 'next' or 'previous'.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["next", "previous"],
                "description": "Skip to next or previous track"
            }
        },
        "required": ["action"]
    }
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1])
                import asyncio
                result = asyncio.run(func(args))
                print(result)
            except Exception as e:
                print(json.dumps({"error": str(e)}))
