import sys
import json
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from datetime import datetime
from pathlib import Path
import os
import subprocess

class AudioRecorder:
    def __init__(self):
        self.system_device = self._get_stereo_mix()
        self.mic_device = self._get_microphone()
        self.recording_system = []
        self.recording_mic = []
        
    def _get_stereo_mix(self):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if 'stereo mix' in dev['name'].lower() and dev['max_input_channels'] > 0:
                print(f"System audio device: {dev['name']}")
                return i
        return None

    def _get_microphone(self):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0 and 'stereo mix' not in dev['name'].lower():
                print(f"Microphone device: {dev['name']}")
                return i
        return sd.default.device[0]

    def start(self):
        if Path(os.path.expanduser('~/.recording')).exists():
            return {"error": "Already recording"}
            
        Path(os.path.expanduser('~/.recording')).touch()
        
        # Create background script
        background_script = Path("audio_recorder_background.py")
        with open(background_script, 'w') as f:
            f.write('''
import sys
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from datetime import datetime
from pathlib import Path
import os

class AudioRecorder:
    def __init__(self):
        self.system_device = self._get_stereo_mix()
        self.mic_device = self._get_microphone()
        self.recording_system = []
        self.recording_mic = []
        self.start_time = time.time()
        
    def _get_stereo_mix(self):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if 'stereo mix' in dev['name'].lower() and dev['max_input_channels'] > 0:
                print(f"System audio device: {dev['name']}")
                return i
        return None

    def _get_microphone(self):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0 and 'stereo mix' not in dev['name'].lower():
                print(f"Microphone device: {dev['name']}")
                return i
        return sd.default.device[0]

    def system_callback(self, indata, frames, time, status):
        if status:
            print(f'System Error: {status}')
        self.recording_system.append(indata.copy())

    def mic_callback(self, indata, frames, time, status):
        if status:
            print(f'Mic Error: {status}')
        self.recording_mic.append(indata.copy())

    def background_record(self):
        try:
            with sd.InputStream(callback=self.system_callback, channels=2, device=self.system_device) as system_stream, \\
                 sd.InputStream(callback=self.mic_callback, channels=2, device=self.mic_device) as mic_stream:
                print("Recording started in background...")
                while Path(os.path.expanduser('~/.recording')).exists():
                    # Auto-stop after 1 hour
                    if time.time() - self.start_time > 3600:  # 3600 seconds = 1 hour
                        print("Auto-stopping after 1 hour")
                        Path(os.path.expanduser('~/.recording')).unlink()
                        break
                    time.sleep(0.1)
                    
            if self.recording_system or self.recording_mic:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_dir = Path.home() / "audio_recordings"
                save_dir.mkdir(exist_ok=True)
                
                # Mix and save both streams
                if self.recording_system and self.recording_mic:
                    system_audio = np.concatenate(self.recording_system, axis=0)
                    mic_audio = np.concatenate(self.recording_mic, axis=0)
                    
                    # Adjust volume levels
                    system_gain = 1.5  # Increase system audio
                    mic_gain = 1.0     # Keep mic at normal level
                    
                    if np.max(np.abs(system_audio)) > 0:
                        system_audio = system_audio / np.max(np.abs(system_audio)) * system_gain
                    if np.max(np.abs(mic_audio)) > 0:
                        mic_audio = mic_audio / np.max(np.abs(mic_audio)) * mic_gain
                    
                    # Ensure same length
                    min_len = min(len(system_audio), len(mic_audio))
                    system_audio = system_audio[:min_len]
                    mic_audio = mic_audio[:min_len]
                    
                    mixed_audio = system_audio + mic_audio
                    
                    # Prevent clipping
                    if np.max(np.abs(mixed_audio)) > 1:
                        mixed_audio = mixed_audio / np.max(np.abs(mixed_audio))
                    
                    audio_file = save_dir / f"recording_{timestamp}.wav"
                    with sf.SoundFile(str(audio_file), mode='w', samplerate=44100, channels=2) as f:
                        f.write(mixed_audio)
                    print(f"Audio saved to: {audio_file}")
                    
                elif self.recording_system:
                    audio_file = save_dir / f"recording_{timestamp}.wav"
                    audio_data = np.concatenate(self.recording_system, axis=0)
                    sf.write(str(audio_file), audio_data, 44100)
                    print(f"Audio saved to: {audio_file}")
                    
                else:
                    audio_file = save_dir / f"recording_{timestamp}.wav"
                    audio_data = np.concatenate(self.recording_mic, axis=0)
                    sf.write(str(audio_file), audio_data, 44100)
                    print(f"Audio saved to: {audio_file}")
                    
        except Exception as e:
            print(f"Recording error: {e}")
        finally:
            sys.exit(0)

if __name__ == '__main__':
    recorder = AudioRecorder()
    recorder.background_record()
''')
        
        subprocess.Popen([sys.executable, str(background_script), "--background"],
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        return {"message": "Recording started"}

    def stop(self):
        if not Path(os.path.expanduser('~/.recording')).exists():
            return {"error": "Not recording"}
            
        Path(os.path.expanduser('~/.recording')).unlink()
        return {"message": "Recording stopped"}

recorder = AudioRecorder()

async def func(args):
    try:
        operation = args.get("operation")
            
        if operation == "start":
            return json.dumps(recorder.start())
        elif operation == "stop":
            return json.dumps(recorder.stop())
        return json.dumps({"error": "Invalid operation"})
    except Exception as e:
        return json.dumps({"error": str(e)})

object = {
    "name": "audio_recorder",
    "description": "Record system and microphone audio (auto-stops after 1 hour)",
    "parameters": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "Operation to perform (start/stop)"
            }
        },
        "required": ["operation"]
    }
}

