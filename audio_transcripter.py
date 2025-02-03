import json
import requests
from pathlib import Path

def transcribe_file(filepath, token):
    try:
        with open(filepath, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"https://scripty.me/api/assistant/transcribe?token={token}",
                files=files
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

async def func(args):
    try:
        audio_path = args.get("audio_path")
        token = args.get("token")
        if not audio_path or not Path(audio_path).exists():
            return json.dumps({"success": False, "error": "Invalid audio path"})
        if not token:
            return json.dumps({"success": False, "error": "Token is required"})
        return json.dumps(transcribe_file(audio_path, token))
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
            },
            "token": {
                "type": "string",
                "description": "Scripty API token"
            }
        },
        "required": ["audio_path", "token"]
    }
}

modules = ['requests']