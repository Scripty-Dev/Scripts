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

        home = Path.home()
        common_paths = {
            'downloads': [home / 'Downloads', home / 'Download'],
            'documents': [home / 'Documents', home / 'Docs'],
            'desktop': [home / 'Desktop'],
            'pictures': [home / 'Pictures', home / 'Photos'],
            'videos': [home / 'Videos', home / 'Movies'],
        }

        def resolve_path(path_str: str) -> str:
            if not path_str:
                return ""
                
            # Direct path check
            if path_str.startswith("~"):
                expanded = os.path.expanduser(path_str)
                if os.path.exists(expanded):
                    return expanded
                    
            # Check common paths
            path_lower = path_str.lower().strip()
            for dir_type, paths in common_paths.items():
                if dir_type in path_lower:
                    for path in paths:
                        if path.exists():
                            return str(path)
                            
            # Fall back to original with home expansion
            return os.path.abspath(os.path.expanduser(path_str))

        # Resolve paths
        source = resolve_path(source)
        destination = resolve_path(destination)

        # Verify paths exist
        if not os.path.exists(source):
            return json.dumps({"error": f"Source not found: {source}"})
        if not os.path.exists(destination):
            return json.dumps({"error": f"Destination not found: {destination}"})

        if operation == "move":
            if filename:
                matches = list(Path(source).glob(f"{filename}*"))
                if not matches:
                    return json.dumps({"error": f"No file matching '{filename}' found"})
                source_path = str(matches[0])
                dest_path = os.path.join(destination, matches[0].name)
            else:
                source_path = source
                dest_path = destination

            shutil.move(source_path, dest_path)

        elif operation == "latest":
            files = [(f, os.path.getmtime(f)) for f in Path(source).iterdir() if f.is_file()]
            if not files:
                return json.dumps({"error": f"No files found in {source}"})
            
            latest_file = max(files, key=lambda x: x[1])[0]
            dest_path = os.path.join(destination, latest_file.name)
            shutil.move(str(latest_file), dest_path)
        else:
            return json.dumps({"error": "Invalid operation"})

        return json.dumps({"message": f"File operation {operation} completed successfully"})
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "file_ops",
    "description": """Enhanced file operations with smart path resolution.

Examples:
"move report from downloads to documents"
→ {"operation": "move", "source": "downloads", "destination": "documents", "filename": "report"}

"move latest download to Documents"
→ {"operation": "latest", "source": "downloads", "destination": "documents"}

The script handles common paths like downloads, documents, desktop, etc.""",
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
                "description": "Source path or common directory name"
            },
            "destination": {
                "type": "string", 
                "description": "Destination path or common directory name"
            },
            "filename": {
                "type": "string",
                "description": "Filename without extension (optional)"
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
