import os
os.environ["PATH"] = r"C:\Users\Mohammed Shaan\Documents\Programming\CodenameProj\eSpeak NG"
import asyncio
import sounddevice as sd
import soundfile as sf
import logging
import sys
from contextlib import redirect_stdout
from io import StringIO
from TTS.api import TTS
import re
import json

with open("config.json", "r") as f:
    config = json.load(f)
# Quiet init
with redirect_stdout(StringIO()):
    tts = TTS("tts_models/en/vctk/vits")
    tts.to(device="cuda")

logging.getLogger("TTS").setLevel(logging.ERROR)

def strip_ansi_codes(text):
    import re
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)
def removeAsterisks(text):
    import re
    # remove inline *something*
    text = re.sub(r'\*[^*]+\*', '', text)
    # remove list bullets starting with "* " at the beginning of a line
    text = re.sub(r'^\*\s+', '', text, flags=re.MULTILINE)
    return text
def removeEmoji(text):
    import re
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)
def finalize_text(text):
    text = strip_ansi_codes(text)
    text = removeAsterisks(text)
    text = removeEmoji(text)
    text = text.replace("*", "")
    return text

# Old speaker: "p335", "p305", "p237"
def convert_text_to_speech(text, speaker=config["vits_speaker_id"], file_path="output.wav"):
    text = finalize_text(text)
    tts.tts_to_file(
        text=text,
        speaker=speaker,
        file_path=file_path
    )

# async def play_audio_async(file_path="output.wav"):
#     """Play audio asynchronously with cancellation support."""
#     data, samplerate = sf.read(file_path)

#     loop = asyncio.get_event_loop()
#     fut = loop.run_in_executor(None, lambda: sd.play(data, samplerate))
    
#     try:
#         await fut
#         await asyncio.sleep(len(data) / samplerate)  # wait duration instead of sd.wait()
#     except asyncio.CancelledError:
#         sd.stop()
#         raise

def stop_audio():
    sd.stop()

def play_audio(file_path="output.wav"):
    data, samplerate = sf.read(file_path)
    sd.play(data, samplerate)
    sd.wait()  # wait until done

def ttsRun(text: str):
    convert_text_to_speech(text)
    play_audio("output.wav")

if __name__ == "__main__":
    sample_text = input("Enter text to convert to speech: ")
    convert_text_to_speech(sample_text)
    play_audio("output.wav")
