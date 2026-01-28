import os
from dotenv import load_dotenv
from utils.tts import ttsRun
from actions.brain import ollamaReply
from actions.launchApp import open_app
from pathlib import Path
import pyautogui
import time

LOG_DIR = Path("utils/logs")
LOG_DIR.mkdir(exist_ok=True)


load_dotenv()

def open_browser():
    os.system("start firefox")
    print("🖥️ Opened Firefox")

def launch(app_name: str):
    open_app(app_name)
    print(f"🖥️ Opened {app_name}")

def search(query: str):
    os.system(f'start firefox "https://www.duckduckgo.com/search?q={query}"')
    print(f"🔍 Searched for: {query}")

def clear_logs():
    for file in LOG_DIR.glob("*.txt"):
        file.unlink()
    print("🗑️ Cleared logs")

def clear_memory():
    memory_file = Path("memory.json")
    if memory_file.exists():
        memory_file.unlink()
    print("🗑️ Cleared memory")

def type_text(text: str):
    # if the text starts with REPLY, we need to extract the actual text to be typed
    if text.startswith("REPLY"):
        reply_text = ollamaReply(f'Generate a reply for: {text[len("REPLY"):].strip()}')
        text_to_type = reply_text
    else:
        text_to_type = text
    time.sleep(4)  # give user 2 seconds to focus the input field
    pyautogui.write(text_to_type, interval=0.05)
import os
from dotenv import load_dotenv
from utils.tts import ttsRun
from actions.brain import ollamaReply
from actions.launchApp import open_app
from pathlib import Path
import pyautogui
import time

LOG_DIR = Path("utils/logs")
LOG_DIR.mkdir(exist_ok=True)


load_dotenv()

def open_browser():
    os.system("start firefox")
    print("🖥️ Opened Firefox")

def launch(app_name: str):
    open_app(app_name)
    print(f"🖥️ Opened {app_name}")

def search(query: str):
    os.system(f'start firefox "https://www.duckduckgo.com/search?q={query}"')
    print(f"🔍 Searched for: {query}")

def clear_logs():
    for file in LOG_DIR.glob("*.txt"):
        file.unlink()
    print("🗑️ Cleared logs")

def clear_memory():
    memory_file = Path("memory.json")
    if memory_file.exists():
        memory_file.unlink()
    print("🗑️ Cleared memory")

def type_text(text: str):
    # if the text starts with REPLY, we need to extract the actual text to be typed
    if text.startswith("REPLY"):
        reply_text = ollamaReply(f'Generate a reply for: {text[len("REPLY"):].strip()}')
        text_to_type = reply_text
    else:
        text_to_type = text
    time.sleep(4)  # give user 2 seconds to focus the input field
    pyautogui.write(text_to_type, interval=0.05)
    print(f"⌨️ Typed text: {text_to_type}")
def press_key(key: str):
    time.sleep(2)
    pyautogui.press(key)
    print(f"⌨️ Pressed key: {key}")

def open_link(url: str):
    os.system(f'start firefox "{url}"')
    ttsRun("Opening the link")
    print(f"🌐 Opened link: {url}")

def read_file(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"📄 Read file: {path}")
        return content
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return f"Error reading file: {e}"

def write_file(path: str, content: str):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"💾 Written to file: {path}")
        return f"Successfully wrote to {path}"
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return f"Error writing file: {e}"

def list_dir(path: str):
    try:
        files = os.listdir(path)
        print(f"📂 Listed directory: {path}")
        return ", ".join(files)
    except Exception as e:
        print(f"❌ Error listing directory: {e}")
        return f"Error listing directory: {e}"

def delete_file(path: str):
    try:
        os.remove(path)
        print(f"🗑️ Deleted file: {path}")
        return f"Successfully deleted {path}"
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        return f"Error deleting file: {e}"