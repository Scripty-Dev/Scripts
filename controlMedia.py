import sys
import json
import keyboard
import psutil
from time import sleep
import pyautogui

def is_spotify_running():
    """Check if Spotify is running"""
    for proc in psutil.process_iter(['name']):
        try:
            if 'spotify' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

async def play_song(query):
    """
    Search and play a specific song on Spotify
    """
    try:
        if not is_spotify_running():
            return json.dumps({
                "error": "Spotify is not running. Please open Spotify first.",
                "status": "error"
            })

        # Focus on search
        keyboard.press_and_release('ctrl+l')  # This focuses Spotify's search bar
        sleep(0.5)
        
        # Clear any existing search
        keyboard.press_and_release('ctrl+a')  # Select all
        sleep(0.1)
        keyboard.press_and_release('backspace')  # Clear selection
        sleep(0.1)
        
        # Type the search query
        keyboard.write(query)
        sleep(1)  # Wait for search results
        
        # Select and play first result
        keyboard.press_and_release('enter')
        sleep(0.5)
        keyboard.press_and_release('enter')  # Second enter to play the top result

        return json.dumps({
            "message": f"Playing: {query}",
            "status": "success"
        })

    except Exception as e:
        return json.dumps({
            "error": f"Failed to play song: {str(e)}",
            "status": "error"
        })

async def func(args):
    """
    Main function to handle media controls
    """
    try:
        if 'action' in args:
            action = args['action'].lower()
            
            # Handle playing specific song
            if action == "play" and "query" in args:
                return await play_song(args["query"])
            
            # Handle basic media controls
            elif action == "next":
                keyboard.send('next track')
                return json.dumps({
                    "message": "Skipped to next track",
                    "status": "success"
                })
            elif action == "previous":
                keyboard.send('previous track')
                return json.dumps({
                    "message": "Skipped to previous track",
                    "status": "success"
                })
            elif action == "pause" or action == "unpause":
                keyboard.send('play/pause media')
                return json.dumps({
                    "message": f"Toggled play/pause",
                    "status": "success"
                })
            
            return json.dumps({
                "error": "Invalid action. Use 'play' (with query), 'pause', 'unpause', 'next', or 'previous'",
                "status": "error"
            })
            
        return json.dumps({
            "error": "Please specify 'action' in the arguments",
            "status": "error"
        })
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })

# Object definition
object = {
    "name": "spotifyControl",
    "description": "Control Spotify playback. Format: {\"action\": string, \"query\": string (required for play)} where action is play/pause/unpause/next/previous",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["play", "pause", "unpause", "next", "previous"],
                "description": "Control action to perform"
            },
            "query": {
                "type": "string",
                "description": "Song to play (required when action is 'play')"
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
                print(json.dumps({
                    "error": str(e),
                    "status": "error"
                }))
