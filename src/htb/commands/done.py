import re
import shutil
import subprocess
import sys
from datetime import date

from .. import hosts, notes, vpn
from ..api import get_api_key, terminate_machine
from ..config import HTB_BASE
from ..ui import BANNER_DONE, ask, console, die, header, ok, warn
from ._shared import submit_one


def run(machine: str, profile: dict):
    box_dir = HTB_BASE / machine
    hostname = f"{machine.lower()}.htb"
    notes_path = box_dir / "notes.md"

    if not box_dir.exists():
        die(f"Machine '{machine}' not found at {box_dir}")

    console.print(BANNER_DONE)
    console.print(f"  [bold]Machine:[/bold]  {machine}")
    console.print(f"  [bold]Date:[/bold]     {date.today().strftime('%Y-%m-%d')}\n")

    user_flag = ""
    root_flag = ""
    flags_pending = 0

    if notes_path.exists():
        header("Summary")
        n = notes.parse(notes_path)

        for field in ("os", "difficulty", "points", "stars"):
            if not n.get(field) or n[field] == "?":
                n[field] = profile.get(field, "?")

        console.print(f"  [bold]OS:[/bold]          {n.get('os', '?')}")
        console.print(f"  [bold]Difficulty:[/bold]  {n.get('difficulty', '?')}")
        if n.get("points") and n["points"] != "?":
            console.print(f"  [bold]Points:[/bold]      {n['points']}")
        if n.get("stars") and n["stars"] != "?":
            console.print(f"  [bold]Rating:[/bold]      ★ {n['stars']}")
        console.print(f"  [bold]User Flag:[/bold]   {n.get('user_flag') or '(empty)'}")
        console.print(f"  [bold]Root Flag:[/bold]   {n.get('root_flag') or '(empty)'}")

        user_flag = n.get("user_flag", "")
        root_flag = n.get("root_flag", "")
        flags_pending = sum(1 for f in (user_flag, root_flag) if f)

    key = get_api_key()
    machine_id = int(profile["id"]) if profile.get("id") else None
    flags_submitted = 0
    submission_possible = bool(key and machine_id)

    if submission_possible and key and machine_id:
        header("Flag Submission")
        if submit_one(key, machine_id, "User", user_flag):
            flags_submitted += 1
        if submit_one(key, machine_id, "Root", root_flag):
            flags_submitted += 1
    else:
        if not key:
            warn("Flag submission skipped (no API key — HTB_API_KEY or ~/.config/htb/api_key)")
        else:
            warn("Flag submission skipped (machine ID not found — is the API reachable?)")

    header("Terminate machine")
    if submission_possible and flags_pending > 0 and flags_submitted < flags_pending:
        warn(f"Not all flags submitted ({flags_submitted}/{flags_pending})!")
        if not ask("Terminate anyway?"):
            warn("Aborted — submit flags first.")
            sys.exit(1)

    active_ip = profile.get("ip", "")
    if active_ip:
        if ask(f"Terminate machine? (active IP: {active_ip})"):
            if key:
                msg = terminate_machine(key)
                if msg and re.search(r"not found|error", msg, re.IGNORECASE):
                    warn(f"Failed: {msg}")
                else:
                    ok("Machine terminated")
            else:
                warn("No API key — terminate machine manually")
        else:
            warn("Machine still running")
    else:
        ok("No active instance found")

    header("/etc/hosts")
    if hosts.contains(hostname):
        if ask(f"Remove entry '{hostname}'?"):
            hosts.remove(hostname)
            ok("Entry removed")
        else:
            warn("Entry kept")
    else:
        ok(f"No entry for {hostname} found")

    header("VPN")
    if vpn.active():
        if ask("Stop VPN (tun0)?"):
            vpn.stop()
        else:
            warn("VPN still running")
    else:
        ok("VPN already inactive")

    header("Archive")
    archive = HTB_BASE / f"{machine}.tar.gz"
    if ask(f"Archive box folder → {machine}.tar.gz?"):
        subprocess.run(
            ["tar", "-czf", str(archive), "-C", str(HTB_BASE), machine],
            check=True,
        )
        size_mb = archive.stat().st_size / (1024 * 1024)
        ok(f"Archive created: {archive} ({size_mb:.0f}M)")
        if ask("Delete original folder?"):
            shutil.rmtree(box_dir)
            ok(f"Folder deleted: {box_dir}")
    else:
        warn("No archive created")

    if box_dir.exists() and ask("Export writeup?"):
        from .writeup import run as writeup_run

        writeup_run(machine)

    console.print("\n[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print(f"[bold]  {machine} — complete[/bold]")
    console.print("[bold cyan]══════════════════════════════════[/bold cyan]\n")
