import sys
import json
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
import os

def get_config():
    # Determine appdata path based on platform
    if sys.platform == 'win32':
        appdata = os.getenv('APPDATA')
    elif sys.platform == 'darwin':
        appdata = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
    else:  # linux
        appdata = os.path.join(os.path.expanduser('~'), '.config')
    
    # Construct path to Scripty config
    config_path = os.path.join(appdata, 'Scripty', 'config.json')
    
    # Read and return config
    with open(config_path, 'r') as f:
        return json.load(f)

class SpotifyController:
    def __init__(self):
        """Initialize Spotify client with credentials from server"""
        try:
            config = get_config()
            # Pass token as URL parameter instead of JSON body
            creds_response = requests.post(
                f'https://scripty.me/api/assistant/spotify?token={config["token"]}',
                headers={'Content-Type': 'application/json'}
            )
            
            if creds_response.status_code != 200:
                raise Exception(f"Failed to get credentials: {creds_response.text}")
                
            creds = creds_response.json()
            
            # Create cache directory in user's home directory
            cache_dir = os.path.join(os.path.expanduser("~"), ".spotify-cache")
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
            cache_path = os.path.join(cache_dir, ".spotify_token_cache")

            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=creds['client_id'],
                client_secret=creds['client_secret'],
                redirect_uri=creds['redirect_uri'],
                scope='user-read-playback-state user-modify-playback-state user-read-currently-playing',
                cache_path=cache_path
            ))
        except Exception as e:
            raise Exception(f"Failed to initialize Spotify client: {str(e)}")

    def play_song(self, query):
        """Search and play a song"""
        try:
            results = self.sp.search(q=query, type='track', limit=5)
            
            if not results['tracks']['items']:
                return {
                    "error": f"No tracks found for: {query}",
                    "status": "error"
                }

            tracks = results['tracks']['items']
            tracks_info = []
            for i, track in enumerate(tracks, 1):
                tracks_info.append({
                    "position": i,
                    "name": track['name'],
                    "artist": track['artists'][0]['name'],
                    "album": track['album']['name'],
                    "duration": track['duration_ms'] // 1000,
                    "uri": track['uri']
                })

            # Get available devices
            devices = self.sp.devices()
            if not devices['devices']:
                return {
                    "error": "No active Spotify devices found",
                    "status": "error"
                }
            
            # Use the first available device
            device_id = devices['devices'][0]['id']
            
            self.sp.start_playback(device_id=device_id, uris=[tracks[0]['uri']])
            
            return {
                "message": f"Now playing: {tracks[0]['name']} by {tracks[0]['artists'][0]['name']}",
                "current_track": tracks_info[0],
                "other_matches": tracks_info[1:],
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

    def control_playback(self, action):
        """Control playback (pause/unpause/next/previous)"""
        try:
            # Get available devices first
            devices = self.sp.devices()
            if not devices['devices']:
                return {
                    "error": "No active Spotify devices found",
                    "status": "error"
                }
            
            device_id = devices['devices'][0]['id']
            
            if action == "pause":
                self.sp.pause_playback(device_id=device_id)
            elif action == "unpause":
                self.sp.start_playback(device_id=device_id)
            elif action == "next":
                self.sp.next_track(device_id=device_id)
            elif action == "previous":
                self.sp.previous_track(device_id=device_id)
            
            # Get current playback state
            current = self.sp.current_playback()
            if current and current['item']:
                return {
                    "message": f"Action '{action}' successful",
                    "now_playing": {
                        "name": current['item']['name'],
                        "artist": current['item']['artists'][0]['name'],
                        "album": current['item']['album']['name'],
                        "progress": current['progress_ms'] // 1000,
                        "duration": current['item']['duration_ms'] // 1000
                    },
                    "status": "success"
                }
            return {
                "message": f"Action '{action}' successful",
                "status": "success"
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }

async def func(args):
    """Main function to handle Spotify controls"""
    try:
        if 'action' in args:
            action = args['action'].lower()
            controller = SpotifyController()
            
            if action == "play" and "query" in args:
                result = controller.play_song(args["query"])
            elif action in ["pause", "unpause", "next", "previous"]:
                result = controller.control_playback(action)
            else:
                result = {
                    "error": "Invalid action. Use 'play' (with query), 'pause', 'unpause', 'next', or 'previous'",
                    "status": "error"
                }
            
            return json.dumps(result, indent=2)
            
        return json.dumps({
            "error": "Please specify 'action' in the arguments",
            "status": "error"
        })
    
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "status": "error"
        })

# Object definition for the assistant framework
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
