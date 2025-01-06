import os
import subprocess
from typing import Dict, Any

def func(args: Dict[str, Any]) -> str:
    command = args["command"]
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return f"{output}\nCommand executed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {str(e)}"

object = {
    "name": "command",
    "description": """Run system commands in the terminal.

IMPORTANT: This script handles file and system operations. When users mention file operations like moving, copying, or unzipping files, use THIS script, not the convert script.

Key triggers that mean you should use this script:
- Any mention of moving files, folders, directories
- Words like "move", "copy", "unzip", "latest file"
- Any references to specific folders like "downloads", "documents", etc.
- Any request to manipulate files or directories

Check the operating system (provided in your system prompt) and use appropriate commands:

Windows examples:
"move latest file in downloads to business folder" →
"move %USERPROFILE%\\Downloads\\$(dir /b /od %USERPROFILE%\\Downloads | findstr /v /i \"desktop.ini\" | tail -1) %USERPROFILE%\\Documents\\Business"

Unix/Linux/MacOS examples:
"move latest file in downloads to business folder" →
"mv $(ls -t ~/Downloads | head -n1) ~/Documents/Business"

"copy photos to Desktop" →
"cp ~/photos/* ~/Desktop"

This is a FILE OPERATION script - do not use it for unit conversions or calculations.
If the user mentions moving, copying, or managing files/folders, use THIS script.""",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The system command to execute"
            }
        },
        "required": ["command"]
    }
}
