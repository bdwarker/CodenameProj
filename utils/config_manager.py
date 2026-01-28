import json
import os

CONFIG_PATH = "config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_config(config_data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=4)

def get_config_value(key, default=None):
    config = load_config()
    return config.get(key, default)

def set_config_value(key, value):
    config = load_config()
    config[key] = value
    save_config(config)
