from .. import notes
from ..api import get_api_key
from ..config import HTB_BASE
from ..ui import header, warn, die
from ._shared import submit_one


def run(machine: str):
    key = get_api_key()
    if not key:
        die("Kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key")

    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md nicht gefunden: {notes_path}")

    n = notes.parse(notes_path)
    machine_id_raw = None

    from ..api import load_machine_profile
    profile = load_machine_profile(machine)
    machine_id_raw = profile.get("id")

    if not machine_id_raw:
        die("Machine-ID nicht gefunden — API erreichbar?")

    header(f"Flag-Submission: {machine}")

    submitted = 0
    for label, flag in (("User", n.get("user_flag", "")), ("Root", n.get("root_flag", ""))):
        if submit_one(key, machine_id_raw, label, flag):
            submitted += 1

    print()
    if submitted > 0:
        from ..ui import ok
        ok(f"{submitted} Flag(s) erfolgreich eingereicht")
