from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os
import json
load_dotenv()

# Load config
with open("config.json", "r") as f:
    config = json.load(f)
# ElevenLabs settings
USE_ELEVENLABS = config.get("use_elevenlabs", False)
VOICE_ID = str(config.get("elevenlabs_voice", "cgSgspJ2msm6clMCkdW9"))

# Array of API keys
API_KEYS = [
    os.getenv("ELEVENLABS_API_KEY1"),
    os.getenv("ELEVENLABS_API_KEY2"),
    os.getenv("ELEVENLABS_API_KEY3"),
]

def playFinale(textPrompt: str):
    if not USE_ELEVENLABS:
        print("ElevenLabs TTS is disabled in config.")
        return
    else:
      for i, api_key in enumerate(API_KEYS, 1):
          try:
              print(f"Trying API Key {i}...")
              client = ElevenLabs(api_key=api_key)
              audio = client.text_to_speech.convert(
                  text=textPrompt,
                  voice_id=VOICE_ID,
                  model_id="eleven_multilingual_v2",
                  output_format="mp3_44100_128",
              )
              play(audio)
              print(f"Success with API Key {i}!")
              return  # Exit if successful
          except Exception as e:
              print(f"API Key {i} failed: {e}")
              if i == len(API_KEYS):
                  print("All API keys exhausted! 😭")
                  raise Exception("All API keys exhausted.")