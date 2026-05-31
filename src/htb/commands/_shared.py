import re
from ..api import submit_flag
from ..ui import console, ok, warn, ask, ask_input


def submit_one(key: str, machine_id: int, label: str, flag: str) -> bool:
    """Interaktive Flag-Submission. Gibt True zurück wenn erfolgreich."""
    if not flag:
        warn(f"{label}: kein Flag in notes.md gefunden")
        return False
    console.print(f"  [bold]{label} Flag:[/bold] {flag}")
    if ask(f"{label} Flag jetzt einreichen?"):
        diff_str = ask_input("Schwierigkeit (1-10):")
        if not re.fullmatch(r"([1-9]|10)", diff_str):
            warn("Ungültige Eingabe, übersprungen")
            return False
        result = submit_flag(key, machine_id, flag, int(diff_str))
        if result and re.search(r"correct|own|congrat|pwned", result, re.IGNORECASE):
            ok(f"Eingereicht: {result}")
            return True
        elif result:
            warn(f"Antwort: {result}")
        else:
            warn("Keine Antwort von der API")
    return False
