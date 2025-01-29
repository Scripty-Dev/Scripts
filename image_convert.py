import sys
import json
import os
from PIL import Image
import glob

SUPPORTED_FORMATS = {
    'PNG': 'PNG',
    'JPG': 'JPEG', 
    'JPEG': 'JPEG',
    'WEBP': 'WEBP',
    'GIF': 'GIF'
}

def validate_format(format_str):
    if not format_str:
        return 'PNG'
    format_upper = format_str.upper()
    if format_upper not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {format_str}. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}")
    return SUPPORTED_FORMATS[format_upper]

def find_single_file(filename):
    search_paths = [
        os.getcwd(),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Pictures"),
        os.path.expanduser("~/Documents")
    ]
    
    for path in search_paths:
        try:
            for root, _, files in os.walk(path):
                if filename in files:
                    return [os.path.join(root, filename)]
        except Exception:
            continue
    return []

def find_batch_files(folder_path, pattern):
    try:
        full_pattern = os.path.join(folder_path, pattern)
        return glob.glob(full_pattern)
    except Exception as e:
        raise ValueError(f"Error searching folder {folder_path}: {str(e)}")

def cleanup_files(files):
    for file in files:
        try:
            os.remove(file)
        except Exception as e:
            print(f"Failed to remove {file}: {str(e)}")

async def func(args):
    try:
        filename = args.get('filename')
        if not filename:
            return json.dumps({"error": "No filename provided"})

        try:
            output_format = validate_format(args.get('format'))
        except ValueError as e:
            return json.dumps({"error": str(e)})
        
        # Handle batch conversion
        if args.get('batch'):
            folder_path = args.get('folder')
            if not folder_path:
                return json.dumps({"error": "Folder path required for batch conversion"})
            if not os.path.exists(folder_path):
                return json.dumps({"error": f"Folder not found: {folder_path}"})
            locations = find_batch_files(folder_path, filename)
        else:
            locations = find_single_file(filename)
            
        if not locations:
            return json.dumps({"error": f"No files found matching {filename}"})

        if len(locations) > 1 and not args.get('batch'):
            locations_list = "\n".join(f"{i+1}. {loc}" for i, loc in enumerate(locations))
            return json.dumps({
                "prompt": {
                    "type": "select",
                    "message": f"Found multiple matches. Convert all? (y/n)\n{locations_list}",
                    "options": ["y", "n"]
                }
            })
        
        converted = []
        errors = []
        original_files = []
        
        for input_path in locations:
            try:
                with Image.open(input_path) as img:
                    original_format = img.format
                    if original_format not in SUPPORTED_FORMATS.values():
                        errors.append(f"Skipped {input_path}: Format {original_format} not supported")
                        continue
                        
                    output_path = os.path.splitext(input_path)[0] + '.' + output_format.lower()
                    if output_format == 'JPEG':
                        img = img.convert('RGB')
                    img.save(output_path, output_format)
                    converted.append(os.path.basename(input_path))
                    original_files.append(input_path)
                    
            except Image.UnidentifiedImageError:
                errors.append(f"Skipped {input_path}: Could not identify image format")
            except Exception as e:
                errors.append(f"Failed {input_path}: {str(e)}")

        if converted:
            return json.dumps({
                "prompt": {
                    "type": "select",
                    "message": f"Converted {len(converted)} files. Delete original files? (y/n)",
                    "options": ["y", "n"],
                    "context": {
                        "files": original_files,
                        "converted": converted,
                        "errors": errors
                    }
                }
            })
            
        result = {
            "message": f"Converted {len(converted)} files to {output_format.lower()}"
        }
        if converted:
            result["converted"] = converted
        if errors:
            result["errors"] = errors
            
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Error: {str(e)}"})

async def handle_cleanup_response(response, context):
    if response.lower() == 'y':
        cleanup_files(context.get('files', []))
        return json.dumps({
            "message": f"Converted {len(context['converted'])} files and cleaned up originals",
            "converted": context['converted'],
            "errors": context.get('errors', [])
        })
    return json.dumps({
        "message": f"Converted {len(context['converted'])} files",
        "converted": context['converted'],
        "errors": context.get('errors', [])
    })

object = {
    "name": "image_convert",
    "description": "Convert images between formats (PNG, JPG, WEBP, GIF). Supports batch conversion with wildcards (*.jpg).",
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Filename or pattern (e.g., image.jpg or *.jpg)"
            },
            "format": {
                "type": "string",
                "enum": list(SUPPORTED_FORMATS.keys()),
                "description": "Output format"
            },
            "batch": {
                "type": "boolean",
                "description": "Convert all matching files in specified folder",
                "default": False
            },
            "folder": {
                "type": "string",
                "description": "Folder path for batch conversion"
            }
        },
        "required": ["filename"]
    }
}
