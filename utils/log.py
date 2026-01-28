import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

with open("config.json", "r") as f:
    config = json.load(f)

load_dotenv()
# Set up logs folder
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def log_to_file(name: str, content: str):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    if config.get("debug_mode", False):
        """Write content to a log file with timestamp in logs/ folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = LOG_DIR / f"{name}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📝 Logged to {filename}")
    else:
        print("Debug mode is off. Logs are not being saved.")

