import sys
import json
import platform
import os
import shutil
from pathlib import Path

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

        # Ensure source and destination are absolute paths
        source = os.path.abspath(source)
        destination = os.path.abspath(destination)

        # Verify directories exist
        if not os.path.exists(source):
            return json.dumps({"error": f"Source directory does not exist: {source}"})
        if not os.path.exists(destination):
            return json.dumps({"error": f"Destination directory does not exist: {destination}"})

        if operation == "move":
            if filename:
                # Find file with any extension
                pattern = os.path.join(source, f"{filename}.*")
                matches = list(Path(source).glob(f"{filename}.*"))
                if not matches:
                    return json.dumps({"error": f"No file matching '{filename}' found in {source}"})
                source_path = str(matches[0])
            else:
                source_path = source

            # Move the file
            shutil.move(source_path, destination)

        elif operation == "latest":
            # Get all files in source directory with their timestamps
            files = [(f, os.path.getmtime(f)) for f in Path(source).iterdir() if f.is_file()]
            if not files:
                return json.dumps({"error": f"No files found in {source}"})
            
            # Sort by modification time and get the latest
            latest_file = max(files, key=lambda x: x[1])[0]
            
            # Move the file
            dest_path = os.path.join(destination, latest_file.name)
            shutil.move(str(latest_file), dest_path)
        else:
            return json.dumps({"error": "Invalid operation specified"})

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
