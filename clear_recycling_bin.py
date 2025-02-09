import json
import platform
import os
import ctypes
import asyncio

PLATFORM = platform.system().lower()

def get_recycle_bin_size():
    # Note: Without winshell, we can't get the exact count
    # but we can check if the operation was successful
    return None

async def func(args):
    try:
        print("\n=== Starting Recycle Bin Cleaner ===")
        
        if PLATFORM != "windows":
            error_msg = f"Unsupported platform: {PLATFORM}"
            print(f"Error: {error_msg}")
            return json.dumps({"error": "This script only works on Windows systems"})
        
        # Check if running with admin rights
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"Admin privileges: {'Yes' if is_admin else 'No'}")
        
        print("\nAttempting to clear recycle bin...")
        success = False
        
        try:
            # Use shell32 to empty the recycle bin
            result = ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
            if result == 0:  # 0 indicates success
                success = True
                message = "Recycle bin cleared successfully!"
            else:
                message = f"Failed to clear recycle bin. Error code: {result}"
            
        except Exception as e:
            message = f"Error clearing recycle bin: {str(e)}"
            
        print(f"\nResult: {message}")
        print("=== Operation Complete ===\n")
        
        return json.dumps({
            "message": message,
            "admin_rights": bool(is_admin),
            "success": success
        })
        
    except Exception as e:
        error_msg = f"Error in main function: {str(e)}"
        print(f"\nError: {error_msg}")
        return json.dumps({"error": str(e)})

object = {
    "name": "clearRecycleBin",
    "description": "Clears the Windows Recycle Bin without confirmation prompts. Creates a detailed log file in the same directory. Requires administrator privileges for best results.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}