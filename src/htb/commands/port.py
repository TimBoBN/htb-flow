from .. import notes
from ..config import HTB_BASE
from ..ui import die, header, ok


def run(machine: str, port: str, service: str, version: str = ""):
    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md nicht gefunden: {notes_path}")

    header(f"Port hinzufügen: {machine}")
    notes.add_port(notes_path, port, service, version)
    ok(f"{port}/{service}{' ' + version if version else ''} → notes.md")
    print()
