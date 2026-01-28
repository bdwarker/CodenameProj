import sounddevice as sd
import numpy as np
import tempfile
import wave
from faster_whisper import WhisperModel
import json
import webrtcvad
import collections

vad = webrtcvad.Vad(1)  # Set aggressiveness mode (0-3)

with open('config.json', 'r') as f:
    config = json.load(f)

model = WhisperModel("base", device="cpu", compute_type="int8")

# Global flag to control listening
is_listening = True

def stop_listening():
    global is_listening
    is_listening = False

def start_listening():
    global is_listening
    is_listening = True

def record_audio_vad(samplerate: int = 16000, frame_duration_ms: int = 30, padding_duration_ms: int = 300):
    """
    Records audio until silence is detected using WebRTC VAD.
    """
    global is_listening
    print("🎤 Listening...")

    frame_size = int(samplerate * frame_duration_ms / 1000)
    padding_frames = int(padding_duration_ms / frame_duration_ms)

    ring_buffer = collections.deque(maxlen=padding_frames)
    triggered = False
    voiced_frames = []

    def frame_generator(indata, frames, time_info, status):
        # yield PCM16 bytes for webrtcvad
        yield indata.tobytes()

    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16') as stream:
        while is_listening:
            audio_chunk, overflowed = stream.read(frame_size)
            pcm_bytes = audio_chunk.tobytes()
            is_speech = vad.is_speech(pcm_bytes, samplerate)

            if not triggered:
                ring_buffer.append((pcm_bytes, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    voiced_frames.extend([f for f, s in ring_buffer])
                    ring_buffer.clear()
            else:
                voiced_frames.append(pcm_bytes)
                ring_buffer.append((pcm_bytes, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    break
        
        if not is_listening:
             return None, samplerate

    # Combine into one audio array
    audio = b"".join(voiced_frames)

    # Convert back to numpy for Whisper
    audio_np = np.frombuffer(audio, dtype=np.int16).reshape(-1, 1)
    return audio_np, samplerate


def record_audio(duration: int = 4, samplerate: int = 16000):
    print("🎤 Listening...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate,
                   channels=1, dtype='int16')
    sd.wait()
    return audio, samplerate

def speech_to_text():
    start_listening()
    result = record_audio_vad()
    if result[0] is None:
        return ""
    
    audio, samplerate = result

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        with wave.open(f.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # int16
            wf.setframerate(samplerate)
            wf.writeframes(audio.tobytes())

        segments, _ = model.transcribe(f.name, beam_size=1)
        text = " ".join(seg.text for seg in segments).strip()

    print(f"🗣 You said: {text}")
    if text == "":
        # raise ValueError("No speech detected. Please try again.")
        return ""
    else:
        return text