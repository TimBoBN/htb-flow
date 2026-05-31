from ..api import get_api_key, load_machine_profile, reset_machine
from ..ui import die, header, ok, warn


def run(machine: str):
    key = get_api_key()
    if not key:
        die("No API key — run: htb key set")

    header(f"Reset: {machine}")

    profile = load_machine_profile(machine)
    machine_id = profile.get("id")
    if not machine_id:
        die(f"Machine '{machine}' not found or API unreachable")

    msg = reset_machine(key, machine_id)
    if msg:
        ok(msg)
    else:
        warn("No response from API")
    print()
