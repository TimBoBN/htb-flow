from .. import notes
from ..config import HTB_BASE
from ..ui import ask_input, die, header, ok, warn


def run(machine: str):
    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md not found: {notes_path}")

    header(f"Credentials: {machine}")

    user = ask_input("Username:")
    if not user:
        warn("Aborted")
        return
    password = ask_input("Password:")
    context = ask_input("Context (e.g. SSH, Web, leave empty for -):")

    notes.append_creds(notes_path, user, password, context)
    ok(f"Saved: {context or '-'} | {user} | ***")
    print()
