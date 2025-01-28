import sys
import json
from typing import Optional
from darkmode import DarkModeController  # Assuming the class is in darkmode.py

async def func(args):
    try:
        controller = DarkModeController()
        action = args.get('action', 'toggle')
        
        if action == 'toggle':
            success = controller.toggle_dark_mode()
            new_state = controller.get_dark_mode_state()
            if success:
                return json.dumps({
                    "message": f"Dark mode {'enabled' if new_state else 'disabled'}",
                    "state": new_state
                })
            return json.dumps({"error": "Failed to toggle dark mode"})
            
        elif action == 'get':
            state = controller.get_dark_mode_state()
            if state is not None:
                return json.dumps({
                    "message": f"Dark mode is {'enabled' if state else 'disabled'}",
                    "state": state
                })
            return json.dumps({"error": "Could not detect dark mode state"})
            
        elif action == 'set':
            enable = args.get('enable')
            if enable is None:
                return json.dumps({"error": "enable parameter required for set action"})
                
            success = controller._set_dark_mode(enable)
            if success:
                return json.dumps({
                    "message": f"Dark mode {'enabled' if enable else 'disabled'}",
                    "state": enable
                })
            return json.dumps({"error": f"Failed to {'enable' if enable else 'disable'} dark mode"})
            
        else:
            return json.dumps({"error": f"Invalid action: {action}"})
            
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

object = {
    "name": "darkMode",
    "description": "Control system-wide dark mode settings. Supports Windows, macOS, and Linux (GNOME, KDE, XFCE).",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["toggle", "get", "set"],
                "description": "Action to perform (toggle, get current state, or set specific state)",
                "default": "toggle"
            },
            "enable": {
                "type": "boolean",
                "description": "Boolean state for set action (true=dark mode, false=light mode)"
            }
        }
    }
}

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--get-exports':
            print(json.dumps({"object": object}))
        else:
            try:
                args = json.loads(sys.argv[1].replace("'", '"'))
                import asyncio
                result = asyncio.run(func(args))
                print(result)
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"JSON Error: {str(e)}"}))
            except Exception as e:
                print(json.dumps({"error": f"Error: {str(e)}"}))
