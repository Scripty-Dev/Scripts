import platform
import subprocess
import sys
import winreg
import os
from typing import Optional, Tuple

class DarkModeController:
    def __init__(self):
        self.os_name = platform.system().lower()
        
    def toggle_dark_mode(self) -> bool:
        """
        Toggle system-wide dark mode (switches to opposite of current state)
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            is_dark = self.get_dark_mode_state()
            if is_dark is None:  # Couldn't detect current state
                return False
                
            # Toggle to opposite of current state
            return self._set_dark_mode(not is_dark)
            
        except Exception as e:
            print(f"Error toggling dark mode: {e}")
            return False

    def get_dark_mode_state(self) -> Optional[bool]:
        """
        Get current dark mode state
        Returns:
            Optional[bool]: True if dark mode is on, False if off, None if couldn't detect
        """
        if self.os_name == 'windows':
            return self._get_windows_dark_mode()
        elif self.os_name == 'darwin':
            return self._get_macos_dark_mode()
        elif self.os_name == 'linux':
            return self._get_linux_dark_mode()
        else:
            print(f"Unsupported operating system: {self.os_name}")
            return None

    def _set_dark_mode(self, enable: bool) -> bool:
        """Internal method to set dark mode state"""
        if self.os_name == 'windows':
            return self._set_windows_dark_mode(enable)
        elif self.os_name == 'darwin':
            return self._set_macos_dark_mode(enable)
        elif self.os_name == 'linux':
            return self._set_linux_dark_mode(enable)
        return False

    def _get_windows_dark_mode(self) -> Optional[bool]:
        try:
            path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, 
                                   winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(reg_key, "AppsUseLightTheme")
            winreg.CloseKey(reg_key)
            return value == 0  # 0 means dark mode is on
        except Exception as e:
            print(f"Error reading Windows dark mode state: {e}")
            return None

    def _set_windows_dark_mode(self, enable: bool) -> bool:
        try:
            path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, 
                                   winreg.KEY_ALL_ACCESS)
            
            # Set value (0 for dark mode, 1 for light mode)
            winreg.SetValueEx(reg_key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 
                            0 if enable else 1)
            winreg.SetValueEx(reg_key, "SystemUsesLightTheme", 0, 
                            winreg.REG_DWORD, 0 if enable else 1)
            
            winreg.CloseKey(reg_key)
            return True
        except Exception as e:
            print(f"Error setting Windows dark mode: {e}")
            return False

    def _get_macos_dark_mode(self) -> Optional[bool]:
        try:
            cmd = '''
            tell application "System Events"
                tell appearance preferences
                    return dark mode
                end tell
            end tell
            '''
            result = subprocess.run(['osascript', '-e', cmd], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip().lower() == 'true'
        except Exception as e:
            print(f"Error reading macOS dark mode state: {e}")
            return None

    def _set_macos_dark_mode(self, enable: bool) -> bool:
        try:
            cmd = f'''
            tell application "System Events"
                tell appearance preferences
                    set dark mode to {str(enable).lower()}
                end tell
            end tell
            '''
            subprocess.run(['osascript', '-e', cmd], check=True)
            return True
        except Exception as e:
            print(f"Error setting macOS dark mode: {e}")
            return False

    def _get_linux_dark_mode(self) -> Optional[bool]:
        try:
            if self._is_gnome():
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                    capture_output=True, text=True, check=True
                )
                return 'prefer-dark' in result.stdout.lower()
                
            elif self._is_kde():
                result = subprocess.run(
                    ['plasma-apply-colorscheme', '--current'],
                    capture_output=True, text=True, check=True
                )
                return 'dark' in result.stdout.lower()
                
            elif self._is_xfce():
                result = subprocess.run(
                    ['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'],
                    capture_output=True, text=True, check=True
                )
                return 'dark' in result.stdout.lower()
                
            else:
                print("Unsupported Linux desktop environment")
                return None
                
        except Exception as e:
            print(f"Error reading Linux dark mode state: {e}")
            return None

    def _set_linux_dark_mode(self, enable: bool) -> bool:
        try:
            if self._is_gnome():
                theme = "prefer-dark" if enable else "prefer-light"
                subprocess.run([
                    'gsettings', 'set', 
                    'org.gnome.desktop.interface', 'color-scheme',
                    theme
                ], check=True)
                return True
                
            elif self._is_kde():
                theme = "BreezeDark" if enable else "BreezeLight"
                subprocess.run([
                    'plasma-apply-colorscheme', theme
                ], check=True)
                return True
                
            elif self._is_xfce():
                theme = "Adwaita-dark" if enable else "Adwaita"
                subprocess.run([
                    'xfconf-query', '-c', 'xsettings', 
                    '-p', '/Net/ThemeName', '-s', theme
                ], check=True)
                return True
                
            else:
                print("Unsupported Linux desktop environment")
                return False
                
        except Exception as e:
            print(f"Error setting Linux dark mode: {e}")
            return False

    def _is_gnome(self) -> bool:
        return os.environ.get('DESKTOP_SESSION', '').lower().find('gnome') != -1

    def _is_kde(self) -> bool:
        return os.environ.get('DESKTOP_SESSION', '').lower().find('plasma') != -1

    def _is_xfce(self) -> bool:
        return os.environ.get('DESKTOP_SESSION', '').lower().find('xfce') != -1

def main():
    controller = DarkModeController()
    
    # Get current state
    current_state = controller.get_dark_mode_state()
    if current_state is None:
        print("Could not detect current dark mode state")
        return
        
    # Toggle dark mode
    success = controller.toggle_dark_mode()
    if success:
        new_state = "enabled" if not current_state else "disabled"
        print(f"Successfully {new_state} dark mode")
    else:
        print("Failed to toggle dark mode")

if __name__ == "__main__":
    main()