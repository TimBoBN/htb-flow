from .. import notes
from ..api import get_api_key, load_machine_profile
from ..config import HTB_BASE
from ..ui import die, header, ok
from ._shared import submit_one


def run(machine: str):
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md not found: {notes_path}")

    n = notes.parse(notes_path)

    profile = load_machine_profile(machine)
    _mid_raw = profile.get("id")
    if not _mid_raw:
        die("Machine ID not found — is the API reachable?")
    machine_id = int(_mid_raw)

    header(f"Flag Submission: {machine}")

    submitted = 0
    for label, flag in (("User", n.get("user_flag", "")), ("Root", n.get("root_flag", ""))):
        if submit_one(key, machine_id, label, flag):
            submitted += 1

    print()
    if submitted > 0:
        ok(f"{submitted} flag(s) submitted successfully")
