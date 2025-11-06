import json, os
from typing import Dict, Any

class JSONLLogger:
    def __init__(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path

    def write(self, obj: Dict[str, Any]) -> None:
        with open(self.path, 'a') as f:
            f.write(json.dumps(obj) + "\n")
