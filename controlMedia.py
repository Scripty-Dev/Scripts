import sys
import json
import platform
import keyboard
import psutil
from time import sleep
import subprocess

# Global for platform
PLATFORM = platform.system().lower()

def get_active_media_player():
    """
    Detects which media player is currently running
    Returns: string - name of media player or None
    """
    media_players = {
        'spotify': 'Spotify',
        'music.ui': 'Apple Music',
        'vlc': 'VLC',
        'windowsmediaplayer': 'Windows Media Player',
        'wmplayer': 'Windows Media Player',
        'itunes': 'iTunes',
        'groove': 'Groove Music'
    }
    
    for proc in psutil.process_iter(['name']):
        try:
            process_name = proc.info['name'].lower()
            for player_process, player_name in media_players.items():
                if player_process in process_name:
                    return player_name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def focus_window(player_name):
    """
    Attempts to focus the media player window
    """
    if PLATFORM == 'windows':
        try:
            subprocess.run(['powershell', '-Command', f'(New-Object -ComObject WScript.Shell).AppActivate("{player_name}")'])
            return True
        except:
            return False
    elif PLATFORM == 'darwin':  # macOS
        try:
            subprocess.run(['osascript', '-e', f'tell application "{player_name}" to activate'])
            return True
        except:
            return False
    elif PLATFORM == 'linux':
        try:
            subprocess.run(['wmctrl', '-a', player_name])
            return True
        except:
            return False
    return False

async def play_song(query):
    """
    Attempts to play a song using the active media player's search functionality
    """
    try:
        # Detect active media player
        player = get_active_media_player()
        if not player:
            return json.dumps({
                "error": "No active media player detected",
                "status": "error"
            })

        # Focus the media player window
        if not focus_window(player):
            return json.dumps({
                "error": f"Could not focus {player} window",
                "status": "error"
            })

        sleep(0.5)  # Wait for window to focus

        # Simulate search shortcut based on player
        if player == "Spotify":
            # Ctrl+L for search in Spotify
            keyboard.press('ctrl+l')
            sleep(0.2)
            keyboard.write(query)
            sleep(0.2)
            keyboard.press('enter')
            sleep(0.5)
            keyboard.press('enter')  # Select first result
        
        elif player in ["iTunes", "Apple Music"]:
            # Cmd+F or Ctrl+F for search
            if PLATFORM == 'darwin':
                keyboard.press('command+f')
            else:
                keyboard.press('ctrl+f')
            sleep(0.2)
            keyboard.write(query)
            sleep(0.2)
            keyboard.press('enter')
        
        else:
            # Generic approach for other players
            # Many use Ctrl+F or Cmd+F for search
            if PLATFORM == 'darwin':
                keyboard.press('command+f')
            else:
                keyboard.press('ctrl+f')
            sleep(0.2)
            keyboard.write(query)
            sleep(0.2)
            keyboard.press('enter')

        return json.dumps({
            "message": f"Attempting to play '{query}' on {player}",
            "player": player,
            "status": "success"
        })

    except Exception as e:
        return json.dumps({
            "error": f"Failed to play song: {str(e)}",
            "status": "error"
        })

async def func(args):
    """
    Controls media playback - supports playing specific songs and basic media controls
    """
    try:
        if 'action' in args:
            action = args['action'].lower()
            
            # Define keyboard shortcuts based on platform
            if PLATFORM == 'windows':
                CONTROLS = {
                    "play": "play/pause media",
                    "next": "next track",
                    "previous": "previous track",
                    "stop": "stop media",
                }
            elif PLATFORM == 'darwin':  # macOS
                CONTROLS = {
                    "play": "play/pause",
                    "next": "fastforward",
                    "previous": "rewind",
                    "stop": "stop",
                }
            else:  # linux
                CONTROLS = {
                    "play": "play/pause",
                    "next": "next",
                    "previous": "previous",
                    "stop": "stop",
                }

            # Handle playing specific song
            if action == "play" and "query" in args:
                return await play_song(args["query"])

            # Handle basic media controls
            elif action in CONTROLS:
                keyboard.send(CONTROLS[action])
                return json.dumps({
                    "message": f"Successfully executed {action} command",
                    "status": "success"
                })
            
            return json.dumps({
                "error": "Invalid action. Available actions: play (with query), stop, next, previous",
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

# Updated object definition
object = {
    "name": "controlMedia",
    "description": f"Control media playback on {PLATFORM.capitalize()}. Required format: {{\"action\": string, \"query\": string}} where action is one of the available commands and query is the song to play.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["play", "stop", "next", "previous"],
                "description": "Control media playback"
            },
            "query": {
                "type": "string",
                "description": "Song title or search query (required when action is 'play')"
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
