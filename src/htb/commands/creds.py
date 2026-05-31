from .. import notes
from ..config import HTB_BASE
from ..ui import ask_input, die, header, ok, warn


def run(machine: str):
    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md nicht gefunden: {notes_path}")

    header(f"Credentials: {machine}")

    user = ask_input("Username:")
    if not user:
        warn("Abgebrochen")
        return
    password = ask_input("Passwort:")
    context = ask_input("Kontext (z.B. SSH, Web, leer = -):")

    notes.append_creds(notes_path, user, password, context)
    ok(f"Gespeichert: {context or '-'} | {user} | ***")
    print()
