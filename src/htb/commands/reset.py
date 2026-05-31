from ..api import get_api_key, load_machine_profile, reset_machine
from ..ui import die, header, ok, warn


def run(machine: str):
    key = get_api_key()
    if not key:
        die("Kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key")

    header(f"Reset: {machine}")

    profile = load_machine_profile(machine)
    machine_id = profile.get("id")
    if not machine_id:
        die(f"Maschine '{machine}' nicht gefunden oder API nicht erreichbar")

    msg = reset_machine(key, machine_id)
    if msg:
        ok(msg)
    else:
        warn("Keine Antwort von der API")
    print()
