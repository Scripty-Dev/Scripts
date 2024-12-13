import sys
import json
import platform
import subprocess

PLATFORM = platform.system().lower()

if PLATFORM == "windows":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    VOLUME_INTERFACE = cast(interface, POINTER(IAudioEndpointVolume))

async def func(args):
    """
    Controls system volume - can either set specific volume or adjust by relative amount
    """
    try:
        if 'set' in args:
            target = max(0, min(100, int(args['set'])))
            
            if PLATFORM == "darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume {target}"])
                return json.dumps({"message": f"Volume set to {target}%"})
                
            elif PLATFORM == "linux":
                subprocess.run(["amixer", "-q", "sset", "Master", f"{target}%"])
                return json.dumps({"message": f"Volume set to {target}%"})
                
            elif PLATFORM == "windows":
                if VOLUME_INTERFACE:
                    VOLUME_INTERFACE.SetMasterVolumeLevelScalar(target / 100.0, None)
                    return json.dumps({"message": f"Volume set to {target}%"})
                return json.dumps({"error": "Windows volume control requires pycaw package"})
                    
            return json.dumps({"error": f"Unsupported operating system: {PLATFORM}"})
        
        elif 'adjust' in args:
            change = max(-100, min(100, int(args['adjust'])))
            
            if PLATFORM == "darwin":
                current = subprocess.getoutput("osascript -e 'output volume of (get volume settings)'")
                new_vol = max(0, min(100, int(current) + change))
                subprocess.run(["osascript", "-e", f"set volume output volume {new_vol}"])
                return json.dumps({"message": f"Volume adjusted by {change}% to {new_vol}%"})
                
            elif PLATFORM == "linux":
                sign = "+" if change > 0 else "-"
                subprocess.run(["amixer", "-q", "sset", "Master", f"{abs(change)}%{sign}"])
                return json.dumps({"message": f"Volume adjusted by {change}%"})
                
            elif PLATFORM == "windows":
                if VOLUME_INTERFACE:
                    current_vol = VOLUME_INTERFACE.GetMasterVolumeLevelScalar()
                    new_vol = max(0.0, min(1.0, current_vol + (change / 100.0)))
                    VOLUME_INTERFACE.SetMasterVolumeLevelScalar(new_vol, None)
                    return json.dumps({"message": f"Volume adjusted by {change}% to {int(new_vol * 100)}%"})
                return json.dumps({"error": "Windows volume control requires pycaw package"})
                    
            return json.dumps({"error": f"Unsupported operating system: {PLATFORM}"})
            
        return json.dumps({"error": "Please specify either 'set' or 'adjust' in the arguments"})
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "controlVolume",
    "description": f"Control system volume on {PLATFORM.capitalize()}. Required format: For setting volume use {{\"set\": number}} where number is 0-100, or for adjusting volume use {{\"adjust\": number}} where number is -100 to +100.",
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
