import json
import requests
from pathlib import Path
import os

AUDIO_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac', '.wma', '.aiff'}

def transcribe_file(filepath):
    try:
        with open(filepath, "rb") as f:
            files = {"file": f}
            headers = {"Authorization": f"Bearer {authtoken}"}
            response = requests.post(
                "https://scripty.me/api/assistant/transcribe",
                files=files,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

async def func(args):
    try:
        audio_path = args.get("audio_path", "")
        
        # If no path provided, use latest file from audio_recordings
        if not audio_path:
            recordings_dir = Path.home() / "audio_recordings"
            if not recordings_dir.exists():
                return json.dumps({"success": False, "error": "No recordings directory found"})
            
            files = [(f, os.path.getmtime(f)) for f in recordings_dir.iterdir() 
                    if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS]
            if not files:
                return json.dumps({"success": False, "error": "No audio files found in recordings directory"})
            
            audio_path = str(max(files, key=lambda x: x[1])[0])
        else:
            # Resolve home directory and expand path
            audio_path = os.path.expanduser(audio_path)
            
            # Handle partial filenames by searching in audio_recordings
            if not os.path.exists(audio_path):
                recordings_dir = Path.home() / "audio_recordings"
                # Try each audio extension
                for ext in AUDIO_EXTENSIONS:
                    matches = list(recordings_dir.glob(f"{audio_path}*{ext}"))
                    if matches:
                        audio_path = str(matches[0])
                        break
        
        if not os.path.exists(audio_path):
            return json.dumps({"success": False, "error": f"Audio file not found: {audio_path}"})
        
        # Verify file extension
        if not Path(audio_path).suffix.lower() in AUDIO_EXTENSIONS:
            return json.dumps({"success": False, "error": f"Unsupported file type. Supported types: {', '.join(AUDIO_EXTENSIONS)}"})
        
        result = transcribe_file(audio_path)
        
        # If transcription successful, save to transcripts directory
        if result.get("success"):
            audio_file = Path(audio_path)
            transcripts_dir = audio_file.parent / "transcripts"
            transcripts_dir.mkdir(exist_ok=True)
            
            transcript_file = transcripts_dir / f"transcript_{audio_file.stem}.txt"
            with open(transcript_file, 'w') as f:
                f.write(result['transcript'])
            
            result["message"] = f"Transcription saved to: {transcript_file}"
            
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

object = {
    "name": "audio_transcriber",
    "description": """Transcribe audio files using server API.
Supported formats: WAV, MP3, M4A, AAC, OGG, FLAC, WMA, AIFF
    
Examples:
"transcribe latest recording"
→ {"audio_path": ""}  # Uses latest file from ~/audio_recordings

"transcribe recording_20240312"
→ {"audio_path": "recording_20240312"}  # Searches in ~/audio_recordings

"transcribe ~/Downloads/meeting.mp3"
→ {"audio_path": "~/Downloads/meeting.mp3"}  # Uses specific path""",
    "parameters": {
        "type": "object",
        "properties": {
            "audio_path": {
                "type": "string",
                "description": "Path to audio file (optional, uses latest recording if empty)"
            }
        }
    }
}

modules = ['requests']