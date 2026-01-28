import json
from typing import List
from pathlib import Path

# Load or create memory file
MEMORY_FILE = Path("database/memory.json")
if not MEMORY_FILE.exists():
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)
else:
    with open(MEMORY_FILE, "r") as f:
        try:
            json.load(f)
        except json.JSONDecodeError:
            with open(MEMORY_FILE, "w") as f:
                json.dump([], f)

def add_memory(key:str, value: str):
    """Add a memory entry to the memory.json file."""
    with open(MEMORY_FILE, "r+") as f:
        memory = json.load(f)
        memory.append({key: value})
        f.seek(0)
        json.dump(memory, f, indent=4)
        f.truncate()
def get_memory() -> List[dict]:
    """Retrieve all memory entries from the memory.json file."""
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
    return memory
def clear_memory():
    """Clear all memory entries from the memory.json file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump([], f)
    print("🗑️ Memory cleared")
