import re

from ..api import submit_flag
from ..ui import ask, ask_input, console, ok, warn


def submit_one(key: str, machine_id: int, label: str, flag: str) -> bool:
    """Interactive flag submission. Returns True on success."""
    if not flag:
        warn(f"{label}: no flag found in notes.md")
        return False
    console.print(f"  [bold]{label} Flag:[/bold] {flag}")
    if ask(f"Submit {label} flag now?"):
        diff_str = ask_input("Difficulty (1-10):")
        if not re.fullmatch(r"([1-9]|10)", diff_str):
            warn("Invalid input, skipped")
            return False
        result = submit_flag(key, machine_id, flag, int(diff_str))
        if result and re.search(r"correct|own|congrat|pwned", result, re.IGNORECASE):
            ok(f"Submitted: {result}")
            return True
        elif result:
            warn(f"Response: {result}")
        else:
            warn("No response from API")
    return False
