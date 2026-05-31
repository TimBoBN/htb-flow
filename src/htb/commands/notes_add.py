from .. import notes
from ..config import HTB_BASE
from ..ui import die, ok


def run(machine: str, text: str):
    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md not found: {notes_path}")

    notes.append_note(notes_path, text)
    ok(f"Note added: {text[:60]}{'...' if len(text) > 60 else ''}")
