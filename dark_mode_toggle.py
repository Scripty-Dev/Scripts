import sys
import json
import platform
from typing import Optional

PLATFORM = platform.system().lower()

class DarkModeController:
    def __init__(self):
        """Platform-specific initialization of dark mode controller"""
        platform = sys.platform
        if platform == 'win32':
            import winreg
            self._reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                         "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                                         0, winreg.KEY_ALL_ACCESS)
        elif platform == 'darwin':
            import platform
            if int(platform.mac_ver()[0].split('.')[0]) < 10:
                raise Exception("macOS version not supported")
            import subprocess
            self._osascript = subprocess.run
            
    def toggle_dark_mode(self) -> bool:
        """Toggle system dark mode and return success state"""
        current = self.get_dark_mode_state()
        if current is None:
            return False
        return self._set_dark_mode(not current)
        
    def get_dark_mode_state(self) -> Optional[bool]:
        """Get current dark mode state. Returns None if couldn't detect."""
        platform = sys.platform
        try:
            if platform == 'win32':
                import winreg
                value = winreg.QueryValueEx(self._reg_key, "AppsUseDarkTheme")[0]
                return bool(value)
            elif platform == 'darwin':
                result = self._osascript(['osascript', '-e', 
                    'tell application "System Events" to tell appearance preferences to get dark mode'])
                return result.stdout.strip() == 'true'
            elif platform == 'linux':
                import subprocess
                desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                if 'gnome' in desktop:
                    result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                                         capture_output=True, text=True)
                    return 'dark' in result.stdout.lower()
                elif 'kde' in desktop:
                    result = subprocess.run(['kreadconfig5', '--group', 'General', '--key', 'ColorScheme'],
                                         capture_output=True, text=True)
                    return 'dark' in result.stdout.lower()
                elif 'xfce' in desktop:
                    result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'],
                                         capture_output=True, text=True)
                    return 'dark' in result.stdout.lower()
        except Exception as e:
            print(f"Error getting dark mode state: {e}")
        return None
        
    def _set_dark_mode(self, enable: bool) -> bool:
        """Set system dark mode state. Returns success state."""
        platform = sys.platform
        try:
            if platform == 'win32':
                import winreg
                winreg.SetValueEx(self._reg_key, "AppsUseDarkTheme", 0, winreg.REG_DWORD, enable)
                return True
            elif platform == 'darwin':
                result = self._osascript(['osascript', '-e',
                    f'tell application "System Events" to tell appearance preferences to set dark mode to {str(enable).lower()}'])
                return result.returncode == 0
            elif platform == 'linux':
                import subprocess
                desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                if 'gnome' in desktop:
                    theme = 'Adwaita-dark' if enable else 'Adwaita'
                    result = subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', theme])
                    return result.returncode == 0
                elif 'kde' in desktop:
                    theme = 'BreezeDark' if enable else 'Breeze'
                    result = subprocess.run(['plasma-apply-colorscheme', theme])
                    return result.returncode == 0
                elif 'xfce' in desktop:
                    theme = 'Adwaita-dark' if enable else 'Adwaita'
                    result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName', '-s', theme])
                    return result.returncode == 0
        except Exception as e:
            print(f"Error setting dark mode: {e}")
        return False

async def func(args):
    """Handle dark mode toggle commands"""
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
    "name": "dark_mode_toggle",
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

modules = ['winreg'] if PLATFORM == "windows" else []