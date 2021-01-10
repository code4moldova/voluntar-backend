from typing import Optional


def toBool(x: Optional[str] = None) -> Optional[bool]:
    return True if x == "true" else False if x == "false" else None
