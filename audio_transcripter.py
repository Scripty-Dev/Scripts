import sys
import json
import requests
from pathlib import Path
import os

def transcribe_file(filepath):
    try:
        with open(filepath, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"https://scripty.me/api/assistant/transcribe?token={config['token']}",
                files=files
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

async def func(args):
    try:
        audio_path = args.get("audio_path")
        if not audio_path or not Path(audio_path).exists():
            return json.dumps({"success": False, "error": "Invalid audio path"})
        return json.dumps(transcribe_file(audio_path))
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

object = {
    "name": "audio_transcriber",
    "description": "Transcribe audio files using server API",
    "parameters": {
        "type": "object",
        "properties": {
            "audio_path": {
                "type": "string",
                "description": "Path to audio file"
            }
        },
        "required": ["audio_path"]
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
                print(json.dumps({"success": False, "error": str(e)}))
