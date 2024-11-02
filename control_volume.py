import platform
import subprocess

# Global for platform
PLATFORM = platform.system().lower()

# Import platform-specific dependencies only if needed
if PLATFORM == "windows":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        
        # Initialize Windows audio devices once
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        VOLUME_INTERFACE = cast(interface, POINTER(IAudioEndpointVolume))
    except ImportError:
        print("Warning: For Windows volume control, install pycaw: pip install pycaw")
        VOLUME_INTERFACE = None

def run_script(args):
    """
    Controls system volume - can either set specific volume or adjust by relative amount
    """
    if 'set' in args:
        target = max(0, min(100, int(args['set'])))
        
        if PLATFORM == "darwin":
            subprocess.run(["osascript", "-e", f"set volume output volume {target}"])
            return f"Volume set to {target}%"
            
        elif PLATFORM == "linux":
            subprocess.run(["amixer", "-q", "sset", "Master", f"{target}%"])
            return f"Volume set to {target}%"
            
        elif PLATFORM == "windows":
            if VOLUME_INTERFACE:
                VOLUME_INTERFACE.SetMasterVolumeLevelScalar(target / 100.0, None)
                return f"Volume set to {target}%"
            return "Error: Windows volume control requires pycaw package"
                
        return f"Unsupported operating system: {PLATFORM}"
    
    elif 'adjust' in args:
        change = max(-100, min(100, int(args['adjust'])))
        
        if PLATFORM == "darwin":
            current = subprocess.getoutput("osascript -e 'output volume of (get volume settings)'")
            new_vol = max(0, min(100, int(current) + change))
            subprocess.run(["osascript", "-e", f"set volume output volume {new_vol}"])
            return f"Volume adjusted by {change}% to {new_vol}%"
            
        elif PLATFORM == "linux":
            sign = "+" if change > 0 else "-"
            subprocess.run(["amixer", "-q", "sset", "Master", f"{abs(change)}%{sign}"])
            return f"Volume adjusted by {change}%"
            
        elif PLATFORM == "windows":
            if VOLUME_INTERFACE:
                current_vol = VOLUME_INTERFACE.GetMasterVolumeLevelScalar()
                new_vol = max(0.0, min(1.0, current_vol + (change / 100.0)))
                VOLUME_INTERFACE.SetMasterVolumeLevelScalar(new_vol, None)
                return f"Volume adjusted by {change}% to {int(new_vol * 100)}%"
            return "Error: Windows volume control requires pycaw package"
                
        return f"Unsupported operating system: {PLATFORM}"
        
    return "Error: Please specify either 'set' or 'adjust' in the arguments"

# Function definition that matches the Groq interface
object = {
    "name": "control_volume",
    "description": f"Control system volume on {PLATFORM.capitalize()} by either setting it to a specific level or adjusting it relatively",
    "parameters": {
        "type": "object",
        "properties": {
            "set": {
                "type": "integer",
                "description": "Set volume to specific level (0-100)"
            },
            "adjust": {
                "type": "integer", 
                "description": "Adjust volume by relative amount (-100 to +100)"
            }
        },
        "oneOf": [
            {"required": ["set"]},
            {"required": ["adjust"]}
        ]
    }
}

# The function that will be called
func = run_script
