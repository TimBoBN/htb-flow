import time

from ..api import get_api_key, load_machine_profile, spawn_machine, get_active_machine
from ..ui import header, ok, warn, die


def run(machine: str):
    key = get_api_key()
    if not key:
        die("Kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key")

    header(f"Spawn: {machine}")

    profile = load_machine_profile(machine)
    machine_id = profile.get("id")
    if not machine_id:
        die(f"Maschine '{machine}' nicht gefunden oder API nicht erreichbar")

    msg = spawn_machine(key, machine_id)
    if msg:
        ok(msg)
    else:
        warn("Keine Antwort von der API")
        return

    print("  Warte auf IP", end="", flush=True)
    for _ in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        active = get_active_machine(key)
        if active.get("ip"):
            print()
            ok(f"Maschine aktiv: [cyan]{active['ip']}[/cyan]")
            ok(f"Hostname: {machine.lower()}.htb")
            return
    print()
    warn("IP noch nicht verfügbar — versuche: htb status")
