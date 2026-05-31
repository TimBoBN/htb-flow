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
        die(f"Maschine '{machine}' nicht gefunden unter {box_dir}")

    console.print(BANNER_DONE)
    console.print(f"  [bold]Machine:[/bold]  {machine}")
    console.print(f"  [bold]Zeit:[/bold]     {date.today().strftime('%d.%m.%Y')}\n")

    user_flag = ""
    root_flag = ""
    flags_pending = 0

    if notes_path.exists():
        header("Summary")
        n = notes.parse(notes_path)

        for field in ("os", "difficulty", "points", "stars"):
            if not n.get(field) or n[field] == "?":
                n[field] = profile.get(field, "?")

        console.print(f"  [bold]OS:[/bold]             {n.get('os', '?')}")
        console.print(f"  [bold]Schwierigkeit:[/bold]  {n.get('difficulty', '?')}")
        if n.get("points") and n["points"] != "?":
            console.print(f"  [bold]Punkte:[/bold]         {n['points']}")
        if n.get("stars") and n["stars"] != "?":
            console.print(f"  [bold]Rating:[/bold]         ★ {n['stars']}")
        console.print(f"  [bold]User Flag:[/bold]      {n.get('user_flag') or '(leer)'}")
        console.print(f"  [bold]Root Flag:[/bold]      {n.get('root_flag') or '(leer)'}")

        user_flag = n.get("user_flag", "")
        root_flag = n.get("root_flag", "")
        flags_pending = sum(1 for f in (user_flag, root_flag) if f)

    # Flag-Submission
    key = get_api_key()
    machine_id = int(profile["id"]) if profile.get("id") else None
    flags_submitted = 0
    submission_possible = bool(key and machine_id)

    if submission_possible and key and machine_id:
        header("Flag-Submission")
        if submit_one(key, machine_id, "User", user_flag):
            flags_submitted += 1
        if submit_one(key, machine_id, "Root", root_flag):
            flags_submitted += 1
    else:
        if not key:
            warn(
                "Flag-Submission übersprungen (kein API-Key — HTB_API_KEY oder ~/.config/htb/api_key)"
            )
        else:
            warn("Flag-Submission übersprungen (Machine-ID nicht gefunden — API erreichbar?)")

    # Maschine terminieren
    header("Maschine terminieren")
    if submission_possible and flags_pending > 0 and flags_submitted < flags_pending:
        warn(f"Nicht alle Flags wurden eingereicht ({flags_submitted}/{flags_pending})!")
        if not ask("Trotzdem terminieren?"):
            warn("Abbruch — Flags zuerst einreichen.")
            sys.exit(1)

    active_ip = profile.get("ip", "")
    if active_ip:
        if ask(f"Maschine terminieren? (aktive IP: {active_ip})"):
            if key:
                msg = terminate_machine(key)
                if msg and re.search(r"not found|error", msg, re.IGNORECASE):
                    warn(f"Fehlgeschlagen: {msg}")
                else:
                    ok("Maschine terminiert")
            else:
                warn("Kein API-Key — Maschine manuell terminieren")
        else:
            warn("Maschine läuft weiter")
    else:
        ok("Keine aktive Instanz gefunden")

    # /etc/hosts
    header("/etc/hosts")
    if hosts.contains(hostname):
        if ask(f"Eintrag '{hostname}' entfernen?"):
            hosts.remove(hostname)
            ok("Eintrag entfernt")
        else:
            warn("Eintrag behalten")
    else:
        ok(f"Kein Eintrag für {hostname} gefunden")

    # VPN
    header("VPN")
    if vpn.active():
        if ask("VPN (tun0) stoppen?"):
            vpn.stop()
        else:
            warn("VPN läuft weiter")
    else:
        ok("VPN bereits inaktiv")

    # Archivierung
    header("Archivierung")
    archive = HTB_BASE / f"{machine}.tar.gz"
    if ask(f"Box-Ordner archivieren → {machine}.tar.gz?"):
        subprocess.run(
            ["tar", "-czf", str(archive), "-C", str(HTB_BASE), machine],
            check=True,
        )
        size_mb = archive.stat().st_size / (1024 * 1024)
        ok(f"Archiv erstellt: {archive} ({size_mb:.0f}M)")
        if ask("Original-Ordner löschen?"):
            shutil.rmtree(box_dir)
            ok(f"Ordner gelöscht: {box_dir}")
    else:
        warn("Keine Archivierung")

    if box_dir.exists() and ask("Writeup exportieren?"):
        from .writeup import run as writeup_run

        writeup_run(machine)

    console.print("\n[bold cyan]══════════════════════════════════[/bold cyan]")
    console.print(f"[bold]  {machine} — abgeschlossen[/bold]")
    console.print("[bold cyan]══════════════════════════════════[/bold cyan]\n")
