import json
from utils.logger import get_logger
from typing import List, Dict, Any


class DataLoader:
    @staticmethod
    def load_mbpp(path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, "r") as f:
                data = [json.loads(line) for line in f]
            return data
        except FileNotFoundError:
            get_logger(__name__).error(f"Error: The file at {path} was not found.")
            return []
        except json.JSONDecodeError:
            get_logger(__name__).error(
                f"Error: Failed to decode JSON from the file at {path}."
            )
            return []
