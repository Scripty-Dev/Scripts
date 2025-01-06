import os
import subprocess
from typing import Dict, Any

def func(args: Dict[str, Any]) -> str:
    operation = args["operation"]
    from_path = args["from_path"]
    to_path = args.get("to_path", "")  # Optional for some operations
    
    # Convert paths to appropriate format based on OS
    from_path = os.path.expanduser(from_path)
    to_path = os.path.expanduser(to_path) if to_path else ""
    
    try:
        if operation == "move_latest":
            if os.name == 'nt':  # Windows
                command = f'move "{os.path.join(from_path, subprocess.check_output("dir /b /od", shell=True, text=True, cwd=from_path).strip().split()[-1])}" "{to_path}"'
            else:  # Unix/Linux/MacOS
                command = f'mv "$(ls -t "{from_path}" | head -n1)" "{to_path}"'
        elif operation == "copy":
            command = f'{"copy" if os.name == "nt" else "cp"} "{from_path}" "{to_path}"'
        elif operation == "unzip":
            command = f'{"tar -xf" if os.name == "nt" else "unzip"} "{from_path}" {"-C" if os.name == "nt" else "-d"} "{to_path}"'
            
        output = subprocess.check_output(command, shell=True, text=True)
        return f"{output}\nFile operation completed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error executing file operation: {str(e)}"

object = {
    "name": "file_ops",
    "description": """Handle file operations like moving, copying, and unzipping files.

This script ONLY handles file operations. Use this whenever the user wants to:
- Move files (especially "latest file" requests)
- Copy files
- Unzip archives

Examples:
"move latest file in downloads to business folder"
→ Use operation: "move_latest", from_path: "~/Downloads", to_path: "~/Documents/Business"

"unzip photos.zip to Pictures"
→ Use operation: "unzip", from_path: "~/photos.zip", to_path: "~/Pictures"

"copy document.txt to Desktop"
→ Use operation: "copy", from_path: "~/document.txt", to_path: "~/Desktop"

The script will automatically handle OS-specific commands.""",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["move_latest", "copy", "unzip"],
                "description": "The type of file operation to perform"
            },
            "from_path": {
                "type": "string",
                "description": "Source path (use ~ for home directory)"
            },
            "to_path": {
                "type": "string",
                "description": "Destination path (use ~ for home directory)"
            }
        },
        "required": ["operation", "from_path", "to_path"]
    }
}
