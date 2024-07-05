from typing import List


def format_list(items: List[str], prefix: str = "") -> str:
    return "\n".join(f"{prefix}{item}" for item in items)
