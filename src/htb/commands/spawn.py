import time

from ..api import get_active_machine, get_api_key, load_machine_profile, spawn_machine
from ..ui import die, header, ok, warn


def run(machine: str):
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    header(f"Spawn: {machine}")

    profile = load_machine_profile(machine)
    machine_id = profile.get("id")
    if not machine_id:
        die(f"Machine '{machine}' not found or API unreachable")

    msg = spawn_machine(key, machine_id)
    if msg:
        ok(msg)
    else:
        warn("No response from API")
        return

    print("  Waiting for IP", end="", flush=True)
    for _ in range(30):
        time.sleep(1)
        print(".", end="", flush=True)
        active = get_active_machine(key)
        if active.get("ip"):
            print()
            ok(f"Machine active: [cyan]{active["ip"]}[/cyan]")
            ok(f"Hostname: {machine.lower()}.htb")
            return
    print()
    warn("IP not yet available — try: htb status")
