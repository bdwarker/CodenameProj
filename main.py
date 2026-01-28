import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=FutureWarning, module="TTS.utils.io")
warnings.filterwarnings("ignore", category=FutureWarning, module="doctr.models.utils.pytorch")

from utils.elevenlabsAPI import playFinale
from dotenv import load_dotenv
from actions.launchApp import open_app
import json
from utils.tts import ttsRun
from actions.actions import *
from utils.memory import add_memory, get_memory, clear_memory
from utils.log import log_to_file
from actions.brain import ollamaReply, ollamaJson, ollamaSeeImage
from actions.image import capture_and_extract
from utils.speechRecog import speech_to_text

with open("config.json", "r") as f:
            config = json.load(f)

load_dotenv()
# Load config
# Ollama settings
OLLAMA_MODEL = config.get("ollama_model", "gemma3:4b")
assistant_name = config.get("name", "Assistant")
f.close()
# -----------------------------
# Main Loop
# -----------------------------
if __name__ == "__main__":
    print(f"🤖 {assistant_name} is ready! Say 'quit' to exit.")
    while True:
        with open("config.json", "r") as f:
            config = json.load(f)
        if config.get("use_speech_recognition", True):
            user_input = speech_to_text()
        else:
            user_input = input("You: ")
        if not user_input:
            continue

        if {"exit_commands"} and any(cmd.lower() in user_input.lower() for cmd in config["exit_commands"]):
            break
        output = ollamaJson(user_input)
        for act in output:  # in case of multiple actions
            if act["action"] == "open_browser":
                open_browser()
            elif act["action"] == "launch_app":
                launch(act["details"])
            elif act["action"] == "search_browser":
                search(act["details"])
            elif act["action"] == "clear logs":
                for file in LOG_DIR.glob("*.txt"):
                    file.unlink()
                print("🗑️ Cleared logs")
                ttsRun("Cleared logs")
            elif act["action"] == "clear memory":
                clear_memory()
                print("🗑️ Cleared memory")
                ttsRun("Cleared memory")
            elif act["action"] == "reply" and act["remember"] == False:
                ttsRun(ollamaReply(user_input))
            elif act["action"] == "open_link":
                # assuming act["details"] has the URL
                url = act["details"]
                if url:
                    open_link(url)
                else:
                    print("❓ No link provided.")
                    ttsRun("I'm sorry, no link was provided.")
            elif act["action"] == "remember" and act["remember"] == True:
                rememberReply = ollamaReply("You can remember things. " + user_input)
                add_memory(act.get("memory_key", "general"), act.get("memory_value", user_input))
                ttsRun(rememberReply)
                print("🧠 Memory added")
                print("🗣️ I've remembered that " + act.get("memory_key", "general"))
                ttsRun(f"I've remembered that {act.get('memory_key', 'general')}")
            elif act["action"] == "see_screen":
                if not act["details"].isdigit() or int(act["details"]) < 1:
                    print("❓ Invalid monitor index. It should be an integer.")
                    ttsRun("I'm sorry, the monitor index should be an integer.")
                    continue
                else:
                    index = int(act["details"])
                    text_file = capture_and_extract(index)
                    with open(text_file, "r", encoding="utf-8") as f:
                        extracted_text = f.read()
                    screenSummary = ollamaSeeImage(extracted_text, user_input)
                    ttsRun("I've processed the content on the screen. Please wait while I tend to your request.")
                    ttsRun(screenSummary)
            elif act["action"] == "type":
                type_text(act["details"])
            elif act["action"] == "press_key":
                press_key(act["details"])
            else:
                print("❓ Unknown action or invalid format.")
                ttsRun("I'm sorry, I didn't understand that action.")
        log_to_file("user_input", user_input)
        log_to_file("assistant_output", str(output))
        # Close JSON file
        f.close()
    print("👋 Goodbye!")