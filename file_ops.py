import sys
import json
import platform
import os
import shutil
from pathlib import Path

PLATFORM = platform.system().lower()

async def func(args):
    """Handle file operations with smart path resolution"""
    try:
        operation = args.get("operation")
        source = args.get("source", "")
        destination = args.get("destination", "")
        filename = args.get("filename", "")
        
        # Resolve home directory paths
        source = os.path.expanduser(source)
        destination = os.path.expanduser(destination)
        
        # Verify paths exist
        if not os.path.exists(source):
            return json.dumps({"error": f"Source not found: {source}"})
        if not os.path.exists(destination):
            return json.dumps({"error": f"Destination not found: {destination}"})

        if operation == "move":
            if filename:
                # Find file with any extension
                matches = list(Path(source).glob(f"{filename}*"))
                if not matches:
                    return json.dumps({"error": f"No file matching '{filename}' found"})
                
                src_file = matches[0]
                dst_file = Path(destination) / src_file.name
                
                try:
                    # Ensure source exists and is a file
                    if not src_file.is_file():
                        return json.dumps({"error": "Source is not a file"})
                    
                    # Create destination directory if needed
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the file
                    os.replace(str(src_file), str(dst_file))
                    
                    # Verify move was successful
                    if not dst_file.exists():
                        return json.dumps({"error": "Move operation failed"})
                        
                except PermissionError:
                    return json.dumps({"error": "Permission denied"})
                except Exception as e:
                    return json.dumps({"error": f"Move failed: {str(e)}"})

            else:
                return json.dumps({"error": "Filename required for move operation"})

        elif operation == "latest":
            try:
                files = [(f, os.path.getmtime(f)) for f in Path(source).iterdir() if f.is_file()]
                if not files:
                    return json.dumps({"error": f"No files found in {source}"})
                
                latest = max(files, key=lambda x: x[1])[0]
                dst_file = Path(destination) / latest.name
                
                os.replace(str(latest), str(dst_file))
                
                if not dst_file.exists():
                    return json.dumps({"error": "Move operation failed"})
                    
            except Exception as e:
                return json.dumps({"error": f"Latest operation failed: {str(e)}"})
        else:
            return json.dumps({"error": "Invalid operation"})

        return json.dumps({"message": "File operation completed successfully"})
        
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "file_ops",
    "description": """Handle file operations with smart path resolution.

Examples:
"move report from downloads to documents"
→ {"operation": "move", "source": "~/Downloads", "destination": "~/Documents", "filename": "report"}

"move latest download to Documents"
→ {"operation": "latest", "source": "~/Downloads", "destination": "~/Documents"}""",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["move", "latest"],
                "description": "Type of file operation"
            },
            "source": {
                "type": "string",
                "description": "Source path (use ~ for home directory)"
            },
            "destination": {
                "type": "string", 
                "description": "Destination path (use ~ for home directory)"
            },
            "filename": {
                "type": "string",
                "description": "Filename without extension (optional)"
            }
        },
        "required": ["operation", "source", "destination"]
    }
}