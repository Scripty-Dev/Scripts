import sys
import json
import platform
import os
import subprocess

PLATFORM = platform.system().lower()

async def func(args):
    """
    Handle file operations like moving, copying, and unzipping files
    """
    try:
        operation = args.get("operation")
        from_path = os.path.expanduser(args.get("from_path", ""))
        to_path = os.path.expanduser(args.get("to_path", ""))

        if operation == "move_latest":
            if PLATFORM == "windows":
                cmd = f'move "{os.path.join(from_path, subprocess.check_output("dir /b /od", shell=True, text=True, cwd=from_path).strip().split()[-1])}" "{to_path}"'
            else:
                cmd = f'mv "$(ls -t "{from_path}" | head -n1)" "{to_path}"'
        elif operation == "copy":
            cmd = f'{"copy" if PLATFORM == "windows" else "cp"} "{from_path}" "{to_path}"'
        elif operation == "unzip":
            cmd = f'{"tar -xf" if PLATFORM == "windows" else "unzip"} "{from_path}" {"-C" if PLATFORM == "windows" else "-d"} "{to_path}"'
        else:
            return json.dumps({"error": "Invalid operation specified"})

        subprocess.run(cmd, shell=True, check=True)
        return json.dumps({"message": f"File operation {operation} completed successfully"})
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "file_ops",
    "description": """Handle file operations like moving, copying, and unzipping files.

This script handles file operations like moving the latest file, copying files, or unzipping archives.

Examples:
"move the latest file in downloads to business folder"
→ {"operation": "move_latest", "from_path": "~/Downloads", "to_path": "~/Documents/Business"}

"unzip photos.zip to Pictures"
→ {"operation": "unzip", "from_path": "~/photos.zip", "to_path": "~/Pictures"}""",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["move_latest", "copy", "unzip"],
                "description": "Type of file operation to perform"
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
