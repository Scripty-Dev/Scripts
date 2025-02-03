import json
import platform
import logging
from datetime import datetime
import os
import ctypes
import asyncio

PLATFORM = platform.system().lower()

# Set up logging
logging.basicConfig(
    filename=f'recycle_bin_clear_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_recycle_bin_size():
    # Note: Without winshell, we can't get the exact count
    # but we can check if the operation was successful
    return None

async def func(args):
    try:
        print("\n=== Starting Recycle Bin Cleaner ===")
        logging.info("Starting recycle bin clearing script")
        
        if PLATFORM != "windows":
            error_msg = f"Unsupported platform: {PLATFORM}"
            print(f"Error: {error_msg}")
            logging.error(error_msg)
            return json.dumps({"error": "This script only works on Windows systems"})
        
        # Check if running with admin rights
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"Admin privileges: {'Yes' if is_admin else 'No'}")
        logging.info(f"Running with admin privileges: {bool(is_admin)}")
        
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
            logging.error(message)
            
        print(f"\nResult: {message}")
        print("=== Operation Complete ===\n")
        
        logging.info(message)
        return json.dumps({
            "message": message,
            "admin_rights": bool(is_admin),
            "success": success
        })
        
    except Exception as e:
        error_msg = f"Error in main function: {str(e)}"
        print(f"\nError: {error_msg}")
        logging.error(error_msg, exc_info=True)
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

modules = []  # No external modules required