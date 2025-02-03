import json
import platform
import winshell
import win32com.client
import logging
from datetime import datetime
import os
import ctypes
import asyncio  # Added for async support

PLATFORM = platform.system().lower()

# Set up logging
logging.basicConfig(
    filename=f'recycle_bin_clear_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_recycle_bin_size():
    try:
        return len(list(winshell.recycle_bin()))
    except Exception as e:
        logging.error(f"Failed to get recycle bin size: {str(e)}")
        print(f"Error checking recycle bin size: {str(e)}")
        return None

async def func(args):
    try:
        print("\n=== Starting Recycle Bin Cleaner ===")
        logging.info("Starting recycle bin clearing script")
        
        # Handle path if provided in args
        if 'source' in args:
            # Convert Unix-style path to Windows path
            source_path = args['source'].replace('~', os.path.expanduser('~'))
            source_path = source_path.replace('/', '\\')
            logging.info(f"Converted source path: {source_path}")
        
        # Check if running with admin rights
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        print(f"Admin privileges: {'Yes' if is_admin else 'No'}")
        logging.info(f"Running with admin privileges: {bool(is_admin)}")
        
        if PLATFORM != "windows":
            error_msg = f"Unsupported platform: {PLATFORM}"
            print(f"Error: {error_msg}")
            logging.error(error_msg)
            return json.dumps({"error": "This script only works on Windows systems"})
        
        # Check initial recycle bin state
        print("\nChecking initial recycle bin state...")
        initial_items = get_recycle_bin_size()
        print(f"Items in recycle bin: {initial_items}")
        logging.info(f"Initial items in recycle bin: {initial_items}")
        
        if initial_items == 0:
            print("Recycle bin is already empty!")
            return json.dumps({"message": "Recycle bin is already empty"})
        
        print("\nAttempting to clear recycle bin...")
        success = False
        
        try:
            # Try the first method (winshell)
            print("Method 1: Using winshell...")
            logging.info("Attempting to clear recycle bin using winshell")
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            print("Winshell method completed")
            success = True
        except Exception as e:
            print(f"Winshell method failed: {str(e)}")
            logging.error(f"winshell method failed: {str(e)}")
            
            # Try alternative method using shell32
            print("\nMethod 2: Using shell32...")
            logging.info("Attempting alternative clear method using shell32")
            try:
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
                print("Shell32 method completed")
                success = True
            except Exception as e2:
                print(f"Shell32 method failed: {str(e2)}")
                logging.error(f"shell32 method failed: {str(e2)}")
        
        # Verify the recycle bin is empty
        print("\nVerifying results...")
        final_items = get_recycle_bin_size()
        print(f"Items remaining in recycle bin: {final_items}")
        logging.info(f"Final items in recycle bin: {final_items}")
        
        if final_items == 0:
            message = "Recycle bin cleared successfully!"
        else:
            message = f"Warning: Recycle bin still contains {final_items} items"
            
        print(f"\nResult: {message}")
        print("=== Operation Complete ===\n")
        
        logging.info(message)
        return json.dumps({
            "message": message,
            "initial_items": initial_items,
            "final_items": final_items,
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

modules = ['winshell', 'pywin32']