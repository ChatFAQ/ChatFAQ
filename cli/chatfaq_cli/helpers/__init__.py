import json
from io import UnsupportedOperation
from json import JSONDecodeError
from os.path import exists
from pathlib import Path

CONFIG_FILE_PATH = f"{str(Path.home())}/.chatfaq-cli-config"


def get_config():
    if not exists(CONFIG_FILE_PATH):
        return {}
    with open(CONFIG_FILE_PATH, "r+") as f:
        try:
            return json.load(f)
        except (UnsupportedOperation, JSONDecodeError) as e:
            print(e)
            return {}


def set_config(key, val):
    with open(CONFIG_FILE_PATH, "r+") as f:
        content = {}
        try:
            content = json.load(f)
        except (UnsupportedOperation, JSONDecodeError) as e:
            print(e)
            pass
        content[key] = val
        f.seek(0)
        json.dump(content, f, indent=4)
        f.truncate()
