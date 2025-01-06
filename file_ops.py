import sys
import json
import platform
import os
import subprocess
from pathlib import Path
import glob

PLATFORM = platform.system().lower()

async def func(args):
    """
    Handle file operations like moving or copying files
    """
    try:
        operation = args.get("operation")
        source = os.path.expanduser(args.get("source", ""))
        destination = os.path.expanduser(args.get("destination", ""))
        filename = args.get("filename", "")

        # If a filename is provided, find its full name with extension
        if filename:
            pattern = os.path.join(source, f"{filename}.*")
            matches = glob.glob(pattern)
            if matches:
                # Use the first match if multiple exist
                source_path = matches[0]
            else:
                return json.dumps({"error": f"No file matching '{filename}' found in {source}"})
        else:
            source_path = source

        # Handle different operations
        if operation == "move":
            if PLATFORM == "windows":
                cmd = f'move "{source_path}" "{destination}"'
            else:
                cmd = f'mv "{source_path}" "{destination}"'
        elif operation == "latest":
            if PLATFORM == "windows":
                cmd = f'move "{os.path.join(source, subprocess.check_output("dir /b /od", shell=True, text=True, cwd=source).strip().split()[-1])}" "{destination}"'
            else:
                cmd = f'mv "$(ls -t "{source}" | head -n1)" "{destination}"'
        else:
            return json.dumps({"error": "Invalid operation specified"})

        subprocess.run(cmd, shell=True, check=True)
        return json.dumps({"message": f"File operation {operation} completed successfully"})
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "file_ops",
    "description": """Handle file operations like moving or copying files.

Examples:
"move BlackGuySquinting from Downloads to Reels"
→ {"operation": "move", "source": "~/Downloads", "destination": "~/Reels", "filename": "BlackGuySquinting"}

"move latest download to Documents"
→ {"operation": "latest", "source": "~/Downloads", "destination": "~/Documents"}

The script will automatically find the correct file regardless of its extension.""",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["move", "latest"],
                "description": "Type of file operation to perform"
            },
            "source": {
                "type": "string",
                "description": "Source directory path (use ~ for home directory)"
            },
            "destination": {
                "type": "string",
                "description": "Destination directory path (use ~ for home directory)"
            },
            "filename": {
                "type": "string",
                "description": "Name of the file without extension (optional)"
            }
        },
        "required": ["operation", "source", "destination"]
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
