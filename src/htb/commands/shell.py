import shutil
import subprocess

from .. import notes
from ..api import get_api_key, load_machine_profile
from ..config import HTB_BASE
from ..ui import console, header, ok, warn, die, ask_input


def run(machine: str):
    notes_path = HTB_BASE / machine / "notes.md"
    if not notes_path.exists():
        die(f"notes.md nicht gefunden: {notes_path}")

    header(f"Shell: {machine}")

    n    = notes.parse(notes_path)
    ip   = n.get("ip", "")
    os   = n.get("os", "").lower()

    if not ip:
        profile = load_machine_profile(machine)
        ip = profile.get("ip", "")
    if not ip:
        die("Keine IP gefunden — htb update <machine> <ip>")

    creds = notes.parse_creds(notes_path)

    # Cred auswählen
    if not creds:
        warn("Keine Credentials in notes.md — verbinde ohne Passwort")
        cred = None
    elif len(creds) == 1:
        cred = creds[0]
    else:
        console.print("\n  Gefundene Credentials:")
        for i, c in enumerate(creds):
            console.print(f"    [{i + 1}] [{c['context']}] {c['user']}")
        choice = ask_input(f"Welche? (1-{len(creds)}):")
        try:
            cred = creds[int(choice) - 1]
        except (ValueError, IndexError):
            die("Ungültige Auswahl")

    _connect(ip, os, cred)


def _connect(ip: str, os_name: str, cred: dict | None):
    user     = cred["user"]     if cred else "root"
    password = cred["password"] if cred else None

    if "windows" in os_name:
        _connect_windows(ip, user, password)
    else:
        _connect_linux(ip, user, password)


def _connect_linux(ip: str, user: str, password: str | None):
    ok(f"SSH → {user}@{ip}")
    if password and shutil.which("sshpass"):
        subprocess.run([
            "sshpass", "-p", password,
            "ssh", "-o", "StrictHostKeyChecking=no",
            f"{user}@{ip}",
        ])
    else:
        if password:
            warn(f"sshpass nicht installiert — Passwort: [bold]{password}[/bold]")
            warn("Installieren: sudo pacman -S sshpass")
        subprocess.run(["ssh", "-o", "StrictHostKeyChecking=no", f"{user}@{ip}"])


def _connect_windows(ip: str, user: str, password: str | None):
    ok(f"evil-winrm → {user}@{ip}")
    if not shutil.which("evil-winrm"):
        die("evil-winrm nicht gefunden\nInstallieren: gem install evil-winrm")
    cmd = ["evil-winrm", "-i", ip, "-u", user]
    if password:
        cmd += ["-p", password]
    subprocess.run(cmd)
